from __future__ import annotations

import flask

from src.travis import TravisJob

# from google.cloud import iam_credentials_v1

rbe_execute_tests_scope = [
    "remotebuildexecution.actions.create",
    "remotebuildexecution.actions.get",
    "remotebuildexecution.blobs.create",
    "remotebuildexecution.blobs.get",
    "remotebuildexecution.logstreams.create",
    "remotebuildexecution.logstreams.get",
    "remotebuildexecution.logstreams.update",
]

app = flask.Flask(__name__)
# credentials_client = iam_credentials_v1.IAMCredentialsClient()

# TODO: the service_account credentials.
#  https://googleapis.github.io/google-cloud-python/latest/iam/gapic/v1/api.html
# service_account_path = credentials_client.service_account_path(
#     project="pants-remoting-beta", service_account="foo@gmail.com"
# )

TravisJobId = int


@app.route("/")
def index() -> str:
    return "App running 🎉"


@app.route("/token/generate", methods=["POST"])
def generate_token() -> str:
    travis_job = TravisJob.get_from_api(job_id=int(flask.request.get_json()["travis_job_id"]))
    if not travis_job.is_valid():
        flask.abort(404)
    return str(travis_job)
    # return credentials_client.generate_access_token(
    #     name=service_account_path, scope=rbe_execute_tests_scope
    # ).access_token
