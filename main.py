import src.server

# Google App Engine expects a file main.py with a variable called `app` referencing a
# WSGI-compatible object. See
# https://cloud.google.com/appengine/docs/standard/python3/runtime#application_startup.
app = src.server.app
