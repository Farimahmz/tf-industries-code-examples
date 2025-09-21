import unittest
import logging
from unittest.mock import MagicMock, patch
import json

from processor import JSONParserProcessor


class TestJSONParserProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = JSONParserProcessor(logging.getLogger())

    def tearDown(self):
        pass

    def test_successful_processing(self):
        self.processor.source = 'message'
        self.processor.target = 'result'
        self.processor.error_field = 'error'
        self.processor.deleteAfterParsing = 'true'
        record = MagicMock()
        record.value = json.dumps({"message" : "{ \"name\" : \"Trovent\", \"year\" : 2019 }", "type" : "company"})

        result = self.processor.onDataProcess(record)
        expected = {'message': '{ "name" : "Trovent", "year" : 2019 }', 'type': 'company', 'result': {'name': 'Trovent', 'year': 2019}}
        self.assertEqual(json.loads(result), expected)



    def test_missing_source_field(self):
        self.processor.source = 'messagex'
        self.processor.error_field = 'error'
        record = MagicMock()
        record.value = json.dumps({"message" : "{ \"name\" : \"Trovent\", \"year\" : 2019 }", "type" : "company"})

        result = self.processor.onDataProcess(record)
        expected = {"message": "{ \"name\" : \"Trovent\", \"year\" : 2019 }", "type": "company", "error": "Source field 'messagex' not found"}
        self.assertEqual(json.loads(result), expected)


    def test_invalid_json_in_source_field(self):
        self.processor.source = 'message'
        self.processor.error_field = 'error'

        record = MagicMock()
        record.value = '{"message": "{ \\"name\\" : \\"Trovent\\", \\"year\\" : 2019 }", "type": }'
        result = self.processor.onDataProcess(record)
        expected = {"error": "JSON decode error: Expecting value: line 1 column 68 (char 67)"}
        self.assertEqual(json.loads(result), expected)


