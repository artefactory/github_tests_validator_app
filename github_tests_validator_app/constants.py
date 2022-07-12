import os

APP_ID = 218336
with open(
    os.path.normpath(os.path.expanduser("~/.certs/github/school-of-data-key.pem"))
) as cert_file:
    APP_KEY = cert_file.read()
