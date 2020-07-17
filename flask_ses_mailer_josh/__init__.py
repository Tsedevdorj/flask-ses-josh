import boto3
from botocore.exceptions import ClientError

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class SESMailer(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.aws_access_key = self.app.config.get("AWS_ACCESS_KEY_ID") or None
        self.aws_secret_key =  self.app.config.get("AWS_SECRET_ACCESS_KEY") or None
        self.ses_charset = self.app.config.get("SES_CHARSET") or 'UTF-8'
        self.aws_region = self.app.config.get("AWS_REGION") or 'us-west-2'
        self.ses_source_email = self.app.config.get("SES_SOURCE_EMAIL")
        self.client = self._connect()

    def _connect(self):
        if self.aws_access_key and self.aws_secret_key:
            self.client = boto3.client('ses', aws_access_key_id=self.aws_access_key , \
                aws_secret_access_key=self.aws_secret_key, region_name=self.aws_region)
        else:
            self.client = boto3.client('ses', region_name=self.aws_region)
        return self.client

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'ses_connection'):
                ctx.ses_connection = self._connect()
            return ctx.ses_connection

    @classmethod
    def destination(self, to_addresses, cc_addresses):
        """Converts strings to lists and formats a valid SES Destination
        model.

        Args:
            to_addresses: a list of or a string of an email address

        Returns:
            'ToAddresses' Dict to match the SES Destination Model.
        """

        address_list = []
        if isinstance(to_addresses, str):
            address_list.append(to_addresses)
        elif isinstance(to_addresses, list):
            address_list = to_addresses
        cc_address_list = []
        if isinstance(cc_addresses, str):
            cc_address_list.append(cc_addresses)
        elif isinstance(cc_addresses, list):
            cc_address_list = cc_addresses
        return { 'ToAddresses': address_list, 'CcAddresses': cc_address_list }

    def message(self, subject, body, body_type='Text'):
        """Formats the arguments into a valid SES Message.  The SES Message
        contains the Subject and Body of an email.

        Args:
            subject: An email subject
            body: The contents of the body of the email
            body_type: Determines if the email should render Html or
                       just Text.
                Default: 'Text'
                Options: ['Html', 'Text']

        Returns:
            A Dict containing 'Subject' and 'Body', a valid SES Message.
        """

        message = {}
        message.update(self._subject(subject))
        message.update(self._body(body, body_type))
        return message

    def _body(self, body, body_type='Text'):
        # Change body_type to Text when encountering an invalid type.
        if not body_type in ['Text', 'Html']:
            body_type = 'Text'
        body = {
            'Body': {
                body_type: {
                    'Charset': self.ses_charset,
                    'Data': body
                }
            }
        }
        return body

    def _subject(self, subject):
        return {
            'Subject': {
                'Charset': self.ses_charset,
                'Data': subject
            }
        }

    def send(self, subject, body, to_addresses, cc_addresses=[], body_type='Text', **kwargs):
        """Send the email via Amazon SES.

        Args:
            subject: Email's subject line.
            body: Contents of the email body.
            to_addresses: Either a list of or a single email address.
            body_type: Send the email as plain Text or as Html to render HTML.
                Default: 'Text'
                Options: ['Html', 'Text']

        Returns:
            Request Id of the sent email.
        """

        # Try to send the email.
        try:
            # Generate the message
            message = self.message(
                subject=subject,
                body=body,
                body_type=body_type
            )
            if "sender_name" in kwargs:
                source = f"{kwargs.get('sender_name')} <{self.ses_source_email}>"
            else:
                source = self.ses_source_email
            # Provide the contents of the email.
            response = self.client.send_email(
                Destination=self.destination(to_addresses, cc_addresses),
                Message=message,
                Source=source
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response['ResponseMetadata']['RequestId']
