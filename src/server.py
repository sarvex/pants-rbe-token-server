import subprocess

from flask import Flask

app = Flask(__name__)


@app.route("/")
def generate_token() -> str:
    result = subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token"],
        encoding="utf-8",
        capture_output=True,
    ).stdout
    return result.splitlines()[0]
