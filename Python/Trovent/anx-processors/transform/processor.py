# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json

import anxprocessor


def navigateToKey(data, key, create_missing=True):
    keys = key.split('.')
    for k in keys[:-1]:
        if k not in data:
            if create_missing:
                data[k] = {}
            else:
                return None, keys[-1]
        data = data[k]
    return data, keys[-1]


class TransformProcessor(
    anxprocessor.KafkaProducerMixin,
    anxprocessor.KafkaConsumerMixin,
    anxprocessor.BaseProcessor,
):

    def __init__(self, logger, isVerbose=False):
        super().__init__(logger, isVerbose)
        self.filePath = None

    def prepareConfigSchema(self):
        self.config.builder.addOption(
            "transform.commands", "array", description="List of transformations."
        )
        super().prepareConfigSchema()

    def add(self, data, key, value, overwrite=False):
        try:
            if not isinstance(key, str):
                raise TypeError(f"Invalid key type: {key}. Key must be a string.")
            target, last_key = navigateToKey(data, key, create_missing=True)
            if last_key in target and not overwrite:
                self.logger.debug(f"Key {key} already exists and overwrite is set to False. Skipping add.")
            else:
                target[last_key] = value
        except TypeError as e:
            self.logger.error(e)
            raise
        except Exception as e:
            self.logger.error(f"An error occurred while adding the key-value pair: {e}")
            raise

    def delete(self, data, key=None, keys=None):
        if key is None and keys is None:
            self.logger.error("Either 'key' or 'keys' must be provided.")
            return

        try:
            if key:
                if not isinstance(key, str):
                    raise TypeError("Key must be a string.")
                target, last_key = navigateToKey(data, key, create_missing=False)
                if last_key in target:
                    del target[last_key]
                else:
                    self.logger.debug(f"Key {key} not found.")
            if keys:
                for k in keys:
                    if not isinstance(k, str):
                        raise TypeError(f"Invalid key type in keys list: {type(k).__name__}. All keys must be strings.")
                    target, last_key = navigateToKey(data, k, create_missing=False)
                    if last_key in target:
                        del target[last_key]
                    else:
                        self.logger.debug(f"Key {k} not found.")

        except TypeError as e:
            self.logger.error(f"Invalid key type: {e}")
            raise
        except Exception as e:
            self.logger.error(f"An error occurred while deleting key(s): {e}")
            raise

    def move(self, data, old_key, new_key):
        try:
            if not isinstance(old_key, str) or not isinstance(new_key, str):
                raise TypeError(
                    f"Invalid key type: {old_key} or {new_key}. Keys must be strings."
                )

            target, last_key = navigateToKey(data, old_key, create_missing=False)
            if target is not None and last_key in target:
                target[new_key] = target.pop(last_key)
            else:
                self.logger.debug(f"Key {old_key} not found.")
        except TypeError as e:
            self.logger.error(e)
            raise
        except Exception as e:
            self.logger.error(f"An error occurred while renaming the key: {e}")
            raise

    def copy(self, data, src_key, dest_key, overwrite=False):
        try:
            if not isinstance(src_key, str) or not isinstance(dest_key, str):
                raise TypeError(f"Invalid key type: {src_key} or {dest_key}. Keys must be strings.")

            src_target, src_last_key = navigateToKey(data, src_key, create_missing=False)
            if src_target is not None and src_last_key in src_target:
                value_to_copy = src_target[src_last_key]
                dest_target, dest_last_key = navigateToKey(data, dest_key, create_missing=True)
                if dest_last_key in dest_target and not overwrite:
                    self.logger.warning(f"Destination key {dest_key} already exists and overwrite is set to False. Skipping copy.")
                else:
                    dest_target[dest_last_key] = value_to_copy
            else:
                self.logger.debug(f"Source key {src_key} not found.")
        except TypeError as e:
            self.logger.error(e)
            raise
        except Exception as e:
            self.logger.error(f"An error occurred while copying value: {e}")
            raise


    def uppercase(self, data, key=None, keys=None):
        if key is None and keys is None:
            self.logger.error("Either 'key' or 'keys' must be provided.")
            return data

        combined_keys = []
        if key:
            if not isinstance(key, str):
                raise TypeError("Key must be a string.")
            combined_keys.append(key)

        if keys:
            for k in keys:
                if not isinstance(k, str):
                    raise TypeError("All keys must be strings.")
                combined_keys.append(k)

        try:
            for k in combined_keys:
                target, last_key = navigateToKey(data, k, create_missing=False)
                if target is not None and last_key in target:
                    if isinstance(target[last_key], str):
                        target[last_key] = target[last_key].upper()
                    else:
                        self.logger.warning(f"Value of key '{k}' is not a string and cannot be uppercased.")
                else:
                    self.logger.debug(f"Key '{k}' not found.")
        except Exception as e:
            self.logger.error(f"An error occurred while uppercasing key(s): {e}")
            raise

        return data


    def lowercase(self, data, key=None, keys=None):
        if key is None and keys is None:
            self.logger.error("Either 'key' or 'keys' must be provided.")
            return data

        combined_keys = []
        if key:
            if not isinstance(key, str):
                raise TypeError("Key must be a string.")
            combined_keys.append(key)

        if keys:
            for k in keys:
                if not isinstance(k, str):
                    raise TypeError("All keys must be strings.")
                combined_keys.append(k)

        try:
            for k in combined_keys:
                target, last_key = navigateToKey(data, k, create_missing=False)
                if target is not None and last_key in target:
                    if isinstance(target[last_key], str):
                        target[last_key] = target[last_key].lower()
                    else:
                        self.logger.warning(f"Value of key '{k}' is not a string and cannot be lowercased.")
                else:
                    self.logger.debug(f"Key '{k}' not found.")
        except Exception as e:
            self.logger.error(f"An error occurred while lowercasing key(s): {e}")
            raise

        return data


    def capitalize(self, data, key=None, keys=None):
        if key is None and keys is None:
            self.logger.error("Either 'key' or 'keys' must be provided.")
            return data

        combined_keys = []
        if key:
            if not isinstance(key, str):
                raise TypeError("Key must be a string.")
            combined_keys.append(key)

        if keys:
            for k in keys:
                if not isinstance(k, str):
                    raise TypeError("All keys must be strings.")
                combined_keys.append(k)

        try:
            for k in combined_keys:
                target, last_key = navigateToKey(data, k, create_missing=False)
                if target is not None and last_key in target:
                    if isinstance(target[last_key], str):
                        target[last_key] = ' '.join(word.capitalize() for word in target[last_key].split())
                    else:
                        self.logger.warning(f"Value of key '{k}' is not a string and cannot be capitalized.")
                else:
                    self.logger.debug(f"Key '{k}' not found.")
        except Exception as e:
            self.logger.error(f"An error occurred while capitalizing key(s): {e}")
            raise

        return data


    def strip(self, data, key=None, left=False, right=False):
        if key is None:
            self.logger.error("Key must be provided.")
            return data

        if not isinstance(key, str):
            raise TypeError("Key must be a string")

        try:
            target, lastKey = navigateToKey(data, key, create_missing=False)

            if lastKey in target:
                if isinstance(target[lastKey], str):
                    if left:
                        target[lastKey] = target[lastKey].lstrip()
                    if right:
                        target[lastKey] = target[lastKey].rstrip()
                    if not left and not right:
                        target[lastKey] = target[lastKey].strip()
                else:
                    self.logger.warning(f"Value of key '{key}' is not a string and cannot be stripped.")
            else:
                self.logger.debug(f"Key '{key}' not found.")

        except Exception as e:
            self.logger.error(f"An error occurred while stripping key '{key}': {e}")
            raise

        return data


    def split(self, data, key=None, separator=",", max_split=0):
        if key is None:
            self.logger.error("Key must be provided.")
            return data

        try:
            if not isinstance(key, str):
                raise TypeError("Key must be a string")

            target, lastKey = navigateToKey(data, key, create_missing=False)
            if lastKey in target:
                if isinstance(target[lastKey], str):
                    if max_split > 0:
                        target[lastKey] = target[lastKey].split(separator, max_split-1)
                    else:
                        target[lastKey] = target[lastKey].split(separator)
                else:
                    self.logger.warning(f"Value of key '{key}' is not a string and cannot be split.")
            else:
                self.logger.debug(f"Key '{key}' not found.")

        except Exception as e:
            self.logger.error(f"An error occurred while splitting key '{key}': {e}")
            raise

        return data


    def join(self, data, key, separator=" ", target=None):
        if key is None:
            self.logger.error("Key must be provided.")
            return data
        try:
            source_target, source_key = navigateToKey(data, key)
            if source_key in source_target:
                if isinstance(source_target[source_key], list):
                    if not isinstance(separator, str):
                        raise TypeError("Separator must be a string")
                    joined_string = separator.join(source_target[source_key])
                    if target:
                        target_target, target_key = navigateToKey(data, target)
                        target_target[target_key] = joined_string
                    else:
                        source_target[source_key] = joined_string
                else:
                    self.logger.warning(f"Value of key '{key}' is not a list and cannot be joined.")
            else:
                self.logger.debug(f"Key '{key}' not found.")
        except KeyError as e:
            self.logger.error(f"KeyError: {e}")
            raise
        except Exception as e:
            self.logger.error(f"An error occurred while joining key '{key}': {e}")
            raise

        return data




    def update(self, data, key, value):
        if not isinstance(key, str):
            self.logger.error("Key must be a string.")
            return data
        try:
            target, lastKey = navigateToKey(data, key, create_missing=False)
            if lastKey in target and target is not None:
                target[lastKey] = value
        except KeyError:
            self.logger.debug(f"Key '{key}' not found.")
        except Exception as e:
            self.logger.error(f"An error occurred while updating key '{key}': {e}")

        return data


    def prepare(self):
        self.commands = self.config.getOption("transform.commands")
        super().prepare()

    def onDataProcess(self, message):
        # main processing loop
        try:
            data = json.loads(message)
            self.logger.info(f"data is: {data}")

            if not self.commands:
                self.logger.error("No commands provided.")
                return json.dumps(data)

            for command in self.commands:
                for action, params in command.items():
                    if action == "add":
                        try:
                            key = params.get("key")
                            value = params.get("value")
                            overwrite = params.get("overwrite", False)
                            if not isinstance(key, str):
                                raise TypeError(f"Invalid key type: {key}. Key must be a string.")
                            self.add(data, key, value, overwrite)
                        except TypeError as e:
                            self.logger.error(e)
                        except Exception as e:
                            self.logger.error(
                                f"An unexpected error occurred while processing command: {e}"
                            )

                    elif action == "move":
                        try:
                            old_key = params.get('from')
                            new_key = params.get('to')
                            if not isinstance(old_key, str) or not isinstance(new_key, str):
                                raise TypeError(f"Invalid key type: {old_key} or {new_key}. Keys must be strings.")
                            self.move(data, old_key, new_key)
                        except TypeError as e:
                            self.logger.error(e)
                        except Exception as e:
                            self.logger.error(
                                f"An unexpected error occurred while processing command: {e}"
                            )

                    elif action == "delete":
                        try:
                            key = params.get("key")
                            keys = params.get("keys")
                            if keys is not None:
                                self.delete(data, keys=keys)
                            if key is not None:
                                self.delete(data, key=key)
                        except Exception as e:
                            self.logger.error(
                                f"An unexpected error occurred while processing command: {e}"
                            )

                    elif action == "copy":
                        try:
                            overwrite = params.get('overwrite', False)
                            src_key = params.get('from')
                            dest_key = params.get('to')
                            if not isinstance(src_key, str) or not isinstance(dest_key, str):
                                raise TypeError(f"Invalid key type: {src_key} or {dest_key}. Keys must be strings.")
                            self.copy(data, src_key, dest_key, overwrite)
                        except TypeError as e:
                            self.logger.error(e)
                        except Exception as e:
                            self.logger.error(
                                f"An unexpected error occurred while processing command: {e}"
                            )

                    elif action == "uppercase":
                        key = params.get('key')
                        keys = params.get('keys')
                        if keys is not None:
                            self.uppercase(data, keys=keys)
                        if key is not None:
                            self.uppercase(data, key=key)

                    elif action == "lowercase":
                        key = params.get('key')
                        keys = params.get('keys')
                        if keys is not None:
                            self.lowercase(data, keys=keys)
                        if key is not None:
                            self.lowercase(data, key=key)

                    elif action == "capitalize":
                        key = params.get('key')
                        keys = params.get('keys')
                        if keys is not None:
                            self.capitalize(data, keys=keys)
                        if key is not None:
                            self.capitalize(data, key=key)

                    elif action == "strip":
                        key = params.get('key')
                        keys = params.get('keys')
                        left = params.get('left', False)
                        right = params.get('right', False)

                        if keys is not None:
                            for k in keys:
                                self.strip(data, key=k, left=left, right=right)
                        elif key is not None:
                            self.strip(data, key=key, left=left, right=right)
                        else:
                            self.logger.error("Either 'key' or 'keys' must be provided for 'strip' action.")

                    elif action == "split":
                        key = params.get('key')
                        separator = params.get('separator', ",")
                        max_split = params.get('max', 0)
                        if key is not None:
                            self.split(data, key=key, separator=separator, max_split=max_split)

                        else:
                            self.logger.error("Key must be provided for 'split' action.")

                    elif action == "join":
                        key = params.get('key')
                        target = params.get('target')
                        separator = params.get('separator', " ")
                        if key is not None:
                            self.join(data, key=key, separator=separator, target=target)

                    elif action == "update":
                        key = params.get('key')
                        value = params.get('value')
                        if key is not None and value is not None:
                            self.update(data, key=key, value=value)

                    else:
                        self.logger.info(f"transform command not found...")

            return json.dumps(data)

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
        except BaseException as e:
            self.logger.error(e)
