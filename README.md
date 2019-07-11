# Remote Build Execution Token Server

Private server to facilitate using Google Remote Build Execution in Travis CI, particularly due to 
the security risk of untrusted builds (i.e. pull request builds).

## Design

See https://docs.google.com/document/d/1gL3D1f-AzL_LzRxWLskCpVQ2ZlB_26GTETgXkXsrpDY/edit?usp=sharing.

Comments encouraged regarding potential vulnerabilities and/or ways to improve the security of
 this service.

## Developing this repo

### To install

```bash
$ pip3 install pipenv
$ pipenv install --dev
```

### To run

You must first be logged in through the `gcloud` CLI to an account with the appropriate permissions.

First:

```bash
$ export FLASK_APP=src/server.py
$ export FLASK_ENV=development
$ export TRAVIS_TOKEN_ENCRYPTED='CiQABCLzEBhEt1AZ3jhRvQZ2NA1ulmF76mCSwOacYSotbd6P8oASPwDsoWgyqy0ByNPQt6CM9cOpzeBEOTrCfrVKYvl63HVF7sFNUOQCnNpj6ph0P3FBnGeJ2EiwqogB9jerU/FMFA=='
$ pipenv shell
```

Then:

```bash
$ flask run
```

### To run linters / auto-formatters

First:

```bash
$ pipenv shell
```

Then:

```bash
$ isort **/*.py
$ black **/*.py
$ mypy **/*.py
$ pylint **/*.py
```

### To deploy
The site is hosted at `https://pants-remoting-beta.appspot.com`.

1. Install the [GCloud SDK / CLI](https://cloud.google.com/sdk/).
1. `gcloud components install app-engine-python`.
1. `pipenv lock --requirements > requirements.txt`.
   * We must run this command to ensure that the `requirements.txt` is still in sync with the 
   `Pipfile.lock`. This is necessary because Google App Engine only understands `requirements.txt`.
1. `gcloud app deploy --project pants-remoting-beta`.
