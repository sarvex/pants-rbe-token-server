# Remote Build Execution Token Server

Private server to facilitate using Google Remote Build Execution in Travis CI, particularly due to 
the security risk of untrusted builds (i.e. pull request builds).

## Motivating problem

To remote tests in CI, we need to have authenticated a user with at least the role 
`roles/remotebuildexecution.artifactCreator`, per 
https://cloud.google.com/remote-build-execution/docs/access-control.

We don't want any bad actor to be able to log in with that account—because they could use
it to overuse our resources—so we must secure the credentials to that login. Normally, we could do
this via Travis's [encrypted environment variables](https://docs.travis-ci.com/user/environment-variables#defining-encrypted-variables-in-travisyml).
That will not work, however, due to pull request builds, which are inherently unsafe as a bad
actor could write code to leak our credentials, e.g. echoing any env vars we use.

Instead, we must either:
1) Give up on remoting for untrusted builds and only provide this option for committers and contributors who are able to do branch builds.
   * First-time contributors would then have very long CI builds still, which would require us 
   paying for more Travis workers than we'd like.
   * Our CI setup would get even more complex—having to support remoting and conventional builds.
2) Find a safe-enough workaround for CI to have the permissions it needs.
   * Must not allow bad actors to gain permanent access to our resources.
   * Should prevent bad actors from using for other purposes, e.g. other Travis builds or using
   the account locally.

## Design

We use Google's [print-access-token](https://cloud.google.com/sdk/gcloud/reference/auth/application-default/print-access-token)
feature to generate temporary access tokens from a secure server that may be used by Travis, as follows:

...

### Rejected alternative: short lived privilege escalation

Google has a service for temporarily elevating the permissions of a service account: 
https://cloud.google.com/iam/docs/creating-short-lived-service-account-credentials

This would involve creating a permanent service account for Travis, that by default has no
permissions, and upon a PR gets a temporary escalation.

This solution won't work because we would have to log in to that permanent worker in our 
`.travis.yml`, meaning that the login to that account will be public. Even though by default it
cannot do anything malicious, during any window of privilege escalation, a bad actor could grab
the public login and use our resources in other environments (e.g. locally) without us knowing.

# Developing this repo

## To install

```bash
$ pip3 install pipenv
$ pipenv install --dev
```

## To run

First:

```bash
$ export FLASK_APP=src/server.py
$ export FLASK_ENV=development
$ pipenv shell
$ flask run
```

Then:

```bash
$ flask run
```

## To run linters / auto-formatters

```bash
$ isort **/*.py
$ black **/*.py
$ mypy **/*.py
$ pylint **/*.py
```
