from __future__ import annotations

from google.cloud import iam_credentials_v1

credentials_client = iam_credentials_v1.IAMCredentialsClient()

# NB: The project name must be a wildcard `-`, per
# https://cloud.google.com/iam/credentials/reference/rest/v1/projects.serviceAccounts/generateAccessToken.
resource_name = credentials_client.service_account_path(
    project="-", service_account="travis-ci-rbe@pants-remoting-beta.iam.gserviceaccount.com"
)

# NB: This may either be `auth/cloud-platform` or `auth/iam`, per
# https://cloud.google.com/iam/docs/creating-short-lived-service-account-credentials#sa-credentials-oauth
scope = ["https://www.googleapis.com/auth/cloud-platform"]


def generate() -> str:
    access_token: str = credentials_client.generate_access_token(
        name=resource_name, scope=scope
    ).access_token
    return access_token
