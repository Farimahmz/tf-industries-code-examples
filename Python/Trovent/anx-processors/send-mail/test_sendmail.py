# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-module-docstring

import unittest
import logging
import json
import smtplib
from unittest.mock import patch, MagicMock
from processor import SendMailProcessor
from email import message_from_string
import base64


class TestSendMailProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = SendMailProcessor(logging.getLogger())
        self.processor.smtp_host = "smtp.example.com"
        self.processor.smtp_port = 587
        self.processor.smtp_tls = True
        self.processor.smtp_user = "test-user@example.com"
        self.processor.smtp_password = "test-password"
        self.processor.mail_subject = "Message from {user.name}"
        self.processor.mail_text = "This mail is sent by {user.name}."
        self.processor.sender = "test-user@example.com"
        self.processor.receivers = [
            "receiver1@example.com",
            "receiver2@example.com"
        ]

    @patch("smtplib.SMTP")
    def test_send_mail_success_with_variable_substitution(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        test_input = json.dumps({
            "user": {
                "name": "Farimah"
            }
        })
        result = self.processor.onDataProcess(test_input)

        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test-user@example.com", "test-password")
        mock_server.sendmail.assert_called_once()

        called_args = mock_server.sendmail.call_args[0]
        email_raw = called_args[2]

        expected_subject = "Message from Farimah"
        expected_body = "This mail is sent by Farimah."

        # Parse and decode base64 content
        email_message = message_from_string(email_raw)
        encoded_payload = email_message.get_payload()
        decoded_body = base64.b64decode(encoded_payload).decode("utf-8")

        self.assertIn(f"Subject: {expected_subject}", email_raw)
        self.assertIn(expected_body, decoded_body)

        self.assertEqual(called_args[0], "test-user@example.com")
        self.assertEqual(called_args[1], ["receiver1@example.com", "receiver2@example.com"])
        self.assertIsNone(result)

    @patch("smtplib.SMTP", side_effect=Exception("SMTP connection failed"))
    def test_send_mail_connection_failure(self, _mock_smtp):
        test_input = json.dumps({"user": {"name": "Fail"}})
        result = self.processor.onDataProcess(test_input)
        self.assertIsNone(result)

    @patch("smtplib.SMTP")
    def test_send_mail_auth_failure(self, mock_smtp):
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Authentication failed')
        mock_smtp.return_value.__enter__.return_value = mock_server

        test_input = json.dumps({"user": {"name": "AuthError"}})
        result = self.processor.onDataProcess(test_input)
        self.assertIsNone(result)

    @patch("smtplib.SMTP")
    def test_send_mail_tls_failure(self, mock_smtp):
        mock_server = MagicMock()
        mock_server.starttls.side_effect = smtplib.SMTPException("TLS failed")
        mock_smtp.return_value.__enter__.return_value = mock_server

        test_input = json.dumps({"user": {"name": "TLS"}})
        result = self.processor.onDataProcess(test_input)
        self.assertIsNone(result)

    def test_invalid_json_input(self):
        invalid_json = '{"this": "is broken", "oops": '  # Invalid JSON
        result = self.processor.onDataProcess(invalid_json)
        self.assertIsNone(result)

    def test_send_mail_with_empty_receivers(self):
        self.processor.receivers = []
        test_input = json.dumps({"user": {"name": "Nobody"}})
        result = self.processor.onDataProcess(test_input)
        self.assertIsNone(result)

    def test_send_mail_with_invalid_receiver_type(self):
        self.processor.receivers = None
        test_input = json.dumps({"user": {"name": "WrongType"}})
        result = self.processor.onDataProcess(test_input)
        self.assertIsNone(result)

        self.processor.receivers = [0, 42]
        test_input = json.dumps({"user": {"name": "WrongType"}})
        result = self.processor.onDataProcess(test_input)
        self.assertIsNone(result)
