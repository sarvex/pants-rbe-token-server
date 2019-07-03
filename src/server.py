from flask import Flask
from google.cloud import iam_credentials_v1

app = Flask(__name__)
credentials_client = iam_credentials_v1.IAMCredentialsClient()

rbe_execute_tests_scope = [
    "remotebuildexecution.actions.create",
    "remotebuildexecution.actions.get",
    "remotebuildexecution.blobs.create",
    "remotebuildexecution.blobs.get",
    "remotebuildexecution.logstreams.create",
    "remotebuildexecution.logstreams.get",
    "remotebuildexecution.logstreams.update",
]
# TODO: the service_account credentials.
#  https://googleapis.github.io/google-cloud-python/latest/iam/gapic/v1/api.html
service_account_path = credentials_client.service_account_path(
    project="pants-remoting-beta", service_account="foo@gmail.com"
)


@app.route("/")
def generate_token() -> str:
    return credentials_client.generate_access_token(
        name=service_account_path, scope=rbe_execute_tests_scope
    ).access_token
