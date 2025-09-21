"""Test webrequest processor"""

import json
import logging
import ssl
import time
import unittest

import certifi
import trustme
import urllib3
from pytest_httpserver import HTTPServer

from processor import WebRequestProcessor


def sleeping(request):  # pylint: disable=unused-argument
    """Helper function to simulate a request timeout"""
    time.sleep(2)


class TestWebRequestProcessorWithHTTP(unittest.TestCase):
    """Testing HTTP requests"""

    def setUp(self):
        self.processor = WebRequestProcessor(logging.getLogger())

        # Initialize HTTP server
        self.httpserver = HTTPServer()
        self.httpserver.start()

    def tearDown(self):
        self.httpserver.clear()
        self.httpserver.stop()

    def test_http_request(self):
        """Test successful HTTP request"""

        self.httpserver.expect_request("/data").respond_with_json(
            {"message": "success"},
        )

        self.processor.url = self.httpserver.url_for("/data")

        result = self.processor.onDataProcess('{"meta": {"source": "test"}}')

        result_dict = json.loads(result)

        del result_dict["response"]["headers"]
        self.assertEqual(
            result_dict,
            {
                "meta": {"source": "test"},
                "response": {
                    "status": {
                        "code": 200,
                        "message": "OK",
                    },
                    "body": {
                        "message": "success",
                    },
                },
            },
        )

    def test_http_post_request(self):
        """Test successful HTTP request"""

        self.httpserver.expect_request("/data", method="POST").respond_with_json(
            {"message": "success"},
        )

        self.processor.url = self.httpserver.url_for("/data")
        self.processor.method = "POST"

        result = self.processor.onDataProcess('{"meta": {"source": "test"}}')

        result_dict = json.loads(result)

        del result_dict["response"]["headers"]
        self.assertEqual(
            result_dict,
            {
                "meta": {"source": "test"},
                "response": {
                    "status": {
                        "code": 200,
                        "message": "OK",
                    },
                    "body": {
                        "message": "success",
                    },
                },
            },
        )

    def test_http_put_request(self):
        """Test successful HTTP request"""

        self.httpserver.expect_request("/data", method="PUT").respond_with_json(
            {"message": "success"},
        )

        self.processor.url = self.httpserver.url_for("/data")
        self.processor.method = "PUT"

        result = self.processor.onDataProcess('{"meta": {"source": "test"}}')

        result_dict = json.loads(result)

        del result_dict["response"]["headers"]
        self.assertEqual(
            result_dict,
            {
                "meta": {"source": "test"},
                "response": {
                    "status": {
                        "code": 200,
                        "message": "OK",
                    },
                    "body": {
                        "message": "success",
                    },
                },
            },
        )

    def test_http_request_with_invalid_method(self):
        """Test successful HTTP request"""

        self.httpserver.expect_request("/data", method="HEAD").respond_with_json(
            {"message": "success"},
        )

        self.processor.url = self.httpserver.url_for("/data")
        self.processor.method = "HEAD"

        result = self.processor.onDataProcess('{"meta": {"source": "test"}}')

        result_dict = json.loads(result)

        del result_dict["response"]["headers"]
        self.assertEqual(
            result_dict,
            {
                "meta": {"source": "test"},
                "response": {
                    "status": {
                        "code": 0,
                        "message": "Request Error",
                    },
                    "body": "Unsupported HTTP method: HEAD",
                },
            },
        )

    def test_http_delete_request(self):
        """Test successful HTTP request"""

        self.httpserver.expect_request("/data", method="DELETE").respond_with_json(
            {"message": "success"},
        )

        self.processor.url = self.httpserver.url_for("/data")
        self.processor.method = "DELETE"

        result = self.processor.onDataProcess('{"meta": {"source": "test"}}')

        result_dict = json.loads(result)

        del result_dict["response"]["headers"]
        self.assertEqual(
            result_dict,
            {
                "meta": {"source": "test"},
                "response": {
                    "status": {
                        "code": 200,
                        "message": "OK",
                    },
                    "body": {
                        "message": "success",
                    },
                },
            },
        )

    def test_different_target(self):
        """Test successful HTTP request with different target"""

        self.httpserver.expect_request("/data").respond_with_json(
            {"message": "success"},
        )

        self.processor.url = self.httpserver.url_for("/data")
        self.processor.target = "resp2"

        result = self.processor.onDataProcess('{"meta": {"source": "test"}}')

        result_dict = json.loads(result)

        del result_dict["resp2"]["headers"]
        self.assertEqual(
            result_dict,
            {
                "meta": {"source": "test"},
                "resp2": {
                    "status": {
                        "code": 200,
                        "message": "OK",
                    },
                    "body": {
                        "message": "success",
                    },
                },
            },
        )

    def test_http_request_with_timeout(self):
        """Test successful HTTP request"""

        self.httpserver.expect_request("/data").respond_with_handler(sleeping)

        self.processor.url = self.httpserver.url_for("/data")
        self.processor.timeout = 1

        result = self.processor.onDataProcess('{"meta": {"source": "test"}}')

        result_dict = json.loads(result)

        self.assertIn(
            "Timeout: HTTPConnectionPool",
            result_dict["response"]["body"],
            "Timeout message missing",
        )
        # Remove parts with too many individual details
        del result_dict["response"]["headers"]
        del result_dict["response"]["body"]
        self.assertEqual(
            result_dict,
            {
                "meta": {"source": "test"},
                "response": {
                    "status": {
                        "code": 0,
                        "message": "Timeout",
                    },
                },
            },
        )


class TestWebRequestProcessorWithHTTPS(unittest.TestCase):
    """Testing HTTPS requests"""

    def setUp(self):
        self.processor = WebRequestProcessor(logging.getLogger())

        # Set up CA
        self.ca = trustme.CA()
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ca_pem = self.ca.cert_pem.bytes().decode('utf-8')

        # Get webserver certificate
        self.localhost_server_cert = self.ca.issue_cert("localhost")
        self.localhost_server_cert.configure_cert(self.context)

        # Initialize HTTPS server
        self.httpserver = HTTPServer(ssl_context=self.context)
        self.httpserver.start()

    def tearDown(self):
        self.httpserver.clear()
        self.httpserver.stop()

    def test_https_with_correct_certificate(self):
        """Test successful SSL request"""

        self.httpserver.expect_request("/data").respond_with_json(
            {"response": {"status": {"code": 200}, "message": "success"}},
        )

        self.processor.ca_certificate = self.ca_pem
        # normally happens in prepare()
        self.processor.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.processor.ssl_context.load_verify_locations(cadata=self.ca_pem)
        ###
        self.processor.skip_cert_check = False
        self.processor.url = self.httpserver.url_for("/data")

        result = self.processor.onDataProcess(
            '{"meta": {"source": "test_ca_certificate"}}'
        )

        result_dict = json.loads(result)

        self.assertEqual(result_dict["response"]["status"]["code"], 200)
        self.assertEqual(
            result_dict["response"]["body"]["response"],
            {"status": {"code": 200}, "message": "success"},
        )

    def test_https_with_correct_certificate_but_skip_test(self):
        """Test successful SSL request"""

        self.httpserver.expect_request("/data").respond_with_json(
            {"response": {"status": {"code": 200}, "message": "success"}},
        )

        self.processor.ca_certificate = self.ca_pem
        self.processor.skip_cert_check = True
        self.processor.url = self.httpserver.url_for("/data")
        # normally happens in prepare()
        self.processor.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.processor.ssl_context.load_verify_locations(cadata=self.ca_pem)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        ###

        result = self.processor.onDataProcess(
            '{"meta": {"source": "test_ca_certificate"}}'
        )

        result_dict = json.loads(result)

        self.assertEqual(result_dict["response"]["status"]["code"], 200)
        self.assertEqual(
            result_dict["response"]["body"]["response"],
            {"status": {"code": 200}, "message": "success"},
        )

    def test_https_with_missing_ca(self):
        """Simulate an SSL verification error"""

        self.httpserver.expect_request("/data").respond_with_json(
            {"response": {"status": {"code": 200}, "message": "success"}},
        )

        self.processor.skip_cert_check = False
        self.processor.ca_certificate = None
        self.processor.ssl_context = None
        self.processor.url = self.httpserver.url_for("/data")

        result = self.processor.onDataProcess(
            '{"meta": {"source": "test_ca_certificate"}}'
        )
        result_dict = json.loads(result)

        self.assertEqual(result_dict["response"]["status"]["code"], 0)
        self.assertEqual(
            result_dict["response"]["status"]["message"], "SSL Verification Error"
        )
        self.assertIn("SSL verification failed", result_dict["response"]["body"])
        self.assertIn("Caused by SSLError", result_dict["response"]["body"])
        self.assertEqual(result_dict["response"]["headers"], {})

    def test_https_with_missing_ca_but_skip_test(self):
        """Test successful SSL request"""

        self.httpserver.expect_request("/data").respond_with_json(
            {"response": {"status": {"code": 200}, "message": "success"}},
        )

        self.processor.ca_certificate = None
        self.processor.ssl_context = None
        self.processor.skip_cert_check = True
        self.processor.url = self.httpserver.url_for("/data")
        # normally happens in prepare()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        result = self.processor.onDataProcess(
            '{"meta": {"source": "test_ca_certificate"}}'
        )

        result_dict = json.loads(result)

        self.assertEqual(result_dict["response"]["status"]["code"], 200)
        self.assertEqual(
            result_dict["response"]["body"]["response"],
            {"status": {"code": 200}, "message": "success"},
        )


class TestWebRequestProcessorWithHTTPSForOtherHost(unittest.TestCase):
    """Testing HTTPS requests"""

    def setUp(self):
        self.processor = WebRequestProcessor(logging.getLogger())

        # Set up CA
        self.ca = trustme.CA()
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ca_pem = self.ca.cert_pem.bytes().decode('utf-8')

        # Get webserver certificate
        self.localhost_server_cert = self.ca.issue_cert("wronghost")
        self.localhost_server_cert.configure_cert(self.context)

        # Initialize HTTPS server
        self.httpserver = HTTPServer(ssl_context=self.context)
        self.httpserver.start()

    def tearDown(self):
        self.httpserver.clear()
        self.httpserver.stop()

    def test_https_hostname_mismatch_but_skip_test(self):
        """Test successful SSL request"""

        self.httpserver.expect_request("/data").respond_with_json(
            {"response": {"status": {"code": 200}, "message": "success"}},
        )

        self.processor.ca_certificate = self.ca_pem
        self.processor.skip_cert_check = True
        self.processor.url = self.httpserver.url_for("/data")
        # normally happens in prepare()
        self.processor.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.processor.ssl_context.load_verify_locations(cadata=self.ca_pem)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        ###

        result = self.processor.onDataProcess(
            '{"meta": {"source": "test_ca_certificate"}}'
        )

        result_dict = json.loads(result)

        self.assertEqual(result_dict["response"]["status"]["code"], 200)
        self.assertEqual(
            result_dict["response"]["body"]["response"],
            {"status": {"code": 200}, "message": "success"},
        )

    def test_https_hostname_mismatch(self):
        """Simulate an SSL verification error"""

        self.httpserver.expect_request("/data").respond_with_json(
            {"response": {"status": {"code": 200}, "message": "success"}},
        )

        self.processor.ca_certificate = self.ca_pem
        # normally happens in prepare()
        self.processor.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.processor.ssl_context.load_verify_locations(cadata=self.ca_pem)
        ###
        self.processor.skip_cert_check = False
        self.processor.url = self.httpserver.url_for("/data")

        result = self.processor.onDataProcess(
            '{"meta": {"source": "test_ca_certificate"}}'
        )
        result_dict = json.loads(result)

        self.assertEqual(result_dict["response"]["status"]["code"], 0)
        self.assertEqual(
            result_dict["response"]["status"]["message"], "SSL Verification Error"
        )
        self.assertIn("SSL verification failed", result_dict["response"]["body"])
        self.assertIn("Caused by SSLError", result_dict["response"]["body"])
        self.assertEqual(result_dict["response"]["headers"], {})

class TestWebRequestProcessorOptionalFlag(unittest.TestCase):
    """Testing HTTP requests"""

    def setUp(self):
        self.processor = WebRequestProcessor(logging.getLogger())

        # Initialize HTTP server
        self.httpserver = HTTPServer()
        self.httpserver.start()

    def tearDown(self):
        self.httpserver.clear()
        self.httpserver.stop()

    def test_including_request(self):
        self.httpserver.expect_request("/data").respond_with_json(
            {"message": "success"},
        )

        self.processor.url = self.httpserver.url_for("/data")
        self.processor.include_request = True
        result = self.processor.onDataProcess('{"meta": {"source": "test"}}')

        result_dict = json.loads(result)

        self.assertIn("request", result_dict)

    def test_not_including_request(self):
        self.httpserver.expect_request("/data").respond_with_json(
            {"message": "success"},
        )

        self.processor.url = self.httpserver.url_for("/data")
        self.processor.include_request = False
        result = self.processor.onDataProcess('{"meta": {"source": "test"}}')

        result_dict = json.loads(result)

        self.assertNotIn("request", result_dict)