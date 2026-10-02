from django.conf import settings
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import URLSafeTimedSerializer


EMAIL_VERIFY_TOKEN_MAX_AGE = 60 * 60 * 24


def generic_email_verify_token(user_id):
    """Create a URL-safe, tamper-evident token for email verification."""
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt='email-verify')
    return serializer.dumps({'user_id': user_id})


def check_email_verify_token(token):
    """Return the token's user ID, or None if it is invalid or expired."""
    if not token:
        return None
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt='email-verify')
    try:
        data = serializer.loads(token, max_age=EMAIL_VERIFY_TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    return data.get('user_id')
