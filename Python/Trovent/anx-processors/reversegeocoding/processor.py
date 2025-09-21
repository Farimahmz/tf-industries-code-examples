# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring

import requests
import json
import anxprocessor


class ReverseGeocodingProcessor(anxprocessor.KafkaProducerMixin,
                                anxprocessor.KafkaConsumerMixin,
                                anxprocessor.BaseProcessor):

    def __init__(self, logger, isVerbose=False):
        super().__init__(logger, isVerbose)
        self.lookupMode = ""
        self.inputField = []
        self.OutputField = []
        self.lookupUrl = ""
        self.userAgent = ""
        self.outputField = "ReverseGeoCoding"

    def lookup_no(self, input_data):
        if not self.inputField or len(self.inputField) < 2:
            self.logger.error("inputField config is invalid or incomplete. Expected 2 fields (e.g., 'Latitude,Longitude').")
            return input_data

        latitude = self.getValue(input_data, self.inputField[0])
        longitude = self.getValue(input_data, self.inputField[1])

        if latitude and longitude:
            url = f"{self.lookupUrl}?lat={latitude}&lon={longitude}&format=json"
            headers = {'User-Agent': self.userAgent}

            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = json.loads(response.content)
                    if isinstance(data, dict):
                        address = data.get('address', {})

                        input_data[self.outputField] = {
                            "input": {
                                "Latitude": latitude,
                                "Longitude": longitude
                            },
                            "output": address
                        }
                    else:
                        self.logger.warning("Invalid data format from response.")
                else:
                    self.logger.warning(f"Lookup failed with status code {response.status_code}")

            except Exception as error:
                self.logger.error(f"Lookup failed: {error}")

        return input_data

    def prepareConfigSchema(self):
        self.config.builder.addOption(
            "geo.input.field",
            "string",
            "Comma-separated fields for latitude and longitude",
            required=True,
        )
        self.config.builder.addOption(
            "geo.lookup.mode",
            "string",
            "Lookup mode: 'reverse' for reverse geocoding",
            required=True,
        )
        self.config.builder.addOption(
            "geo.lookup.url",
            "string",
            "URL for the reverse geocoding service (e.g., OpenStreetMap Nominatim)",
            required=True,
        )
        self.config.builder.addOption(
            "geo.lookup.user_agent",
            "string",
            "User-Agent header for the reverse geocoding request",
            required=True,
        )
        self.config.builder.addOption(
            "geo.output",
            "string",
            "Field to write reverse geocoding result into",
            required=False,
            default="ReverseGeoCoding"
        )
        super().prepareConfigSchema()

    def prepare(self):
        self.lookupMode = self.config.getOption("geo.lookup.mode") or "reverse"
        self.inputField = self.config.getOption("geo.input.field").split(",")
        self.lookupUrl = self.config.getOption("geo.lookup.url")
        self.userAgent = self.config.getOption("geo.lookup.user_agent")
        self.outputField = self.config.getOption("geo.output")
        super().prepare()

    def onDataProcess(self, message):
        try:
            v = json.loads(message)
            if self.lookupMode == "reverse":
                enriched = self.lookup_no(v)
            else:
                enriched = v

            self.logger.info(enriched)
            return json.dumps(enriched)

        except Exception as e:
            self.logger.error(f"[Error] Failed in onDataProcess: {e}")
            return None
