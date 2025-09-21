import unittest
import logging
import json
from processor import MSISDNLookupProcessor


class TestMSISDNLookupProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = MSISDNLookupProcessor(logging.getLogger())
        self.processor.inputField = "MSISDN"
        self.processor.outputField = "MSISDNLookup"

    def test_lookup_country_valid_germany(self):
        input_data = {
            "Full Name": "Test User",
            "MSISDN": "+4917631058456"
        }

        result = self.processor.lookup_country(input_data.copy())
        self.assertEqual(result["MSISDNLookup"]["input"], "+4917631058456")
        self.assertEqual(result["MSISDNLookup"]["output"]["country"], "Germany")
        self.assertTrue(result["MSISDNLookup"]["output"]["operator"])

    def test_lookup_country_valid_us(self):
        input_data = {
            "Full Name": "US User",
            "MSISDN": "+15053558736"
        }

        result = self.processor.lookup_country(input_data.copy())
        self.assertEqual(result["MSISDNLookup"]["input"], "+15053558736")
        self.assertEqual(result["MSISDNLookup"]["output"]["country"], "United States")
        self.assertTrue(result["MSISDNLookup"]["output"]["operator"])

    def test_lookup_country_valid_uk(self):
        input_data = {
            "Full Name": "UK User",
            "MSISDN": "+447570326477"
        }

        result = self.processor.lookup_country(input_data.copy())
        self.assertEqual(result["MSISDNLookup"]["input"], "+447570326477")
        self.assertEqual(result["MSISDNLookup"]["output"]["country"], "United Kingdom")
        self.assertTrue(result["MSISDNLookup"]["output"]["operator"])


    def test_lookup_country_valid_iran(self):
        input_data = {
            "Full Name": "Iran User",
            "MSISDN": "+989124338645"
        }

        result = self.processor.lookup_country(input_data.copy())
        self.assertEqual(result["MSISDNLookup"]["input"], "+989124338645")
        self.assertEqual(result["MSISDNLookup"]["output"]["country"], "Iran, Islamic Republic of")
        self.assertTrue(result["MSISDNLookup"]["output"]["operator"])

    def test_lookup_country_valid_france(self):
        input_data = {
            "Full Name": "FR User",
            "MSISDN": "+33612345678"
        }

        result = self.processor.lookup_country(input_data.copy())
        self.assertEqual(result["MSISDNLookup"]["input"], "+33612345678")
        self.assertEqual(result["MSISDNLookup"]["output"]["country"], "France")
        self.assertTrue(result["MSISDNLookup"]["output"]["operator"])

    def test_lookup_country_invalid_format(self):
        input_data = {
            "Full Name": "Test User",
            "MSISDN": "not_a_number"
        }

        result = self.processor.lookup_country(input_data.copy())
        self.assertNotIn("MSISDNLookup", result)

    def test_lookup_country_missing_msisdn(self):
        input_data = {
            "Full Name": "Test User"
        }

        result = self.processor.lookup_country(input_data.copy())
        self.assertEqual(result, input_data)

    def test_onDataProcess_valid(self):
        message = json.dumps({
            "Full Name": "Test User",
            "MSISDN": "+4917631058456"
        })

        result = self.processor.onDataProcess(message)
        result_data = json.loads(result)

        self.assertEqual(result_data["MSISDNLookup"]["input"], "+4917631058456")
        self.assertEqual(result_data["MSISDNLookup"]["output"]["country"], "Germany")
        self.assertTrue(result_data["MSISDNLookup"]["output"]["operator"])

    def test_onDataProcess_invalid_json(self):
        message = '{"Full Name": "Test User", "MSISDN": +49176BADJSON'
        result = self.processor.onDataProcess(message)
        self.assertIsNone(result)
