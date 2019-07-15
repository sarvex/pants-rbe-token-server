from __future__ import annotations

import flask

from src import token_generator
from src.datastore import JobAttempt
from src.travis import TravisJob

app = flask.Flask(__name__)


@app.route("/")
def index() -> str:
    return "App running 🎉"


@app.route("/token/generate", methods=["POST"])
def generate_token() -> str:
    travis_job = TravisJob.get_from_api(job_id=int(flask.request.get_json()["travis_job_id"]))
    if not travis_job.is_valid():
        flask.abort(404)
    job_attempt = JobAttempt(travis_job_id=travis_job.id_, started_at=travis_job.started_at)
    if job_attempt.already_used():
        flask.abort(403)
    job_attempt.save_to_db()
    return token_generator.generate()
