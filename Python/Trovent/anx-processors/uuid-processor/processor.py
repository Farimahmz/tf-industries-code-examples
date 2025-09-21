import sys
import os
import anxprocessor
import json
import uuid


class UUIDProcessor(anxprocessor.KafkaProducerMixin,
                    anxprocessor.KafkaConsumerMixin,
                    anxprocessor.BaseProcessor):

    def __init__(self, logger, isVerbose=False):
        super().__init__(logger, isVerbose)
        self.target = None
        self.overwrite = False

    def prepareConfigSchema(self):
        self.config.builder.addOption("uuid.target", "string", description="Name of the field to store the UUID.", default="uuid")
        self.config.builder.addOption("uuid.overwrite", "boolean", description="Overwrite existing UUID if true.", required=False, default=False)
        super().prepareConfigSchema()

    def prepare(self):
        self.target = self.config.getOption("uuid.target")
        self.overwrite = self.config.getOption("uuid.overwrite", default=False)
        super().prepare()

    def _set_uuid(self, data):
        target_parts = self.target.split('.')
        target = data
        for part in target_parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]

        if not self.overwrite and target.get(target_parts[-1]):
            self.logger.debug(f"UUID already exists for target '{self.target}', skipping overwrite.")
            return

        target[target_parts[-1]] = str(uuid.uuid4())
        self.logger.debug(f"UUID set for target '{self.target}': {target[target_parts[-1]]}")


    def onDataProcess(self, message):
        try:
            data = None
            data = json.loads(message)            
            self._set_uuid(data)
            return json.dumps(data)
        
        except json.JSONDecodeError as e:
            error_msg = f"Failed to decode record value JSON: {e}"
            self.logger.error(error_msg)
            if data:
                return data

        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            self.logger.error(error_msg)
            if data:
                return data
