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

We use Google's [IAM library's `generate_access_token()`](https://googleapis.github.io/google-cloud-python/latest/iam/gapic/v1/api.html)
feature to generate temporary access tokens from a secure server that may be used by Travis, as follows.

Unique identifiers:
* This is the main unit of abstraction.
* An identifier is composed of the GitHub PR / build + the commit SHA + the Travis shard ID, as follows:
   * Branch builds -  branch name. Accessed via `TRAVIS_BRANCH`.
   * Pull requests - the PR `number`, e.g. `8711`.
      In Travis, accessed via `TRAVIS_PULL_REQUEST`.  
   * Commit SHA - the commit currently being tested. Accessed via `TRAVIS_COMMIT`.
   * Travis Job ID - the integer Travis uses internally. Accessed via `TRAVIS_JOB_ID`. 
        * TODO: does this change upon restarts? We need to make sure it doesn't.
* Why not use a simpler scheme, like only the Travis job ID?
   * We need to ensure that this identifier belongs to Pants, e.g. that someone is not using a Job
     ID for an unrelated project.

Token generation flow:
1. Each Travis shard constructs its unique identifier and sends a `POST` request to our server.
1. The server checks if this is a valid identifier via the Travis and GitHub APIs. `404` if not.
1. The server checks via [Google Cloud Firestore in Datastore Mode]() if that identifier has already been used:
   1. If used `>=3 ` times, reject with a `403`.
   1. Else, generate token and log the creation time in Google Datastore. 

Retries:
* Because each _shard_ gets its own token, rather than the entire build, flaky shards may be
   restarted without restarting the whole build.
* Tokens may be issued concurrently to avoid having to wait if a shard fails quickly.
   * TODO: should we tweak this to require the shard to have failed, as confirmed by Travis? 
      Two downsides: i) can't restart succcesful shards to check for flakiness, and ii) if
      you see in the log that the shard is going to fail, but it hasn't yet finished, then
      you can't eagerly cancel it.

Alert system:
* Core Pants committers will receive email alerts of suspicious behavior under the following circumstances:
   * TODO: under what circumstances should we email?

Additional policies:
* Server only allows whitelisted Travis IP addresses, per https://docs.travis-ci.com/user/ip-addresses/.
   * Environment variable to override this for debugging.
   * Still at risk of non-Pants Travis builds using our resources.
* Blacklist identifiers from before we turn on this mechanism.
    * You should not be able to get a token for a PR from 2018, for example.
* Pull requests must still be `open` for a token to be regenerated.

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
```

Then:

```bash
$ flask run
```

## To run linters / auto-formatters

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
