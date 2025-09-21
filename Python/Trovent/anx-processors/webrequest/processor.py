"""Processor to make web requests"""

import json
import ssl

import anxprocessor
import certifi
import requests
import urllib3
from requests.adapters import HTTPAdapter
from requests.exceptions import SSLError


# pylint: disable=too-many-instance-attributes
class WebRequestProcessor(
    anxprocessor.KafkaProducerMixin,
    anxprocessor.KafkaConsumerMixin,
    anxprocessor.BaseProcessor,
):
    """Processor class using base processor and Kafka modules"""

    def __init__(self, logger, isVerbose=False):
        super().__init__(logger, isVerbose)
        self.url = None
        self.method = "GET"
        self.headers = {}
        self.body_plain = None
        self.body_json = None
        self.target = "response"
        self.ca_certificate = None
        self.ssl_context = None
        self.timeout = None
        self.skip_cert_check = False
        self.include_request = False
        self.include_request_data = {}

    def prepareConfigSchema(self):
        """Defines the configuration schema for the processor."""
        super().prepareConfigSchema()
        config = self.config.builder
        config.addOption(
            "webrequest.url",
            "string",
            description="URL to request. Supports variable substitution.",
            required=True,
        )
        config.addOption(
            "webrequest.method",
            "string",
            default="GET",
            description="HTTP method (GET, POST, PUT, DELETE).",
            required=False,
            enum = ["GET", "POST", "PUT", "DELETE"]
        )
        config.addOption(
            "webrequest.headers",
            "object",
            description="Headers for the request.",
            required=False,
        )
        config.addOption(
            "webrequest.body.plain",
            "string",
            description="Plain body to be sent with the request.",
            required=False,
        )
        config.addOption(
            "webrequest.body.json",
            "object",
            description="JSON body to be sent with the request.",
            required=False,
        )
        config.addOption(
            "webrequest.target",
            "string",
            default="response",
            description="Key to store the response. 1st level only.",
            required=False,
        )
        config.addOption(
            "webrequest.ca_certificate",
            "string",
            description="CA certificate in PEM format.",
            required=False,
        )
        config.addOption(
            "webrequest.timeout",
            "number",
            description="Timeout for the web request in seconds.",
            required=False,
        )
        config.addOption(
            "webrequest.skip_cert_check",
            "boolean",
            default=False,
            description="Skip SSL certificate check if True.",
            required=False,
        )

        config.addOption(
            "webrequest.include_request",
            "boolean",
            default=False,
            description="Includes the request parameters into the outgoing message"
        )

    def prepare(self):
        """Prepares the processor by loading configuration values."""
        self.url = self.config.getOption("webrequest.url")
        self.method = self.config.getOption("webrequest.method", "GET").upper()
        self.headers = self.config.getOption("webrequest.headers", {})
        self.body_plain = self.config.getOption("webrequest.body.plain")
        self.body_json = self.config.getOption("webrequest.body.json")
        self.target = self.config.getOption("webrequest.target", "response")
        self.ca_certificate = self.config.getOption("webrequest.ca_certificate")
        self.timeout = self.config.getOption("webrequest.timeout")
        self.skip_cert_check = self.config.getOption(
            "webrequest.skip_cert_check", False
        )
        if self.body_plain and self.body_json:
            raise ValueError(
                "Both 'body.plain' and 'body.json' cannot be set simultaneously."
            )
        if self.ca_certificate:
            self.ssl_context = ssl.create_default_context(cafile=certifi.where())
            try:
                self.ssl_context.load_verify_locations(cadata=self.ca_certificate)
            except (ssl.SSLError, ValueError) as e:
                raise ValueError("CA cannot be loaded") from e
        if self.skip_cert_check:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.include_request = self.config.getOption("webrequest.include_request")
        super().prepare()

    def _make_request(self, url_to_call):
        """Handles the HTTP request based on the configured parameters."""

        request_kwargs = {
            "headers": self.headers,
            "timeout": self.timeout,
        }
        with requests.Session() as session:
            http_adapter = HTTPAdapter()
            session.mount("http://", http_adapter)
            if self.skip_cert_check:
                https_adapter = NoSSLVerificationAdapter()
                request_kwargs['verify'] = False
                session.mount("https://", https_adapter)
            else:
                if self.ssl_context:
                    https_adapter = SSLContextAdapter(ssl_context=self.ssl_context)
                    session.mount("https://", https_adapter)
            body = json.dumps(self.body_json) if self.body_json else self.body_plain

            #******     Start creating optional request for message inclusion   ****
            if self.include_request:
                req = requests.Request(
                    method=self.method,
                    url=url_to_call,
                    data=body,
                    headers=self.headers
                )

                prepped = session.prepare_request(req)

                self.include_request_data ={
                    "method:" : f"{prepped.method}",
                    "url:" : f"{prepped.url}",
                    "headers:" : f"{prepped.headers}",
                    "body:" : f"{prepped.body}"
                }
            # ******     End creating optional request for message inclusion   ****

            try:
                if self.method == "GET":
                    response = session.get(url_to_call, **request_kwargs)
                elif self.method == "POST":
                    response = session.post(url_to_call, data=body, **request_kwargs)
                elif self.method == "PUT":
                    response = session.put(url_to_call, data=body, **request_kwargs)
                elif self.method == "DELETE":
                    response = session.delete(url_to_call, **request_kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {self.method}")

                return {
                    "status_code": response.status_code,
                    "reason": response.reason,
                    "text": response.text,
                    "headers": dict(response.headers),
                }
            except requests.Timeout as e:
                self.logger.error(f"Timeout during request to {url_to_call}: {str(e)}")
                return {
                    "status_code": 0,
                    "reason": "Timeout",
                    "text": f"Timeout: {str(e)}",
                    "headers": {},
                }
            except SSLError as e:
                self.logger.error(
                    f"SSL error during request to {url_to_call}: {str(e)}"
                )
                return {
                    "status_code": 0,
                    "reason": "SSL Verification Error",
                    "text": f"SSL verification failed: {str(e)}",
                    "headers": {},
                }
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.logger.error(
                    f"Error during web request to {url_to_call}: {str(e)}"
                )
                return {
                    "status_code": 0,
                    "reason": "Request Error",
                    "text": str(e),
                    "headers": {},
                }

    def onDataProcess(self, message):
        try:
            if isinstance(message, str):
                message_dict = json.loads(message)
            elif hasattr(message, "value"):
                message_dict = json.loads(message.value)
            else:
                raise TypeError(
                    "Unexpected type for 'message'. Must be str or have 'value' attribute."
                )

            if "{" in self.url and "}" in self.url:
                url_to_call = self.url.format(**message_dict)
            else:
                url_to_call = self.url
            if self.body_plain and isinstance(self.body_plain, str):
                self.body_plain = self.body_plain.format(**message_dict)

            response = self._make_request(url_to_call)

            try:
                response_body = json.loads(response["text"])
            except json.JSONDecodeError:
                response_body = response["text"]

            result = {
                self.target: {
                    "status": {
                        "code": response["status_code"],
                        "message": response["reason"],
                    },
                    "body": response_body,
                    "headers": response["headers"],
                }
            }
            message_dict.update(result)

            if self.include_request:
                message_dict["request"] = self.include_request_data

            return json.dumps(message_dict)
        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({self.target: {"error": error_msg}})
        except TypeError as e:
            error_msg = f"Type error: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({self.target: {"error": error_msg}})
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Error during web request: {e}")
            return json.dumps({self.target: {"error": str(e)}})


class SSLContextAdapter(HTTPAdapter):
    """Create a custom transport adapter using the SSL context for HTTPS"""

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

class NoSSLVerificationAdapter(HTTPAdapter):
    """Create a custom transport adapter without SSL verification"""
    def init_poolmanager(self, *args, **kwargs):
        kwargs['assert_hostname'] = False
        kwargs['cert_reqs'] = 'CERT_NONE'
        return super().init_poolmanager(*args, **kwargs)
