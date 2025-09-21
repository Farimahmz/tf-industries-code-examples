import unittest
import logging
from unittest.mock import MagicMock, patch
import json
import uuid
from processor import UUIDProcessor


class TestUUIDProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = UUIDProcessor(logging.getLogger())
        self.processor.target = 'data.uuid'
        self.processor.overwrite = False

    def tearDown(self):
        pass

    def test_successful_uuid_generation(self):
        record = MagicMock()
        record.value = json.dumps({"data": {}})

        result = self.processor.onDataProcess(record)
        result_data = json.loads(result)

        self.assertIn('uuid', result_data['data'])
        self.assertTrue(uuid.UUID(result_data['data']['uuid']))

    def test_uuid_already_exists_no_overwrite(self):
        existing_uuid = str(uuid.uuid4())
        record = MagicMock()
        record.value = json.dumps({"data": {"uuid": existing_uuid}})

        result = self.processor.onDataProcess(record)
        result_data = json.loads(result)

        self.assertEqual(result_data['data']['uuid'], existing_uuid)

    def test_uuid_already_exists_with_overwrite(self):
        self.processor.overwrite = True
        existing_uuid = str(uuid.uuid4())
        record = MagicMock()
        record.value = json.dumps({"data": {"uuid": existing_uuid}})

        result = self.processor.onDataProcess(record)
        result_data = json.loads(result)

        self.assertIn('uuid', result_data['data'])
        self.assertNotEqual(result_data['data']['uuid'], existing_uuid)
        self.assertTrue(uuid.UUID(result_data['data']['uuid']))
