import json
import phonenumbers
from phonenumbers import carrier
import anxprocessor
from phonenumbers.phonenumberutil import region_code_for_number
import pycountry


class MSISDNLookupProcessor(anxprocessor.KafkaProducerMixin,
                            anxprocessor.KafkaConsumerMixin,
                            anxprocessor.BaseProcessor):

    def __init__(self, logger, isVerbose=False):
        super().__init__(logger, isVerbose)
        self.inputField = []
        self.outputField = "MSISDNLookup"

    def lookup_country(self, input_data):
        msisdn = self.getValue(input_data, self.inputField)
        if msisdn:
            try:
                parsed_number = phonenumbers.parse(msisdn)
                region_code = region_code_for_number(parsed_number)
                try:
                    country = pycountry.countries.get(alpha_2=region_code).name
                except AttributeError:
                    country = "Unknown"

                operator = carrier.name_for_number(parsed_number, "en") or "Unknown"

                input_data[self.outputField] = {
                    "input": msisdn,
                    "output": {
                        "country": country,
                        "operator": operator
                    }
                }
            except Exception as error:
                self.logger.error(f"Failed to parse MSISDN {msisdn}: {error}")
        return input_data

    def prepareConfigSchema(self):
        self.config.builder.addOption(
            "msisdn.input.field",
            "string",
            "JSON field key containing the MSISDN",
            required=True,
        )
        self.config.builder.addOption(
            "msisdn.output.field",
            "string",
            "JSON field key where to store the MSISDN lookup result",
            required=False,
            default="MSISDNLookup"
        )
        super().prepareConfigSchema()

    def prepare(self):
        self.inputField = self.config.getOption("msisdn.input.field")
        self.outputField = self.config.getOption("msisdn.output.field")
        super().prepare()

    def onDataProcess(self, message):
        try:
            record = json.loads(message)
            processed_record = self.lookup_country(record)

            if processed_record:
                result = json.dumps(processed_record)
                return result
            else:
                self.logger.error("Processing failed. Skipping record.")
                return None

        except BaseException as error:
            self.logger.error(f"Processing failed: {error}")
