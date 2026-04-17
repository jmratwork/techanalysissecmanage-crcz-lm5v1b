import os
import re

import bcrypt


DEFAULT_BCRYPT_ROUNDS = int(os.getenv('PASSWORD_BCRYPT_ROUNDS', '12'))
MIN_PASSWORD_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', '10'))
PASSWORD_COMPLEXITY_REGEX = os.getenv(
    'PASSWORD_COMPLEXITY_REGEX',
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$',
)


def _validate_password_strength(password):
    """Return a human-readable error if password does not meet policy."""

    if not isinstance(password, str):
        return 'password must be a string'
    if len(password) < MIN_PASSWORD_LENGTH:
        return f'password must be at least {MIN_PASSWORD_LENGTH} characters long'
    if PASSWORD_COMPLEXITY_REGEX and not re.match(PASSWORD_COMPLEXITY_REGEX, password):
        return 'password does not meet complexity requirements'
    return None


def hash_password(password):
    """Hash a password using bcrypt and enforce configurable strength checks."""

    validation_error = _validate_password_strength(password)
    if validation_error:
        raise ValueError(validation_error)
    encoded = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=DEFAULT_BCRYPT_ROUNDS)
    return bcrypt.hashpw(encoded, salt).decode('utf-8')


def verify_password(password, hashed_password):
    """Verify password against a bcrypt hash."""

    if not isinstance(password, str) or not isinstance(hashed_password, str):
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False
