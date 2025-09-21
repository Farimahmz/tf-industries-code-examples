import sys
import os
import anxprocessor
import json


class LookupProcessor(anxprocessor.KafkaProducerMixin,
                      anxprocessor.KafkaConsumerMixin,
                      anxprocessor.BaseProcessor):

    def __init__(self, logger, isVerbose=False):
        super().__init__(logger, isVerbose)
        self.lookup_key = ""
        self.lookup_destination = ""
        self.lookup_dict = {}

    def prepareConfigSchema(self):
        self.config.builder.addOption(
            "lookup.key",
            "string",
            description="Path to the key in the input data to look up",
            required=True
        )

        self.config.builder.addOption(
            "lookup.destination",
            "string",
            description="Path to the destination in the data where the result will be set",
            required=True
        )

        self.config.builder.addOption(
            "lookup.dictionary",
            "object",
            description="Key-value pairs for lookup (postal code -> city)",
            required=True
        )

        super().prepareConfigSchema()

    def prepare(self):
        self.lookup_key = self.config.getOption("lookup.key", "")
        self.lookup_destination = self.config.getOption("lookup.destination", "")
        self.lookup_dict = self.config.getOption("lookup.dictionary", {})

        super().prepare()

    def lookup(self, data):
        if not self.lookup_key or not self.lookup_destination or not self.lookup_dict:
            self.logger.error("Invalid configuration: missing key, destination, or dictionary.")
            return data

        key_path = self.lookup_key.split(".")
        postal_code = self._get_nested_value(data, key_path)

        if postal_code:
            city = self.lookup_dict.get(str(postal_code))
            if city:
                destination_path = self.lookup_destination.split(".")
                self._set_nested_value(data, destination_path, city)

        return data

    def _get_nested_value(self, data, key_path):
        """ Helper function to get a value from a nested dictionary. """
        for key in key_path:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        return data

    def _set_nested_value(self, data, key_path, value):
        """ Helper function to set a value in a nested dictionary. """
        for key in key_path[:-1]:
            data = data.setdefault(key, {})
        data[key_path[-1]] = value

    def onDataProcess(self, message):
        try:
            if isinstance(message, str):
                data = json.loads(message)
            elif hasattr(message, 'value'):
                data = json.loads(message.value)
            else:
                raise TypeError("Unexpected type for 'message'. Must be str or have 'value' attribute.")

            updated_data = self.lookup(data)
            return json.dumps(updated_data)

        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({"error": error_msg})
