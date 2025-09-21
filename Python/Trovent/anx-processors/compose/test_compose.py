import unittest
import logging
from unittest.mock import MagicMock
import json
from processor import ComposeProcessor


class TestComposeProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = ComposeProcessor(logging.getLogger())

    def tearDown(self):
        pass

    def test_simple_template(self):
        self.processor.source = "Company {name} has {size} employees."
        self.processor.target = "message"

        record = MagicMock()
        record.value = json.dumps({
            "name": "Trovent",
            "size": 99
        })

        result = self.processor.onDataProcess(record)
        expected = {
            "name": "Trovent",
            "size": 99,
            "message": "Company Trovent has 99 employees."
        }
        self.assertEqual(json.loads(result), expected)

    def test_successful_processing_with_nested_fields(self):
        self.processor.source = 'User {user.name} lives in {user.city}.'
        self.processor.target = 'message'

        record = MagicMock()
        record.value = json.dumps({
            "user": {
                "name": "Bob",
                "city": "Atlantis"
            }
        })

        result = self.processor.onDataProcess(record)
        expected = {
            "user": {
                "name": "Bob",
                "city": "Atlantis"
            },
            "message": "User Bob lives in Atlantis."
        }
        self.assertEqual(json.loads(result), expected)

        self.processor.source = "Company {company.name} has {company.size} employees."
        self.processor.target = 'message'

        record = MagicMock()
        record.value = json.dumps(
            {
                "company": {
                    "name": "Trovent",
                    "size": 99
                }
            }
        )

        result = self.processor.onDataProcess(record)
        expected = {
            "company": {
                "name": "Trovent",
                "size": 99
            },
            "message": "Company Trovent has 99 employees."
        }
        self.assertEqual(json.loads(result), expected)

    def test_missing_source_field(self):
        self.processor.source = 'User {user.name} lives in {user.country}.'
        self.processor.target = 'message'

        record = MagicMock()
        record.value = json.dumps({
            "user": {
                "name": "Alice",
                "city": "Wonderland"
            }
        })

        result = self.processor.onDataProcess(record)
        expected = {
            "user": {
                "name": "Alice",
                "city": "Wonderland"
            },
            "message": "User Alice lives in {user.country}."
        }
        self.assertEqual(json.loads(result), expected)

    def test_empty_template(self):
        self.processor.source = ''
        self.processor.target = 'message'

        record = MagicMock()
        record.value = json.dumps({
            "user": {
                "name": "Charlie",
                "city": "Neverland"
            }
        })

        result = self.processor.onDataProcess(record)
        expected = {
            "user": {
                "name": "Charlie",
                "city": "Neverland"
            },
            "message": ""
        }
        self.assertEqual(json.loads(result), expected)

    def test_no_matching_fields(self):
        self.processor.source = 'Company {company.name} is in {company.location}.'
        self.processor.target = 'message'

        record = MagicMock()
        record.value = json.dumps({
            "user": {
                "name": "Diana",
                "city": "Utopia"
            }
        })

        result = self.processor.onDataProcess(record)
        expected = {
            "user": {
                "name": "Diana",
                "city": "Utopia"
            },
            "message": "Company {company.name} is in {company.location}."
        }
        self.assertEqual(json.loads(result), expected)

    def test_malformed_json(self):
        self.processor.source = 'Company {company.name} has {company.size} employees.'
        self.processor.target = 'message'

        record = MagicMock()
        record.value = '{"company": {"name": "Trovent", "size": 99'

        result = self.processor.onDataProcess(record)
        expected = '{}'
        self.assertEqual(result, expected)

    def test_non_string_values(self):
        self.processor.source = 'Company {company.name} has {company.size} employees and is {company.isPublic}.'
        self.processor.target = 'message'

        record = MagicMock()
        record.value = json.dumps({
            "company": {
                "name": "Trovent",
                "size": 99,
                "isPublic": True
            }
        })

        result = self.processor.onDataProcess(record)
        expected = {
            "company": {
                "name": "Trovent",
                "size": 99,
                "isPublic": True
            },
            "message": "Company Trovent has 99 employees and is True."
        }
        self.assertEqual(json.loads(result), expected)
