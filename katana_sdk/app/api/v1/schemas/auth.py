from .base import *
from .custom_validations import (
    login_validate_attributes,
    varify_otp_in_validate_attributes,
    logout_validate_attributes,
    admin_login_validate_attributes,
    reset_pwd_validate_attributes,
    change_pwd_validate_attributes,
)
from typing_extensions import Annotated
from pydantic import StringConstraints


class LoginRequest(Schema):
    """
    A schema for validating login request data.

    Attributes:
        username (str): The username entered by the user, automatically converted to lowercase.

    Class Variables:
        _validate_attributes (function): A model validator that validates the attributes
            of the login request before the actual validation. It uses the custom validation
            function `login_validate_attributes`.

    This schema is used to ensure the provided login data is correctly formatted
    before any further processing, such as authenticating the user.
    """

    username: Annotated[str, StringConstraints(to_lower=True)]

    _validate_attributes = model_validator(mode="before")(login_validate_attributes)


class AdminLoginRequest(LoginRequest):
    password: str

    _validate_attributes = model_validator(mode="before")(
        admin_login_validate_attributes
    )


class ForgotPwdIn(LoginRequest):
    pass


class ResetPwdIn(AdminLoginRequest):
    otp: str
    confirm_password: str

    _validate_attributes = model_validator(mode="before")(reset_pwd_validate_attributes)


class VerifyOtpIn(LoginRequest):
    """
    A schema for verifying OTP (One-Time Password) during the login process.

    Inherits from:
        LoginRequest: This schema extends the `LoginRequest` schema and adds additional
        functionality for OTP validation.

    Attributes:
        otp (int): The One-Time Password (OTP) entered by the user for verification.

    Class Variables:
        _validate_verify_otp_in_attributes (function): A model validator that validates
            the OTP-related attributes before the actual validation. It uses the custom
            validation function `varify_otp_in_validate_attributes`.

    This schema is used to validate and process the OTP provided by the user after
    the initial login request (username), ensuring it is valid before allowing
    further actions (like completing the login).
    """

    otp: int

    _validate_verify_otp_in_attributes = model_validator(mode="before")(
        varify_otp_in_validate_attributes
    )


class TokenLoginResponse(Schema):
    """
    A schema for the response returned after a successful token-based login.

    Attributes:
        email (str): The email address associated with the user account.
        is_super_admin (bool): A flag indicating whether the user has super admin privileges.
        token (str): The authentication token provided for the user's session.

    This schema is used to structure the response data when a user successfully logs in
    and receives a token, along with their email and admin status, for further authentication.
    """

    email: str
    is_super_admin: bool
    token: str


class LogOutIn(Schema):
    """
    A schema for the request to log out a user using a refresh token.

    Attributes:
        refresh_token (str): The refresh token used to authenticate the logout request.

    Class Variables:
        _validate_attributes (function): A model validator that validates the attributes
            of the logout request before the actual validation. It uses the custom
            validation function `logout_validate_attributes`.

    This schema is used to ensure that the provided refresh token is valid before
    logging the user out and invalidating the session.
    """

    refresh_token: str = Field(description="Refresh token for logging out")

    _validate_attributes = model_validator(mode="before")(logout_validate_attributes)


class LogoutResponse(Schema):
    """
    A schema for the response returned after a successful logout.

    Attributes:
        message (str): A message indicating the result of the logout request,
                        such as "Logout successful" or an error message.

    This schema is used to structure the response data sent back to the client after
    a logout action is performed, providing feedback to the user about the outcome.
    """

    message: str


class ChangePasswordIn(Schema):
    """
    Schema for Logged-in User Change Password Request.

    This class defines the structure of a password change request for logged-in
    users, including the old password, new password, and confirmation of the new
    password. It includes a root validator to ensure that the provided attributes
    meet the necessary criteria for changing the password.

    Attributes:
        old_password (str): The current password of the user.
        password (str): The new password that the user wants to set.
        confirm_password (str): Confirmation of the new password to ensure it matches.

    Validators:
        _validate_attributes: A root validator that calls `change_pwd_validate_attributes`
        to perform custom validation on the old_password, password, and confirm_password
        attributes, ensuring they meet the necessary requirements.
    """

    old_password: str
    password: str
    confirm_password: str

    _validate_attributes = model_validator(mode="before")(
        change_pwd_validate_attributes
    )
