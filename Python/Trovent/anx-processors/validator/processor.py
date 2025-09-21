import sys
import os
import anxprocessor
import json


class ValidatorProcessor(anxprocessor.KafkaProducerMixin,
                         anxprocessor.KafkaConsumerMixin,
                         anxprocessor.BaseProcessor):

    def __init__(self, logger, isVerbose=False):
        super().__init__(logger, isVerbose)
        self.tests = []

    def prepareConfigSchema(self):
        self.config.builder.addOption(
            "validator.tests",
            "array",
            description="List of validation tests to apply on data",
            required=True
        )
        super().prepareConfigSchema()

    def prepare(self):
        self.tests = self.config.getOption("validator.tests", [])
        super().prepare()

    def validate(self, data):
        results = []
        for test in self.tests:
            try:
                result = self._execute_test(test, data)
            except Exception as e:
                result = {
                    "result": "error",
                    "message": f"Unexpected error during test execution: {str(e)}"
                }
                self.logger.error(f"Error executing test: {test}, error: {e}")
            results.append(result)
        return results

    def _execute_test(self, test, data):
        if "exists" in test:
            return self._test_exists(test["exists"], data)
        elif "equals" in test:
            return self._test_equals(test["equals"], data)
        elif "range" in test:
            return self._test_range(test["range"], data)
        elif "contains" in test:
            return self._test_contains(test["contains"], data)
        elif "in" in test:
            return self._test_in(test["in"], data)
        else:
            return {"result": "error", "message": "Invalid test type"}

    def _apply_common_parameters(self, result, test):
        if "id" in test:
            result["id"] = test["id"]
        if "description" in test:
            result["description"] = test["description"]
        return result

    def _test_exists(self, test, data):
        key_path = test["key"].split(".")
        value = self._get_nested_value(data, key_path)
        if value is not None:
            result = {"result": "success"}
        else:
            result = {
                "result": "fail",
                "expected": "Key to exist",
                "message": test.get("message", f"Key '{test['key']}' does not exist.")
            }
        return self._apply_common_parameters(result, test)

    def _test_equals(self, test, data):
        try:
            if "key" in test:
                key_path = test["key"].split(".")
                actual_value = self._get_nested_value(data, key_path)

                if actual_value is None:
                    return {
                        "result": "error",
                        "message": f"Key '{test['key']}' not found or value is None."
                    }

                expected_value = test.get("value")
                case_insensitive = test.get("case_insensitive", False)

                if case_insensitive and isinstance(actual_value, str) and isinstance(expected_value, str):
                    actual_value = actual_value.lower()
                    expected_value = expected_value.lower()

                if actual_value == expected_value:
                    result = {"result": "success"}
                else:
                    result = {
                        "result": "fail",
                        "value": actual_value,
                        "expected": expected_value,
                        "message": test.get("message", f"Value at '{test['key']}' does not match expected.")
                    }

            elif "keys" in test:
                keys = test["keys"]
                values = {key: self._get_nested_value(data, key.split(".")) for key in keys}
                unique_values = set(values.values())
                if len(unique_values) == 1:
                    result = {"result": "success"}
                else:
                    result = {
                        "result": "fail",
                        "value": values,
                        "expected": f"Values of keys {', '.join(keys)} to be equal",
                        "message": test.get("message", f"Values of keys {', '.join(keys)} are not equal.")
                    }
            else:
                result = {
                    "result": "error",
                    "message": "Test must contain either 'key' or 'keys' for equals."
                }
        except Exception as e:
            result = {
                "result": "error",
                "message": f"Unexpected error during test execution: {str(e)}"
            }
        return self._apply_common_parameters(result, test)

    def _test_range(self, test, data):
        key_path = test["key"].split(".")
        actual_value = self._get_nested_value(data, key_path)
        min_value = test.get("min")
        max_value = test.get("max")
        if min_value <= actual_value <= max_value:
            result = {"result": "success"}
        else:
            result = {
                "result": "fail",
                "value": actual_value,
                "expected": f"between {min_value} and {max_value}",
                "message": test.get("message", f"Value at '{test['key']}' is not in range.")
            }
        return self._apply_common_parameters(result, test)

    def _test_contains(self, test, data):
        key_path = test["key"].split(".")
        array = self._get_nested_value(data, key_path)
        expected_value = test["value"]
        if isinstance(array, list) and expected_value in array:
            result = {"result": "success"}
        else:
            result = {
                "result": "fail",
                "value": array,
                "expected": f"contains {expected_value}",
                "message": test.get("message", f"Array at '{test['key']}' does not contain the expected value.")
            }
        return self._apply_common_parameters(result, test)

    def _test_in(self, test, data):
        key_path = test["key"].split(".")
        actual_value = self._get_nested_value(data, key_path)
        allowed_values = test["values"]
        if actual_value in allowed_values:
            result = {"result": "success"}
        else:
            result = {
                "result": "fail",
                "value": actual_value,
                "expected": f"one of {allowed_values}",
                "message": test.get("message", f"Value at '{test['key']}' is not in the list of allowed values.")
            }
        return self._apply_common_parameters(result, test)

    def _get_nested_value(self, data, key_path):
        for key in key_path:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        return data

    def onDataProcess(self, message):
        try:
            if isinstance(message, str):
                data = json.loads(message)
            elif hasattr(message, 'value'):
                data = json.loads(message.value)
            else:
                raise TypeError("Unexpected type for 'message'. Must be str or have 'value' attribute.")

            validation_results = self.validate(data)
            data["validation"] = validation_results
            return json.dumps(data)

        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({"validation": {"error": error_msg}})
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({"validation": {"error": error_msg}})
