from __future__ import annotations

import os
from base64 import b64decode
from dataclasses import dataclass
from datetime import datetime

import requests
from google.cloud import kms_v1

DATE_MECHANISM_FIRST_ENABLED = datetime(year=2019, month=7, day=11)
PANTSBUILD_PANTS_REPO_ID = 402860

JobId = int


def _get_travis_token() -> str:
    env_var = "TRAVIS_TOKEN_ENCRYPTED"
    if env_var not in os.environ:
        raise OSError(
            f"Missing value for `{env_var}`. When running via Google App Engine, this should be "
            "automatically set from `app.yaml`. When running locally, you must set this to the "
            "value in `app.yaml`."
        )
    kms_client = kms_v1.KeyManagementServiceClient()
    resource_name = kms_client.crypto_key_path_path(
        project="pants-remoting-beta",
        location="global",
        key_ring="rbe-token-server",
        crypto_key_path="travis",
    )
    token: str = kms_client.decrypt(
        name=resource_name, ciphertext=b64decode(os.environ[env_var])
    ).plaintext.decode()
    return token


TRAVIS_TOKEN = _get_travis_token()


@dataclass(frozen=True)
class TravisJob:
    id_: JobId
    repo_id: int
    created_at: datetime

    @classmethod
    def get_from_api(cls, *, job_id: JobId) -> TravisJob:
        travis_response = requests.get(
            f"https://api.travis-ci.org/job/{job_id}",
            headers={"Travis-API-Version": "3", "Authorization": f"token {TRAVIS_TOKEN}"},
        )
        if not travis_response.ok:
            travis_response.raise_for_status()
        data = travis_response.json()
        return TravisJob(
            id_=job_id,
            repo_id=data["repository"]["id"],
            created_at=datetime.fromisoformat(data["created_at"][:-5]),
        )

    def is_valid(self) -> bool:
        """Check that the job belongs to pantsbuild.pants and that it was created after we turned
          on this mechanism."""
        return (
            self.repo_id == PANTSBUILD_PANTS_REPO_ID
            and self.created_at >= DATE_MECHANISM_FIRST_ENABLED
        )
