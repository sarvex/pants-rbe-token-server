from __future__ import annotations

import dataclasses
import os
from typing import Any, Dict, Optional

import flask
import requests
from google.cloud import iam_credentials_v1

rbe_execute_tests_scope = [
    "remotebuildexecution.actions.create",
    "remotebuildexecution.actions.get",
    "remotebuildexecution.blobs.create",
    "remotebuildexecution.blobs.get",
    "remotebuildexecution.logstreams.create",
    "remotebuildexecution.logstreams.get",
    "remotebuildexecution.logstreams.update",
]

pantsbuild_pants_travis_repo_id = 402860

app = flask.Flask(__name__)
credentials_client = iam_credentials_v1.IAMCredentialsClient()

# TODO: the service_account credentials.
#  https://googleapis.github.io/google-cloud-python/latest/iam/gapic/v1/api.html
service_account_path = credentials_client.service_account_path(
    project="pants-remoting-beta", service_account="foo@gmail.com"
)


@dataclasses.dataclass(frozen=True)
class Identifier:
    commit_sha: str
    travis_job_id: str
    branch_name: Optional[str] = None
    pr_number: Optional[int] = None

    def __post_init__(self) -> None:
        if self.branch_name is None and self.pr_number is None:
            raise ValueError(
                "Must specify either the branch name (for branch builds) "
                "or the PR number (for PR builds)."
            )

    @staticmethod
    def from_json(json: Dict[str, Any]) -> Identifier:
        return Identifier(
            commit_sha=json["commit_sha"],
            travis_job_id=json["travis_job_id"],
            branch_name=json["branch_name"] if "branch_name" in json else None,
            pr_number=int(json["pr_number"]) if "pr_number" in json else None,
        )

    def exists_in_pantsbuild_pants(self) -> bool:
        travis_response = requests.get(
            f"https://api.travis-ci.org/job/{self.travis_job_id}",
            headers={
                "Travis-API-Version": "3",
                "Authorization": f"token {os.getenv('TRAVIS_TOKEN')}",
            },
        )
        try:
            return travis_response.json()["repository"]["id"] == pantsbuild_pants_travis_repo_id
        except KeyError:
            return False


@app.route("/token/generate", methods=["POST"])
def generate_token() -> str:
    identifier = Identifier.from_json(flask.request.get_json())
    if not identifier.exists_in_pantsbuild_pants():
        flask.abort(404)
    return str(identifier)
    # return credentials_client.generate_access_token(
    #     name=service_account_path, scope=rbe_execute_tests_scope
    # ).access_token
