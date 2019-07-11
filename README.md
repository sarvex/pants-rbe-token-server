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

First:

```bash
$ export FLASK_APP=src/server.py
$ export FLASK_ENV=development
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
