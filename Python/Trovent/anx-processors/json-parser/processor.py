import sys
import os
import anxprocessor
import json


class JSONParserProcessor(anxprocessor.KafkaProducerMixin,
                          anxprocessor.KafkaConsumerMixin,
                          anxprocessor.BaseProcessor):

    def __init__(self, logger, isVerbose=False):
        super().__init__(logger, isVerbose)
        self.delete_after_parsing = None
        self.error_field = None
        self.target = None
        self.source = None

    def prepareConfigSchema(self):
        self.config.builder.addOption("json.source", "string", description="Name of the field to parse.")
        self.config.builder.addOption("json.target", "string", description="Name of the field to store parsed values.")
        self.config.builder.addOption("json.error_field", "string", description="Name of the field to store errors.", required=False)
        self.config.builder.addOption("json.deleteAfterParsing", "boolean", description="Remove field named in json.source after parsing.", default=False)
        super().prepareConfigSchema()

    def prepare(self):
        self.source = self.config.getOption("json.source")
        self.target = self.config.getOption("json.target")
        self.error_field = self.config.getOption("json.error_field")
        self.delete_after_parsing = self.config.getOption("json.deleteAfterParsing")
        super().prepare()

    def _set_error(self, data, error_message):
        if not self.error_field:
            return

        error_field_parts = self.error_field.split('.')
        target = data
        for part in error_field_parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        target[error_field_parts[-1]] = error_message


    def _set_target(self, data, parsed_json):
        target_parts = self.target.split('.')
        target = data
        for part in target_parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        target[target_parts[-1]] = parsed_json

    def _delete_source(self, data):
        source_parts = self.source.split('.')
        target = data
        for part in source_parts[:-1]:
            if part not in target:
                return
            target = target[part]
        del target[source_parts[-1]]


    def onDataProcess(self, message):
        data = None
        try:
            data = json.loads(message)
            if not data:
                raise RuntimeError(f"Source field '{self.source}' not found")

            source_value = data
            source_parts = self.source.split('.')
            for part in source_parts:
                if isinstance(source_value, dict) and part in source_value:
                    source_value = source_value[part]
                else:
                    raise RuntimeError(f"Source field '{self.source}' not found")

            if not isinstance(source_value, str):
                raise RuntimeError(f"Source field '{self.source}' is not a string")
            
            try:
                parsed_json = json.loads(source_value)
                self._set_target(data, parsed_json)
                if self.delete_after_parsing:
                    self._delete_source(data)
            except json.JSONDecodeError as e:
                error_msg = f"JSON decode error: {e}"
                self._set_error(data, error_msg)
                self.logger.error(error_msg)                    
                    
            return json.dumps(data)

        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error: {e}"
            self.logger.error(error_msg)
            if data:
                return data
        except RuntimeError as e:
            error_msg = str(e)
            self._set_error(data if data else {}, error_msg)
            self.logger.error(error_msg)
            if data:
                return data
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            self._set_error(data if data else {}, error_msg)
            self.logger.error(error_msg)
            if data:
                return data
