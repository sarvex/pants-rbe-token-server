from __future__ import annotations

import os

import flask
import requests
from google.cloud import iam_credentials_v1

pantsbuild_pants_travis_repo_id = 402860

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
credentials_client = iam_credentials_v1.IAMCredentialsClient()

# TODO: the service_account credentials.
#  https://googleapis.github.io/google-cloud-python/latest/iam/gapic/v1/api.html
service_account_path = credentials_client.service_account_path(
    project="pants-remoting-beta", service_account="foo@gmail.com"
)

TravisJobId = int


def belongs_to_pantsbuild_pants(job_id: TravisJobId) -> bool:
    travis_response = requests.get(
        f"https://api.travis-ci.org/job/{job_id}",
        headers={
            "Travis-API-Version": "3",
            "Authorization": f"token {os.getenv('TRAVIS_TOKEN')}",
        },
    )
    try:
        return (
            travis_response.json()["repository"]["id"]
            == pantsbuild_pants_travis_repo_id
        )
    except KeyError:
        return False


@app.route("/token/generate", methods=["POST"])
def generate_token() -> str:
    travis_job_id = int(flask.request.get_json()["travis_job_id"])
    if not belongs_to_pantsbuild_pants(travis_job_id):
        flask.abort(404)
    return str(travis_job_id)
    # return credentials_client.generate_access_token(
    #     name=service_account_path, scope=rbe_execute_tests_scope
    # ).access_token
