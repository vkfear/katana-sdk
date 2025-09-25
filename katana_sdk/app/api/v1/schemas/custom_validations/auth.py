from .base import *


def login_validate_attributes(values):
    username = getattr(values, "username", None)
    validate_email(username)
    return values


def admin_login_validate_attributes(values):
    login_validate_attributes(values)
    password = getattr(values, "password", None)
    validate_length(password, "Password", True, 8, 15)
    return values


def varify_otp_in_validate_attributes(values):
    otp = getattr(values, "otp", None)
    is_numeric_only(str(otp), "OTP")
    return values


def logout_validate_attributes(values):
    refresh_token = getattr(values, "refresh_token", None)
    required_field(refresh_token, "Refresh Token")
    return values


def reset_pwd_validate_attributes(values):
    admin_login_validate_attributes(values)
    otp = getattr(values, "otp", None)
    password = getattr(values, "password", None)
    confirm_password = getattr(values, "confirm_password", None)

    is_numeric_only(str(otp), "OTP")
    validate_length(otp, "OTP", True, 6, 6)

    required_field(confirm_password, "Confirm Password")

    if password != confirm_password:
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Password does not match.")

    return values


def change_pwd_validate_attributes(cls, values):
    pwd = getattr(values, "password", None)
    c_pwd = getattr(values, "confirm_password", None)
    old_pwd = getattr(values, "old_password", None)
    required_field(old_pwd, "Old Password")
    is_alphanumeric(pwd, "New Password", True, True)
    validate_length(pwd, "New Password", True, 8, 15)
    required_field(c_pwd, "Confirm Password")
    pwd_match(pwd, c_pwd)
    return values
