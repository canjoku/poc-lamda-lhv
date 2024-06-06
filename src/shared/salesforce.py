from datetime import datetime, timedelta



from botocore.errorfactory import ClientError
from aws_lambda_powertools.utilities import parameters
from simple_salesforce import Salesforce

from src.shared.secrets_salesforce import fetch_secret


AUTHENTICATION_SECRET = "salesforce/authentication/oauth2"
SESSION_SECRET = "salesforce/session_id/oauth2"


class SalesforceClient:
    def __init__(self):
        self.domain = None
        self.is_sandbox = None
        self.username = None
        self.password = None
        self.consumer_key = None
        self.consumer_secret = None

        self.session_id = None
        self.instance = None
        self.session_expiry = None
        self.sf_client = None

        self.log = None

        # Even though the password is only needed for invalid sessions we need to get
        # the domain from SSM for session auth
        self.get_credentials()

        try:
            secret = fetch_secret(SESSION_SECRET)
            self.session_id = secret["session_id"]
            self.instance = secret["instance"]
            self.session_expiry = secret["session_expiry"]

        except ClientError as e:
            if e.response["Error"]["Message"] == "Secrets Manager can't find the specified secret.":
                pass
            else:
                raise

    def get_credentials(self):
        auth_secrets = fetch_secret(AUTHENTICATION_SECRET)
        if auth_secrets["isSandbox"].lower() == "true":
            self.domain = "test"
            self.is_sandbox = True
        else:
            self.domain = None
            self.is_sandbox = False
        self.username = auth_secrets["username"]
        self.password = auth_secrets["password"]
        self.consumer_key = auth_secrets["consumerKey"]
        self.consumer_secret = auth_secrets["consumerSecret"]

    def valid_session(self):
        """Check token validity"""
        return self.session_expiry and self.session_expiry > str(datetime.now())
       

    def auth_salesforce_password(self):
        """
        Authenticate with Salesforce with username and password.
        The resulting session is written to SSM to allow reuse across Lambdas.
        Each time this is called the credentials are retrieved """
        self.get_credentials()

        self.sf_client = Salesforce(
            username=self.username,
            password = self.password,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            domain=self.domain,
        )

        self.session_id = self.sf_client.session_id
        self.instance = self.sf_client.sf_instance
        self.session_expiry = str(datetime.now() + timedelta(minutes=10))

        secret_body = {
            "session_id": self.session_id,
            "session_expiry": self.session_expiry,
            "instance": self.instance,
        }

        parameters.set_secret(name=SESSION_SECRET, value=secret_body)

    def auth_salesforce_session(self):
        self.sf_client = Salesforce(
            session_id=self.session_id, instance=self.instance, domain=self.domain
        )

    def init_salesforce(self):
        """
        Checks the session_id validity and determines the method to authenticate
        If a valid session and sf_client already exist then that connection is used
        """
        if self.valid_session():
            if self.sf_client:
                pass
            else:
                self.auth_salesforce_session()
        else:
            self.auth_salesforce_password()