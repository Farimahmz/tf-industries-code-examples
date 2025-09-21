import unittest
import logging
import json
from processor import LookupProcessor


class TestLookupProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = LookupProcessor(logging.getLogger())

    def tearDown(self):
        pass

    def test_lookup_success(self):
        """Test successful lookup for a valid postal code."""
        self.processor.lookup_key = "postal.code"
        self.processor.lookup_destination = "postal.city"
        self.processor.lookup_dict = {
            "44795": "Bochum",
            "44801": "Bochum",
            "10115": "Berlin",
            "45131": "Essen",
            "28201": "Bremen"
        }

        data = {"postal": {"code": "44801"}}
        result = self.processor.lookup(data)
        self.assertEqual(result["postal"]["city"], "Bochum")

    def test_lookup_missing_key(self):
        """Test lookup when the input data is missing the required key."""
        self.processor.lookup_key = "postal.code"
        self.processor.lookup_destination = "postal.city"
        self.processor.lookup_dict = {
            "44795": "Bochum",
            "44801": "Bochum",
            "10115": "Berlin",
            "45131": "Essen",
            "28201": "Bremen"
        }

        data = {"postal": {}}
        result = self.processor.lookup(data)
        self.assertNotIn("city", result["postal"])

    def test_lookup_invalid_postal_code(self):
        """Test lookup when the postal code is not in the dictionary."""
        self.processor.lookup_key = "postal.code"
        self.processor.lookup_destination = "postal.city"
        self.processor.lookup_dict = {
            "44795": "Bochum",
            "44801": "Bochum",
            "10115": "Berlin",
            "45131": "Essen",
            "28201": "Bremen"
        }

        data = {"postal": {"code": "99999"}}
        result = self.processor.lookup(data)
        self.assertNotIn("city", result["postal"])

    def test_lookup_invalid_data_structure(self):
        """Test lookup when the data structure is unexpected."""
        self.processor.lookup_key = "postal.code"
        self.processor.lookup_destination = "postal.city"
        self.processor.lookup_dict = {
            "44795": "Bochum",
            "44801": "Bochum",
            "10115": "Berlin",
            "45131": "Essen",
            "28201": "Bremen"
        }

        data = {"unexpected": {"key": "value"}}
        result = self.processor.lookup(data)
        self.assertNotIn("city", result)

    def test_onDataProcess_valid_message(self):
        """Test processing a valid JSON message."""
        self.processor.lookup_key = "postal.code"
        self.processor.lookup_destination = "postal.city"
        self.processor.lookup_dict = {
            "44795": "Bochum",
            "44801": "Bochum",
            "10115": "Berlin",
            "45131": "Essen",
            "28201": "Bremen"
        }

        message = json.dumps({"postal": {"code": "44795"}})
        result = self.processor.onDataProcess(message)
        result_data = json.loads(result)
        self.assertEqual(result_data["postal"]["city"], "Bochum")

    def test_onDataProcess_invalid_json(self):
        """Test processing an invalid JSON message."""
        message = "{invalid_json}"
        result = self.processor.onDataProcess(message)
        result_data = json.loads(result)
        self.assertIn("error", result_data)

    def test_onDataProcess_unexpected_message_type(self):
        """Test processing an unexpected message type."""
        message = 12345  # Not a string or object with 'value'
        with self.assertRaises(TypeError):
            self.processor.onDataProcess(message)
