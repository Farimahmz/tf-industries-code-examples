import unittest
from unittest.mock import patch, MagicMock
import json
from processor import ReverseGeocodingProcessor


class DummyLogger:
    def __init__(self):
        self.logs = []

    def info(self, msg): self.logs.append(("INFO", msg))
    def warning(self, msg): self.logs.append(("WARN", msg))
    def error(self, msg): self.logs.append(("ERROR", msg))
    def debug(self, msg): self.logs.append(("DEBUG", msg))


class TestReverseGeocodingProcessor(unittest.TestCase):

    def setUp(self):
        self.logger = DummyLogger()
        self.processor = ReverseGeocodingProcessor(self.logger)
        self.processor.inputField = ["Latitude", "Longitude"]
        self.processor.lookupUrl = "http://mock-reverse-geocode.com"
        self.processor.userAgent = "test-agent"
        self.processor.outputField = "ReverseGeoCoding"

    @patch("requests.get")
    def test_lookup_no_valid_coordinates(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps({
            "address": {
                "road": "Test Street",
                "city": "Test City",
                "country": "Testland"
            }
        }).encode("utf-8")
        mock_get.return_value = mock_response

        input_data = {
            "Latitude": "52.5200",
            "Longitude": "13.4050"
        }

        result = self.processor.lookup_no(input_data.copy())
        self.assertIn(self.processor.outputField, result)
        self.assertEqual(result[self.processor.outputField]["input"]["Latitude"], "52.5200")
        self.assertEqual(result[self.processor.outputField]["output"]["country"], "Testland")

    @patch("requests.get")
    def test_lookup_no_invalid_coordinates(self, mock_get):
        self.processor.inputField = ["missingLat", "missingLon"]
        input_data = {
            "Latitude": "52.5200"
        }
        result = self.processor.lookup_no(input_data.copy())
        self.assertNotIn(self.processor.outputField, result)

    @patch("requests.get")
    def test_onDataProcess_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps({
            "address": {
                "city": "Berlin",
                "country": "Germany"
            }
        }).encode("utf-8")
        mock_get.return_value = mock_response

        self.processor.lookupMode = "reverse"

        message = json.dumps({
            "Latitude": "52.5200",
            "Longitude": "13.4050"
        })

        output = self.processor.onDataProcess(message)
        result = json.loads(output)
        self.assertIn(self.processor.outputField, result)
        self.assertEqual(result[self.processor.outputField]["output"]["country"], "Germany")
