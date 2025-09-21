import unittest
import logging
import json
from unittest.mock import Mock
from processor import ValidatorProcessor


class TestValidatorProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = ValidatorProcessor(logging.getLogger())

    def tearDown(self):
        pass

    def test_validate_equals_success(self):
        self.processor.tests = [{
            "equals": {
                "key": "record.city",
                "value": "Bochum",
                "message": "Wrong city is given"
            }
        }]

        data = {"record": {"city": "Bochum"}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "success")

    def test_validate_equals_fail(self):
        self.processor.tests = [{
            "equals": {
                "key": "record.city",
                "value": "Bochum",
                "message": "Wrong city is given"
            }
        }]

        data = {"record": {"city": "Berlin"}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "fail")
        self.assertEqual(result[0]["expected"], "Bochum")
        self.assertEqual(result[0]["value"], "Berlin")
        self.assertEqual(result[0]["message"], "Wrong city is given")

    def test_validate_equals_multiple_keys_success(self):
        self.processor.tests = [{
            "equals": {
                "keys": ["record.city", "record.expected_city"],
                "message": "City does not match the expected value"
            }
        }]

        data = {"record": {"city": "Bochum", "expected_city": "Bochum"}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "success")

    def test_validate_equals_multiple_keys_fail(self):
        self.processor.tests = [{
            "equals": {
                "keys": ["record.city", "record.expected_city"],
                "message": "City does not match the expected value"
            }
        }]

        data = {"record": {"city": "Berlin", "expected_city": "Bochum"}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "fail")
        self.assertEqual(result[0]["value"], {
            "record.city": "Berlin",
            "record.expected_city": "Bochum"
        })
        self.assertEqual(result[0]["expected"], "Values of keys record.city, record.expected_city to be equal")
        self.assertEqual(result[0]["message"], "City does not match the expected value")

    def test_validate_equals_case_insensitive_success(self):
        self.processor.tests = [{
            "equals": {
                "key": "record.city",
                "value": "bochum",
                "case_insensitive": True,
                "message": "City comparison failed"
            }
        }]

        data = {"record": {"city": "Bochum"}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "success")

    def test_validate_exists_success(self):
        self.processor.tests = [{
            "exists": {
                "key": "record.country",
                "message": "Country is missing"
            }
        }]

        data = {"record": {"country": "Germany"}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "success")

    def test_validate_exists_fail(self):
        self.processor.tests = [{
            "exists": {
                "key": "record.country",
                "message": "Country is missing"
            }
        }]

        data = {"record": {}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "fail")
        self.assertEqual(result[0]["expected"], "Key to exist")
        self.assertEqual(result[0]["message"], "Country is missing")

    def test_validate_range_success(self):
        self.processor.tests = [{
            "range": {
                "key": "record.age",
                "min": 18,
                "max": 65,
                "message": "Age is out of range"
            }
        }]

        data = {"record": {"age": 30}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "success")

    def test_validate_range_fail(self):
        self.processor.tests = [{
            "range": {
                "key": "record.age",
                "min": 18,
                "max": 65,
                "message": "Age is out of range"
            }
        }]

        data = {"record": {"age": 70}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "fail")
        self.assertEqual(result[0]["expected"], "between 18 and 65")
        self.assertEqual(result[0]["value"], 70)
        self.assertEqual(result[0]["message"], "Age is out of range")

    def test_validate_contains_success(self):
        self.processor.tests = [{
            "contains": {
                "key": "record.tags",
                "value": "active",
                "message": "Tag 'active' is missing"
            }
        }]

        data = {"record": {"tags": ["active", "premium"]}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "success")

    def test_validate_contains_fail(self):
        self.processor.tests = [{
            "contains": {
                "key": "record.tags",
                "value": "active",
                "message": "Tag 'active' is missing"
            }
        }]

        data = {"record": {"tags": ["inactive"]}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "fail")
        self.assertEqual(result[0]["expected"], "contains active")
        self.assertEqual(result[0]["value"], ["inactive"])
        self.assertEqual(result[0]["message"], "Tag 'active' is missing")

    def test_validate_in_success(self):
        self.processor.tests = [{
            "in": {
                "key": "record.status",
                "values": ["approved", "pending", "rejected"],
                "message": "Status is not valid"
            }
        }]

        data = {"record": {"status": "approved"}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "success")

    def test_validate_in_fail(self):
        self.processor.tests = [{
            "in": {
                "key": "record.status",
                "values": ["approved", "pending", "rejected"],
                "message": "Status is not valid"
            }
        }]

        data = {"record": {"status": "unknown"}}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "fail")
        self.assertEqual(result[0]["expected"], "one of ['approved', 'pending', 'rejected']")
        self.assertEqual(result[0]["value"], "unknown")
        self.assertEqual(result[0]["message"], "Status is not valid")

    def test_unexpected_error(self):
        self.processor.tests = [{
            "equals": {
                "key": "record.nonexistent",
                "value": 123,
                "message": "This will trigger an error"
            }
        }]

        data = {"record": None}
        result = self.processor.validate(data)
        self.assertEqual(result[0]["result"], "error")
        self.assertIn("Key 'record.nonexistent' not found or value is None.", result[0]["message"])
