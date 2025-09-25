from _thread import start_new_thread
from random import randint

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from app.api.utils.otp_manager import send_sign_up_or_sign_in_email, send_forgot_mail
from app.api.v1.schemas.auth import (
    LoginRequest,
    VerifyOtpIn,
    LogOutIn,
    AdminLoginRequest,
    ForgotPwdIn,
    ResetPwdIn,
    ChangePasswordIn,
)
from app.models import Profile, OtpHistory, UserRole, OtpType, BlackListedToken
from .base_imports import *
from .router import router
from ..accessibility.base import logger
from ..utils.auth import (
    get_user_role,
    authenticate_user,
    get_tokens_for_user,
    check_admin_account_status,
    check_otp,
)
from ..utils.reset_token import validate_token

tags = ["Authentication"]


@router.post("/authenticate-user-otp", response={200: dict}, auth=None, tags=tags)
def authenticate_user_with_otp(request, payload: LoginRequest):
    """
    Description
    --
        Handles user login and sign-up via OTP (One-Time Password).

        This API endpoint verifies if the provided username exists in the system. If the user exists,
        an OTP is generated for login purposes; if the user is new, the user is created, and an OTP
        is sent for account verification.

    Steps:
    --
        - If the user exists, a one-time password (OTP) is generated and set as the user's password.
        - If the user doesn't exist, a new user and profile are created, and the OTP is sent for sign-up verification.
        - The OTP is stored in the `OtpHistory` for tracking, and any old OTPs for the user are deleted.
        - The OTP is then sent to the user's email asynchronously.

    Args:
    --
        request (HttpRequest): The request object containing the HTTP request data.
        payload (LoginRequest): A data object containing the username (email) of the user.

    Returns:
    --
        dict: A message indicating that the OTP has been sent to the user's email.

    Raises:
    --
        HttpError: Raised if there is an issue processing the request, with a 422 status code.

    Payload Structure:
    --
        - username: Email address of the user attempting to log in or sign up.

    Example Response:
    --
        {
            "message": "An OTP has been sent to your email address to login."
        }

    Example Error:
    --
        {
            "detail": "Something went wrong."
        }

    """
    user = User.objects.filter(username=payload.username).first()
    if user and user.is_staff:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY, "Username is already reserved!"
        )
    try:
        with transaction.atomic():
            profile_obj = (
                Profile.objects.select_related("user")
                .filter(user__username=payload.username)
                .first()
            )
            otp = str(randint(100000, 999999))

            if profile_obj:
                if get_user_role(profile_obj) not in [
                    UserType.NORMAL_USER,
                    UserType.TECHNICIAN,
                ]:
                    raise HttpError(
                        HTTPStatus.UNPROCESSABLE_ENTITY,
                        "You are not authorized to login from this service.",
                    )
                user_obj = profile_obj.user
                user_obj.set_password(otp)
                user_obj.save()
            else:
                user_obj, _ = User.objects.update_or_create(
                    username=payload.username, defaults={"password": otp}
                )
                user_obj.set_password(otp)
                user_obj.save()
                user_role = UserRole.objects.get(name=UserType.NORMAL_USER)
                profile_obj = Profile.objects.create(
                    user=user_obj, email=payload.username, role=user_role
                )

            if profile_obj.is_active:
                otp_type = OtpType.SIGN_IN_OTP
                is_created = False
            else:
                otp_type = OtpType.SIGN_UP_OTP
                is_created = True

            data_dict = {"name": payload.username, "otp": otp}

            OtpHistory.objects.filter(profile=profile_obj).delete()
            OtpHistory.objects.create(profile=profile_obj, otp=otp, otp_type=otp_type)
        start_new_thread(
            send_sign_up_or_sign_in_email, (payload.username, is_created, data_dict)
        )
        return {"message": "An OTP has been sent to your email address to login."}
    except HttpError as e:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during authenticate_user_with_otp: {str(e)}",
            exc_info=True,
        )
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Something went wrong.")


@router.post("/authenticate-admin-user", response={200: dict}, auth=None, tags=tags)
def authenticate_admin_user(request, payload: AdminLoginRequest):
    """
    Description
    --
        Handles admin user authentication by verifying credentials and sending an OTP.

    Steps:
    --
        - Verifies if the provided username exists and belongs to an admin user.
        - Checks if the user is active.
        - Authenticates the user using the provided password.
        - Generates a secure OTP and stores it in `OtpHistory`.
        - Sends the OTP to the user's email asynchronously.

    Args:
    --
        - `request (HttpRequest)`: The HTTP request object.
        - `payload (AdminLoginRequest)`: Contains:
            - `username`: The email address of the admin user.
            - `password`: The user's login password.

    Returns:
    --
        - `dict`: A message indicating that the OTP has been sent.

    Example Response:
    --
        ```json
        {
            "message": "An OTP has been sent to your email address for login."
        }
        ```

    Raises:
    --
        - `HttpError 404`: If the user account doesn't exist.
        - `HttpError 401`: If the provided password is incorrect.
        - `HttpError 422`: If the user is inactive or unauthorized.
    """
    try:
        with transaction.atomic():

            profile_obj = check_admin_account_status(payload.username)
            user = authenticate(username=payload.username, password=payload.password)
            if not user:
                raise HttpError(
                    HTTPStatus.UNAUTHORIZED, "Provided password is incorrect."
                )

            otp = str(randint(100000, 999999))

            OtpHistory.objects.filter(profile=profile_obj).delete()
            OtpHistory.objects.create(
                profile=profile_obj, otp=otp, otp_type=OtpType.TWO_FACTOR_OTP
            )
        email_data = {"name": payload.username, "otp": otp}
        is_created = False

        start_new_thread(
            send_sign_up_or_sign_in_email, (payload.username, is_created, email_data)
        )

        return {"message": "An OTP has been sent to your email address for login."}

    except HttpError:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during authenticate_admin_user: {str(e)}", exc_info=True
        )
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Something went wrong.")


@router.post("/verify-otp", response={200: dict}, auth=None, tags=tags)
def verify_otp(request, payload: VerifyOtpIn):
    """
    Description
    --
        Handles user OTP verification for login and sign-up.

        This endpoint verifies if the provided username (email) exists in the system.
        If found, it validates the OTP, authenticates the user, and returns authentication
        tokens.

    Steps:
    --
        - Checks if the user profile exists.
        - If the profile exists but is inactive, flags the account as newly created.
        - Validates the OTP and authenticates the user.
        - If authentication is successful, generates authentication tokens.
        - Non-admin users get a new temporary password for security.

    Args:
    --
        request (HttpRequest): The request object containing the HTTP request data.
        payload (VerifyOtpIn): A data object containing the username (email) and OTP.

    Returns:
    --
        dict: A message indicating successful login and tokens for authentication.

        Example Response:
        --
        {
            "token": "<authentication tokens>",
            "message": "Login Successful."
        }

    Raises:
    --
        HttpError: Raised in the following cases:
            - 404: If the user account doesn't exist.
            - 401: If there is suspicious activity during login.
            - 422: If something went wrong during processing.

        Example Error:
        --
        {
            "detail": "Something went wrong."
        }

    Payload Structure:
    --
        - username: The email address of the user attempting to log in.
        - otp: The one-time password provided for verification.

    Example Request:
    --
        {
            "username": "user@example.com",
            "otp": "123456"
        }
    """
    try:
        profile_obj = (
            Profile.objects.select_related("user")
            .filter(user__username__iexact=payload.username)
            .first()
        )

        if not profile_obj:
            logger.warning(
                f"Failed login attempt: User '{payload.username}' not found."
            )
            raise HttpError(
                HTTPStatus.NOT_FOUND,
                "We cannot find this account in our database. Please register first.",
            )

        is_account_created = not profile_obj.is_active

        role_name = get_user_role(profile_obj)

        is_admin = role_name == UserType.ADMIN
        is_two_factor = is_admin  # Admins require two-factor authentication

        with transaction.atomic():
            authenticate_user(
                profile_obj, str(payload.otp), is_account_created, is_two_factor
            )

        if not is_admin:
            user = authenticate(username=payload.username, password=str(payload.otp))

            if user is None:
                raise HttpError(
                    HTTPStatus.UNAUTHORIZED, "Suspicious activity found while login."
                )
            random_password = str(randint(100000, 999999))
            user.set_password(random_password)
            user.save()
        else:
            user = profile_obj.user

        token = get_tokens_for_user(user, role_name, profile_obj.role.id)
        logger.info(
            f"User '{payload.username}' logged in successfully as '{role_name}'."
        )

        return {
            "token": token,
            "message": "Login Successful.",
            "user_role": role_name,
            "is_first_time_password_changed": profile_obj.is_first_time_password_changed,
        }
    except HttpError as e:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during verify_otp: {str(e)}", exc_info=True)
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Something went wrong.")


@router.post("/logout", response={200: dict}, auth=token_auth(), tags=tags)
def user_logout(
    request,
    payload: LogOutIn,
    latitude: float = Header(None),
    longitude: float = Header(None),
):
    """
    User Logout
    -----------
        Endpoint: "/logout"
        Method: POST
        Authentication: Any authenticated user through the `Authorization` header.

    Description
    -----------
        This endpoint is responsible for securely logging out a user by blacklisting both the refresh token provided in the
        payload and the access token from the Authorization header. This prevents the tokens from being used for future
        requests.

    Parameters
    ----------
        request : HttpRequest
            The HTTP request object, which must contain the access token in its Authorization header to authenticate the
            request.
        payload : LogOutIn
            An object containing the refresh token to be invalidated. It should have the following field:
                - refresh_token (str): The refresh token to be blacklisted.

    Returns
    ---------
        200 OK
            Returns a success message indicating the user has been successfully logged out.
            Example: {"message": "Logout successful."}

        422 Unprocessable Entity
            Returned if there is an error in processing the request, such as an invalid token or failure in blacklisting the
            tokens.
            Example: {"detail": "Something went wrong. Please try again."}

    Raises
    ------
        HttpError
            An error is raised with an appropriate HTTP status code and message in case of failures, such as invalid tokens,
            issues in blacklisting tokens, or server-side issues.

    Example
    -------
        POST /logout
        Headers: Authorization: Bearer <access_token>
        Payload:
        {
            "refresh_token": "example_refresh_token_here"
        }

    Functionality
    -------------
        The endpoint performs the following actions:
        - Validates the provided refresh token. If the token is not valid, it raises an HttpError with status 422.
        - Blacklists the provided refresh token to prevent its future use.
        - Optionally, blacklists the access token found in the Authorization header to also prevent its future use.
        - Logs any unexpected errors during the process and raises an HttpError with status 422 if any issue occurs.
    """
    refresh_token = payload.refresh_token

    if not validate_token(refresh_token, True):
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Token is not valid.")
    try:
        # Blacklist the refresh token
        refresh_token_obj = RefreshToken(refresh_token)
        refresh_token_obj.blacklist()
        BlackListedToken.objects.create(token=refresh_token)

        # Blacklist the access token (optional)
        access_token = request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
        BlackListedToken.objects.create(token=access_token)

        return {"message": "Logout successful."}
    except Exception as e:
        logger.error(f"Unexpected error during logout: {str(e)}", exc_info=True)
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY, "Something went wrong. Please try again."
        )


@router.post("/change-password", response={200: dict}, auth=token_auth(), tags=tags)
@validate_role_for_service_access
def user_change_password(
    request,
    payload: ChangePasswordIn,
):
    """
    Change Password
    ---------------
        Endpoint: "/change-password"
        Method: POST
        Authentication: Any authenticated user

    Description
    -----------
        This endpoint allows a logged-in user to change their password. The user must provide their current
        password and a new password along with its confirmation. The system validates the old password and ensures
        the new password meets the required criteria. If the old password is incorrect, the new password is the same
        as the old one, or the new password and confirmation do not match, an appropriate error is returned.

    Parameters:
    -----------
        request : HttpRequest
            The HTTP request object containing user and other request metadata.

        payload : ChangePasswordIn
            An object containing the necessary information for changing the password. It should have the following fields:
                - old_password (str): The current password of the user.
                - password (str): The new password to be set for the user.
                - confirm_password (str): Confirmation of the new password, must match with 'password'.

    Responses:
    ----------
        200 OK
            Returns a success message indicating the password was successfully changed.
            Example: {"message": "Your password has been changed successfully"}

        401 Unauthorized
            Returned if the old password provided is incorrect.
            Example: {"detail": "Old password is incorrect"}

        422 Unprocessable Entity
            Returned if the new password is the same as the old password or if the new password and confirmation password do not match.
            Example: {"detail": "New password cannot be same."}
            Example: {"detail": "Password does not match with confirm password"}

        500 Internal Server Error
            Returned if there is an unexpected error during the password change process.
            Example: {"detail": "Something went wrong. Please try again."}

    Raises:
    -------
        HttpError
            An error is raised with an appropriate HTTP status code and message in case of failures
            such as incorrect old password, identical new password, password mismatch, or server-side issues.

    Example:
    --------
        POST /change-password
        Headers: Authorization: Bearer <token>
        Payload:
        {
            "old_password": "currentpassword123",
            "password": "newpassword123",
            "confirm_password": "newpassword123"
        }
    """
    user = request.user

    if not check_password(payload.old_password, user.password):
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Old password is incorrect")

    if payload.old_password == payload.password:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "New password cannot be same.",
        )

    try:
        user.set_password(payload.password)
        user.save()
        # Logging the password change
        logger.info(f"Password changed for user {user.username}")
        return {"message": "Your password has been changed successfully"}
    except Exception as e:
        logger.error(
            f"Unexpected error during change password: {str(e)}", exc_info=True
        )
        raise HttpError(
            HTTPStatus.INTERNAL_SERVER_ERROR, "Something went wrong. Please try again."
        )


@router.post("/forgot-password", response={200: dict}, auth=None, tags=tags)
def forgot_password(request, payload: ForgotPwdIn):
    """
    Description
    --
        Handles the Forgot Password process by generating a secure OTP and sending it via email.
        - Validates if the provided username exists in the database.
        - Checks if the user account is active.
        - Ensures only users with the `ADMIN` role can request a password reset.
        - Generates a 6-digit OTP and securely stores it in the database.
        - Sends the OTP to the user's registered email asynchronously.

    Request Body:
    --
        - `username` (str, required): The username of the account requesting password recovery.

    Response:
    --
        - **200 OK**: OTP successfully generated and sent to the user's email.
          ```json
          {
            "message": "An OTP has been sent to your email address to recover password."
          }
          ```
        - **404 Not Found**: If the username does not exist in the database.
          ```json
          {
            "detail": "We cannot find this account in our database."
          }
          ```
        - **422 Unprocessable Entity**: If the account is deactivated or the user is unauthorized.
          ```json
          {
            "detail": "Account is deactivated."
          }
          ```
          ```json
          {
            "detail": "You are not authorized to use this service."
          }
          ```
        - **422 Unprocessable Entity**: If an unexpected error occurs.
          ```json
          {
            "detail": "Something went wrong."
          }
          ```

    Authorization:
    --
        - No authentication is required (`auth=None`), as it is a public-facing endpoint.

    Notes:
    --
        - The OTP is valid for a limited time and should be entered promptly.
        - Users must be **ADMIN** to request a password reset.
    """
    try:
        # Check if user profile exists
        profile_obj = check_admin_account_status(payload.username)

        # Generate secure OTP
        otp = str(randint(100000, 999999))

        with transaction.atomic():
            OtpHistory.objects.filter(profile=profile_obj).delete()
            # Store OTP securely in the database
            OtpHistory.objects.create(
                profile=profile_obj, otp=otp, otp_type=OtpType.FORGOT_PWD_OTP
            )

        data_dict = {"name": payload.username, "otp": otp}
        start_new_thread(send_forgot_mail, (payload.username, data_dict))
        return {
            "message": "An OTP has been sent to your email address to recover password.",
        }
    except HttpError as e:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during verify_otp: {str(e)}", exc_info=True)
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Something went wrong.")


@router.post("/reset-password", response={200: dict}, auth=None, tags=tags)
def reset_password(request, payload: ResetPwdIn):
    """
    Description
    --
        Handles the password reset process by verifying OTP and securely updating the user's password.

        - Validates if the provided username exists.
        - Checks if the user is an admin and their account is active.
        - Ensures `password` and `confirm_password` match before updating.
        - Verifies the OTP to ensure it is valid and not expired.
        - Updates the user's password securely using Django's built-in password hashing.
        - Marks the OTP as used and deletes it after a successful password reset.

    Request Body:
    --
        - `username` (str, required): The username of the account requesting a password reset.
        - `otp` (str, required): The one-time password (OTP) received via email.
        - `password` (str, required): The new password to be set.
        - `confirm_password` (str, required): Must match the `password` field.

    Response:
    --
        - **200 OK**: Password successfully updated.
          ```json
          {
            "message": "Success! Your password has been updated securely."
          }
          ```
        - **404 Not Found**: If the user does not exist.
          ```json
          {
            "detail": "User not found."
          }
          ```
        - **422 Unprocessable Entity**: If OTP is invalid or expired.
          ```json
          {
            "detail": "Invalid or expired OTP."
          }
          ```
        - **422 Unprocessable Entity**: If the account is deactivated or unauthorized.
          ```json
          {
            "detail": "Account is deactivated."
          }
          ```
          ```json
          {
            "detail": "You are not authorized to reset this password."
          }
          ```
        - **422 Unprocessable Entity**: If an unexpected error occurs.
          ```json
          {
            "detail": "Something went wrong."
          }
          ```

    Authorization:
    --
        - No authentication required (`auth=None`), as this is a public-facing endpoint.

    Notes:
    --
        - The OTP is valid for a limited time.
        - The new password should meet security requirements (length, complexity, etc.).
        - The OTP is marked as used and deleted after a successful password reset.
    """

    user = get_object_or_404(User, username=payload.username)
    try:
        # Check if user profile exists
        profile_obj = check_admin_account_status(payload.username)

        otp_type = OtpType.FORGOT_PWD_OTP
        otp_history_obj = check_otp(profile_obj, payload.otp, otp_type)
        otp_history_obj.is_used = True
        otp_history_obj.save()

        user.set_password(payload.password)
        user.save()
        otp_history_obj.delete()
        return {
            "message": "Success! Your password has been updated securely.",
        }
    except HttpError as e:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during verify_otp: {str(e)}", exc_info=True)
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Something went wrong.")
