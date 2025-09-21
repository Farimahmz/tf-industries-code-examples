import sys
import os
import anxprocessor
import json
import re


class ComposeProcessor(anxprocessor.KafkaProducerMixin,
                       anxprocessor.KafkaConsumerMixin,
                       anxprocessor.BaseProcessor):

    def __init__(self, logger, isVerbose=False):
        super().__init__(logger, isVerbose)
        self.source = None
        self.target = None

    def prepareConfigSchema(self):
        self.config.builder.addOption("compose.source", "string", description="Template string with variables.")
        self.config.builder.addOption("compose.target", "string", description="Name of the field to store the composed message.")
        super().prepareConfigSchema()

    def prepare(self):
        self.source = self.config.getOption("compose.source")
        self.target = self.config.getOption("compose.target")
        super().prepare()

    def get_value_from_path(self, data, path):
        keys = path.split('.')
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        return data

    def replace_variable(self, match, data):
        variable_path = match.group(1).strip()
        value = self.get_value_from_path(data, variable_path)
        return str(value) if value is not None else match.group(0)

    def onDataProcess(self, record):
        data = None
        try:
            data = json.loads(record)
            if not data:
                raise RuntimeError("Incoming data is empty or invalid JSON.")

            result_message = re.sub(r'{([^{}]+)}', lambda match: self.replace_variable(match, data), self.source)

            target_parts = self.target.split('.')
            target = data
            for part in target_parts[:-1]:
                if part not in target:
                    target[part] = {}
                target = target[part]
            target[target_parts[-1]] = result_message

            return json.dumps(data)

        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error: {e}"
            self.logger.error(error_msg)
            # Return an empty JSON object if data is None, otherwise return the current state of data
            return json.dumps(data if data else {})

        except RuntimeError as e:
            error_msg = str(e)
            self.logger.error(error_msg)
            return json.dumps(data if data else {})

        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            self.logger.error(error_msg)
            return json.dumps(data if data else {})
