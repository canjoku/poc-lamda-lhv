import boto3
import os
import json

def fetch_secret(secret_name):
    region = os.environ["AWS_REGION"]
    client = boto3.client("secretsmanager", region)
    secret_object = client.get_secret_value(SecretId=secret_name)
    return json.loads(secret_object["SecretString"])