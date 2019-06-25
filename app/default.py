"""
DON'T EDIT THIS FILE
Copy it to local.py and use that instead.
"""

# Security
#
# Do not ever uncomment this in production.
# DEBUG = True

# SECRET_KEY MUST be set to a secure, random value.
# Generate one with:
#    python -c "import os; from base64 import b64encode; print(b64encode(os.urandom(64)).decode('utf-8'));"
SECRET_KEY = None

# Database
# https://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.sqlite'

MAIL_SERVER = 'smtp.mailgun.org'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'postmaster@yourdomain.com'
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = 'noreply@yourdomain.com'

# Sentry
# https://sentry.io
SENTRY_DSN = ''
