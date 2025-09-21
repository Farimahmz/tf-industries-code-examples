import unittest
import logging

from processor import TransformProcessor


class TestTransformProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = TransformProcessor(logging.getLogger())
    
    def tearDown(self):
        pass


    def testAdd(self):
        """
        Test method add() of DataProcessor
        """
        data = dict()

        # Helper function to check if any log message contains the expected substring
        def log_contains(log_output, expected_substring):
            return any(expected_substring in message for message in log_output)

        # Test adding a new key
        self.processor.add(data, "my-key", "my-value")
        self.assertEqual(1, len(data))
        self.assertIn("my-key", data.keys())
        self.assertEqual("my-value", data["my-key"])

        # Test adding an existing key without overwrite
        with self.assertLogs(self.processor.logger, level='DEBUG') as log:
            self.processor.add(data, "my-key", "new-value", overwrite=False)
            self.assertEqual(1, len(data))
            self.assertEqual("my-value", data["my-key"])  # Value should not change
            self.assertTrue(log_contains(log.output, "Key my-key already exists and overwrite is set to False. Skipping add."))

        # Test adding an existing key with overwrite
        self.processor.add(data, "my-key", "new-value", overwrite=True)
        self.assertEqual(1, len(data))
        self.assertEqual("new-value", data["my-key"])  # Value should change

        # Test adding with invalid key type
        with self.assertLogs(self.processor.logger, level='ERROR') as log:
            with self.assertRaises(TypeError):
                self.processor.add(data, 123, "xyz")
            self.assertTrue(log_contains(log.output, "Invalid key type: 123. Key must be a string."))

        # Test adding a nested key with overwrite
        self.processor.add(data, "one.two.three", "initial-value")
        self.processor.add(data, "one.two.three", "new-value", overwrite=True)
        self.assertEqual("new-value", data["one"]["two"]["three"])

        # Test debug message for nested key overwrite check
        with self.assertLogs(self.processor.logger, level='DEBUG') as log:
            self.processor.add(data, "one.two.three", "another-value", overwrite=False)
            self.assertEqual("new-value", data["one"]["two"]["three"])  # Value should not change
            self.assertTrue(log_contains(log.output, "Key one.two.three already exists and overwrite is set to False. Skipping add."))


    def testMove(self):
        """
        Test method move() of DataProcessor
        """
        data = {
            "old-key": "value",
            "another-key": "another-value",
            "one": {
                "two": {
                    "three": "nested-value"
                }
            }
        }

        # Helper function to check if any log message contains the expected substring
        def log_contains(log_output, expected_substring):
            return any(expected_substring in message for message in log_output)

        # Test moving a key to a new key
        self.processor.move(data, "old-key", "new-key")
        self.assertNotIn("old-key", data)
        self.assertIn("new-key", data)
        self.assertEqual("value", data["new-key"])

        # Test moving a non-existing key
        with self.assertLogs(self.processor.logger, level='DEBUG') as log:
            self.processor.move(data, "non-existing-key", "new-key")
            self.assertFalse("new-key" in data and data["new-key"] == "non-existing-key")
            self.assertTrue(log_contains(log.output, "Key non-existing-key not found."))

        # Test moving with invalid key types
        with self.assertLogs(self.processor.logger, level='ERROR') as log:
            with self.assertRaises(TypeError):
                self.processor.move(data, 123, "new-key")
            self.assertTrue(log_contains(log.output, "Invalid key type: 123 or new-key. Keys must be strings."))

        with self.assertLogs(self.processor.logger, level='ERROR') as log:
            with self.assertRaises(TypeError):
                self.processor.move(data, "old-key", 456)
            self.assertTrue(log_contains(log.output, "Invalid key type: old-key or 456. Keys must be strings."))

        # Test moving a nested key
        self.processor.move(data, "one.two.three", "one.two.new-key")
        self.assertNotIn("three", data["one"]["two"])

        # Test moving a non-existing nested key
        with self.assertLogs(self.processor.logger, level='DEBUG') as log:
            self.processor.move(data, "one.two.non-existing-key", "one.two.new-key")
            self.assertFalse("new-key" in data["one"]["two"] and data["one"]["two"]["new-key"] == "non-existing-key")
            self.assertTrue(log_contains(log.output, "Key one.two.non-existing-key not found."))



    def testCopy(self):
        """
        Test method copy() of DataProcessor
        """
        data = {
            "existing-key": "existing-value",
            "nested": {
                "existing-nested-key": "nested-value"
            }
        }

        def log_contains(log_output, expected_substring):
            return any(expected_substring in message for message in log_output)

        # Test copying to an existing key with overwrite=False
        with self.assertLogs(self.processor.logger, level='DEBUG') as log:
            self.processor.copy(data, "existing-key", "existing-key", overwrite=False)
            self.assertEqual("existing-value", data["existing-key"])  # Value should not change
            self.assertTrue(log_contains(log.output, "Destination key existing-key already exists and overwrite is set to False. Skipping copy."))

        # Test copying to an existing key with overwrite=True
        self.processor.copy(data, "existing-key", "existing-key", overwrite=True)
        self.assertEqual("existing-value", data["existing-key"])  # Value should be overwritten

        # Test copying to a nested existing key with overwrite=False
        with self.assertLogs(self.processor.logger, level='DEBUG') as log:
            self.processor.copy(data, "nested.existing-nested-key", "nested.existing-nested-key", overwrite=False)
            self.assertEqual("nested-value", data["nested"]["existing-nested-key"])  # Value should not change
            self.assertTrue(log_contains(log.output, "Destination key nested.existing-nested-key already exists and overwrite is set to False. Skipping copy."))

        # Test copying with invalid key types
        with self.assertRaisesRegex(TypeError, "Invalid key type: 123 or new-key. Keys must be strings."):
            self.processor.copy(data, 123, "new-key")



    def testDelete(self):
        """
        Test method delete() of DataProcessor
        """
        data = {
            "my-key": "my-value",
            "another-key": "another-value",
            "one": {
                "two": {
                    "three": "nested-value"
                }
            }
        }

        def log_contains(log_output, expected_substring):
            return any(expected_substring in message for message in log_output)

        # Test deleting a single key
        self.processor.delete(data, key="my-key")
        self.assertNotIn("my-key", data)

        # Test deleting a non-existing single key
        with self.assertLogs(self.processor.logger, level='DEBUG') as log:
            self.processor.delete(data, key="non-existing-key")
            self.assertTrue(log_contains(log.output, "Key non-existing-key not found."))

        # Test deleting multiple keys
        self.processor.delete(data, keys=["another-key", "one.two.three"])
        self.assertNotIn("another-key", data)
        self.assertNotIn("three", data["one"]["two"])

        # Test deleting non-existing multiple keys
        with self.assertLogs(self.processor.logger, level='DEBUG') as log:
            self.processor.delete(data, keys=["non-existing-key-1", "non-existing-key-2"])
            self.assertTrue(log_contains(log.output, "Key non-existing-key-1 not found."))
            self.assertTrue(log_contains(log.output, "Key non-existing-key-2 not found."))

        # Test deleting with invalid key type
        with self.assertLogs(self.processor.logger, level='ERROR') as log:
            with self.assertRaises(TypeError):
                self.processor.delete(data, key=123)
            self.assertTrue(log_contains(log.output, "Invalid key type: Key must be a string."))

        # Test deleting with invalid key types in keys list
        with self.assertLogs(self.processor.logger, level='ERROR') as log:
            with self.assertRaises(TypeError):
                self.processor.delete(data, keys=["valid-key", 456])
            self.assertTrue(log_contains(log.output, "Invalid key type in keys list: int. All keys must be strings."))

        # Test error when neither key nor keys is provided
        with self.assertLogs(self.processor.logger, level='ERROR') as log:
            self.processor.delete(data)
            self.assertTrue(log_contains(log.output, "Either 'key' or 'keys' must be provided."))


    def testUppercase(self):
        """
        Test method uppercase() of TransformProcessor
        """
        data = {"key1": "value1", "key2": "value2"}

        updated_data = self.processor.uppercase(data, key="key1")
        self.assertEqual("VALUE1", updated_data["key1"])
        self.assertEqual("value2", updated_data["key2"])

        updated_data = self.processor.uppercase(data, keys=["key1", "key2"])
        self.assertEqual("VALUE1", updated_data["key1"])
        self.assertEqual("VALUE2", updated_data["key2"])

        with self.assertRaises(TypeError):
            self.processor.uppercase(data, key=123)

        with self.assertRaises(TypeError):
            self.processor.uppercase(data, keys=["key1", 123])


    def testLowercase(self):
        """
        Test method lowercase() of TransformProcessor
        """
        data = {"key1": "VALUE1", "key2": "VALUE2"}

        updated_data = self.processor.lowercase(data, key="key1")
        self.assertEqual("value1", updated_data["key1"])
        self.assertEqual("VALUE2", updated_data["key2"])

        updated_data = self.processor.lowercase(data, keys=["key1", "key2"])
        self.assertEqual("value1", updated_data["key1"])
        self.assertEqual("value2", updated_data["key2"])

        with self.assertRaises(TypeError):
            self.processor.lowercase(data, key=123)

        with self.assertRaises(TypeError):
            self.processor.lowercase(data, keys=["key1", 123])


    def testCapitalize(self):
        """
        Test method capitalize() of TransformProcessor
        """
        data = {"key1": "value1", "key2": "value2"}

        updated_data = self.processor.capitalize(data, key="key1")
        self.assertEqual("Value1", updated_data["key1"])
        self.assertEqual("value2", updated_data["key2"])

        updated_data = self.processor.capitalize(data, keys=["key1", "key2"])
        self.assertEqual("Value1", updated_data["key1"])
        self.assertEqual("Value2", updated_data["key2"])

        data["key3"] = 123
        with self.assertLogs(level="WARNING") as log:
            self.processor.capitalize(data, key="key3")
            self.assertIn("Value of key 'key3' is not a string and cannot be capitalized.", log.output[0])

        with self.assertRaises(TypeError):
            self.processor.capitalize(data, key=123)

        with self.assertRaises(TypeError):
            self.processor.capitalize(data, keys=["key1", 123])


    def testStrip(self):
        """
        Test method strip() of TransformProcessor
        """
        data = {"key1": "  value1  ", "key2": "value2"}

        # Test stripping left side of a key's value
        updated_data = self.processor.strip(data.copy(), key="key1", left=True)
        self.assertEqual("value1  ", updated_data["key1"])

        # Test stripping right side of a key's value
        updated_data = self.processor.strip(data.copy(), key="key1", right=True)
        self.assertEqual("  value1", updated_data["key1"])

        # Test stripping both sides of a key's value
        updated_data = self.processor.strip(data.copy(), key="key1", left=True, right=True)
        self.assertEqual("value1", updated_data["key1"])

        # Test stripping both sides of a key's value without specifying left or right
        updated_data = self.processor.strip(data.copy(), key="key1")
        self.assertEqual("value1", updated_data["key1"])

        # Ensure other data remains unchanged
        self.assertEqual("value2", updated_data["key2"])

        # Test stripping a key with non-string value
        data_with_non_string = {"key1": "  value1  ", "key2": "value2", "key3": 123}
        with self.assertLogs(level="WARNING") as log:
            self.processor.strip(data_with_non_string.copy(), key="key3", left=True)
            self.assertIn("Value of key 'key3' is not a string and cannot be stripped.", log.output[0])

        # Test stripping a non-existent key
        with self.assertLogs(level="DEBUG") as log:
            self.processor.strip(data.copy(), key="non_existing_key", left=True)
            self.assertIn("Key 'non_existing_key' not found.", log.output[0])

        # Test stripping with invalid key type
        with self.assertRaises(TypeError):
            self.processor.strip(data.copy(), key=123)


    def testSplit(self):
        """
        Test method split() of TransformProcessor
        """
        data = {"key1": "value1,value2,value3", "key2": "another;test", "key3": "value1 value2", "key4": 12345, "key5": "value1,value2,value3"}

        # Test splitting a key's value with default separator (comma)
        updated_data = self.processor.split(data.copy(), key="key1")
        self.assertEqual(["value1", "value2", "value3"], updated_data["key1"])

        # Test splitting a key's value with a different separator (semicolon)
        updated_data = self.processor.split(data.copy(), key="key2", separator=";")
        self.assertEqual(["another", "test"], updated_data["key2"])

        updated_data = self.processor.split(data.copy(), key="key5", separator=",", max_split=2)
        self.assertEqual(["value1", "value2,value3"], updated_data["key5"])

        # Test splitting a key's value with a space separator
        updated_data = self.processor.split(data.copy(), key="key3", separator=" ")
        self.assertEqual(["value1", "value2"], updated_data["key3"])

        # Test splitting a non-string value
        with self.assertLogs(level="WARNING") as log:
            self.processor.split(data.copy(), key="key4")
            self.assertIn("Value of key 'key4' is not a string and cannot be split.", log.output[0])

        # Test splitting a key that does not exist
        with self.assertLogs(level="DEBUG") as log:
            self.processor.split(data.copy(), key="non_existing_key")
            self.assertIn("Key 'non_existing_key' not found.", log.output[0])

        # Test splitting with an invalid separator type
        with self.assertRaises(TypeError):
            self.processor.split(data.copy(), key="key1", separator=123)

        # Test splitting with a non-string key
        with self.assertRaises(TypeError):
            self.processor.split(data.copy(), key=123, separator=",")


    def testJoin(self):
        """
        Test method join() of TransformProcessor
        """
        data = {
            "key1": ["value1", "value2", "value3"],
            "key2": "not a list",
            "key3": []
        }

        # Test joining a key's value with default separator (space)
        updated_data = self.processor.join(data.copy(), key="key1")
        self.assertEqual("value1 value2 value3", updated_data["key1"])

        # Test joining a key's value with a different separator (semicolon)
        updated_data = self.processor.join(data.copy(), key="key1", separator=";")
        self.assertEqual("value1;value2;value3", updated_data["key1"])

        # Test joining an empty list
        updated_data = self.processor.join(data.copy(), key="key3")
        self.assertEqual("", updated_data["key3"])

        # Test joining a non-list value
        with self.assertLogs(level="WARNING") as log:
            updated_data = self.processor.join(data.copy(), key="key2")
            self.assertIn("Value of key 'key2' is not a list and cannot be joined.", log.output[0])
            self.assertEqual(data["key2"], updated_data["key2"])  # Ensure data is unchanged

        # Test joining a key that does not exist
        with self.assertLogs(level="DEBUG") as log:
            self.processor.join(data.copy(), key="non_existing_key")
            self.assertIn("Key 'non_existing_key' not found.", log.output[0])

        # Test joining with a non-string separator
        with self.assertRaises(TypeError):
            self.processor.join(data.copy(), key="key1", separator=123)

        # Test joining with target parameter
        updated_data = self.processor.join(data.copy(), key="key1", separator=", ", target="joined_key1")
        self.assertEqual("value1, value2, value3", updated_data["joined_key1"])
        self.assertIn("joined_key1", updated_data)
        self.assertEqual(data["key1"], updated_data["key1"])

        # Test joining with target parameter where the target key does not exist
        updated_data = self.processor.join(data.copy(), key="key1", separator=", ", target="nested.new_key")
        self.assertEqual("value1, value2, value3", updated_data["nested"]["new_key"])
        self.assertIn("nested", updated_data)
        self.assertIn("new_key", updated_data["nested"])
        self.assertEqual(data["key1"], updated_data["key1"])


    def testUpdate(self):
        """
        Test method update() of TransformProcessor
        """
        data = {
            "key1": "value1",
            "key2": {
                "subkey1": "subvalue1"
            }
        }

        # Test updating an existing key's value
        updated_data = self.processor.update(data.copy(), key="key1", value="new_value")
        self.assertEqual("new_value", updated_data["key1"])

        # Test updating a nested key's value
        updated_data = self.processor.update(data.copy(), key="key2.subkey1", value="new_subvalue")
        self.assertEqual("new_subvalue", updated_data["key2"]["subkey1"])

        # Test updating with None key
        with self.assertLogs(level="ERROR") as log:
            self.processor.update(data.copy(), key=None, value="value")
            self.assertIn("Key must be a string.", log.output[0])

        # Test updating with invalid key format
        with self.assertLogs(level="ERROR") as log:
            self.processor.update(data.copy(), key=123, value="value")
            self.assertIn("Key must be a string.", log.output[0])
