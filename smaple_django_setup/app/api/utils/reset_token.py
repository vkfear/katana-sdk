import jwt
from datetime import datetime, timedelta
from django.conf import settings


def validate_token(token, validate_only=False):
    """
    To validate token and check all user data is correct or not

    Args:
        token (str): forgot password token received on email
        validate_only (bool, optional): If True, the function only checks token validity (expiration and signature) without extracting data.

    Returns:
        user email if token is validated
        Return None if Token is Expired or decode error occurs
    """
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        expiration_time = datetime.fromtimestamp(data["exp"])

        if expiration_time < datetime.now():
            return None

        if validate_only:
            return True

        return data["user_email"]

    except jwt.ExpiredSignatureError:
        return None
    except jwt.DecodeError:
        return None
