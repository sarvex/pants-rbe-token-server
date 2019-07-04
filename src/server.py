from __future__ import annotations

import os
from datetime import datetime

import flask
import requests
from google.cloud import iam_credentials_v1

date_mechanism_first_enabled = datetime(year=2019, month=7, day=3)
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


@app.route("/token/generate", methods=["POST"])
def generate_token() -> str:
    travis_job_id = int(flask.request.get_json()["travis_job_id"])
    if not is_valid_travis_job(travis_job_id):
        flask.abort(404)
    return str(travis_job_id)
    # return credentials_client.generate_access_token(
    #     name=service_account_path, scope=rbe_execute_tests_scope
    # ).access_token


def is_valid_travis_job(job_id: TravisJobId) -> bool:
    """Check that the job belongs to pantsbuild.pants and that it was created after we turned
    on this mechanism."""
    travis_response = requests.get(
        f"https://api.travis-ci.org/job/{job_id}",
        headers={"Travis-API-Version": "3", "Authorization": f"token {os.getenv('TRAVIS_TOKEN')}"},
    )
    data = travis_response.json()
    try:
        repo_id = data["repository"]["id"]
        created_at = datetime.fromisoformat(data["created_at"][:-5])
    except KeyError:
        return False
    else:
        return (
            repo_id == pantsbuild_pants_travis_repo_id
            and created_at >= date_mechanism_first_enabled
        )
