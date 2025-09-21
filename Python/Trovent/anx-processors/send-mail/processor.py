# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring

import smtplib
import json
import re
from email.mime.text import MIMEText
import anxprocessor


class SendMailProcessor(anxprocessor.KafkaConsumerMixin,
                        anxprocessor.BaseProcessor):

    def __init__(self, logger, isVerbose=False):
        super().__init__(logger, isVerbose)
        self.smtp_host = ""
        self.smtp_port = 0
        self.smtp_tls = True
        self.smtp_user = ""
        self.smtp_password = ""
        self.mail_subject = ""
        self.mail_text = ""
        self.sender = ""
        self.receivers = []

    def prepareConfigSchema(self):
        self.config.builder.addOption("smtp.host", "string", "SMTP host", required=True)
        self.config.builder.addOption("smtp.port", "number", "SMTP port", required=True)
        self.config.builder.addOption("smtp.TLS", "boolean", "Use TLS", default=True)
        self.config.builder.addOption("smtp.credentials.user", "string", "SMTP username",
                                      required=True)
        self.config.builder.addOption("smtp.credentials.password", "string", "SMTP password",
                                      required=True, writeOnly=True)
        self.config.builder.addOption("mail.subject", "string", "Mail subject", required=True)
        self.config.builder.addOption("mail.text", "string", "Mail body text", required=True)
        self.config.builder.addOption("sender", "string", "Sender email address", required=True)
        self.config.builder.addOption("receivers", "array", "Receiver email addresses",
                                      required=True, custom={"items": {"type": "string"}})
        super().prepareConfigSchema()

    def prepare(self):
        self.smtp_host = self.config.getOption("smtp.host")
        self.smtp_port = self.config.getOption("smtp.port")
        self.smtp_tls = self.config.getOption("smtp.TLS")
        self.smtp_user = self.config.getOption("smtp.credentials.user")
        self.smtp_password = self.config.getOption("smtp.credentials.password")
        self.mail_subject = self.config.getOption("mail.subject")
        self.mail_text = self.config.getOption("mail.text")
        self.sender = self.config.getOption("sender")
        self.receivers = self.config.getOption("receivers")

        super().prepare()


    def get_value_from_path(self, data, path):
        keys = path.split('.')
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        return data

    def replace_variable(self, match, data):
        variable_path = match.group(1).strip()
        value = self.get_value_from_path(data, variable_path)
        return str(value) if value is not None else match.group(0)


    def onDataProcess(self, message):
        try:
            data = json.loads(message)

            subject = re.sub(r'{([^{}]+)}', lambda m: self.replace_variable(m, data), self.mail_subject)
            text = re.sub(r'{([^{}]+)}', lambda m: self.replace_variable(m, data), self.mail_text)

            msg = MIMEText(text, "plain", "utf-8")
            msg["Subject"] = subject

            # msg = MIMEText(self.mail_text, "plain", "utf-8")
            # msg["Subject"] = self.mail_subject
            msg["From"] = self.sender
            msg["To"] = ", ".join(self.receivers)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender, self.receivers, msg.as_string())

        except Exception as e:
            self.logger.error(f"[Error] Failed to send mail: {e}")
            return None
