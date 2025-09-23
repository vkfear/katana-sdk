from http import HTTPStatus

from ninja.errors import HttpError
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import Profile, UserType, OtpHistory, OtpType

from django.utils import timezone


def check_admin_account_status(username):
    profile_obj = (
        Profile.objects.select_related("user")
        .filter(user__username__iexact=username)
        .first()
    )
    if not profile_obj:
        raise HttpError(
            HTTPStatus.NOT_FOUND,
            "We cannot find this account in our database.",
        )

    if not profile_obj.is_active:
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Account is deactivated.")

    role_name = get_user_role(profile_obj)

    if role_name not in [UserType.ADMIN, UserType.MANAGER]:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "You are not authorized to use this service.",
        )

    return profile_obj


def check_otp(profile_obj, otp, otp_type):
    otp_history = OtpHistory.objects.filter(
        profile=profile_obj, otp=otp, otp_type=otp_type
    ).first()

    if otp_history is None:
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Incorrect verification code.")

    if otp_history.expiration_time <= timezone.now():
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "This Otp is expired. Please get a new OTP.",
        )

    if otp_history.is_used:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "This Otp is already used.",
        )

    return otp_history


#######################################################
# Generate Token Manually
def get_tokens_for_user(user, role_name, role_id):
    """
    Generates and returns authentication tokens (refresh and access tokens) for a given user.

    This function creates a refresh token and an access token for the specified user. It also
    embeds additional custom claims such as the user's email, role name, and role ID into the token.

    Args:
        user (User): The user instance for whom the tokens are being generated.
                     Must be a valid Django user model instance.
        role_name (str): The name of the role associated with the user.
        role_id (int): The ID of the role associated with the user.

    Returns:
        dict: A dictionary containing the generated tokens:
            - "refresh": The refresh token as a string.
            - "access": The access token as a string.

    Raises:
        HttpError: If token generation fails, an HTTP 422 error is raised with an appropriate message.

    Dependencies:
        - Requires `RefreshToken` from Django REST Framework Simple JWT for token generation.
        - Custom claims such as `email`, `role_id`, and `role_name` are added to the refresh token.

    Example:
        tokens = get_tokens_for_user(user, "Admin", 1)
        print(tokens)
        # Output: {'refresh': '<refresh_token>', 'access': '<access_token>'}

    Notes:
        - Ensure the `user` instance is authenticated and active.
        - Proper exception handling is included for unexpected errors.

    """
    try:
        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        refresh["role_id"] = role_id
        refresh["role_name"] = role_name
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    except Exception as e:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY, "Something went wrong. Please try again."
        )


def authenticate_user(profile_obj, otp, is_account_created=False, is_two_factor=False):
    """
    Authenticates a user by verifying the provided OTP (One-Time Password).

    This function validates the OTP entered by the user for either sign-up or sign-in processes.
    It ensures that the OTP is correct, not expired, and has not been previously used.
    If the user is signing up, their profile is activated upon successful OTP verification.

    Args:
        profile_obj (Profile): The profile object associated with the user.
        otp (str): The one-time password provided by the user for authentication.
        is_account_created (bool): A flag indicating whether the user is signing up (`True`)
                                   or signing in (`False`).

    Raises:
        HttpError: Raised in the following scenarios:
            - If the OTP is incorrect.
            - If the OTP has expired.
            - If the OTP has already been used.

    Side Effects:
        - If `is_account_created` is `True` and the OTP is valid, the user's profile is activated.
        - The `is_used` flag of the `OtpHistory` instance is updated after successful verification.

    Dependencies:
        - `OtpType`: Enum for distinguishing between sign-up and sign-in OTP types.
        - `OtpHistory`: Model that stores OTP details such as type, expiration time, and usage status.
        - `timezone.now()`: Used to compare the OTP's expiration time with the current time.

    Example:
        try:
            authenticate_user(profile, "123456", is_account_created=True)
            print("OTP verified successfully.")
        except HttpError as e:
            print(f"OTP verification failed: {e.detail}")

    Notes:
        - Ensure the `profile_obj` is a valid and existing profile instance.
        - This function modifies the `is_active` status of the profile and the `is_used`
          status of the OTP record.
    """
    if is_account_created:
        otp_type = OtpType.SIGN_UP_OTP
    elif is_two_factor:
        otp_type = OtpType.TWO_FACTOR_OTP
    else:
        otp_type = OtpType.SIGN_IN_OTP

    otp_history = check_otp(profile_obj, otp, otp_type)

    if is_account_created:
        profile_obj.is_active = True
        profile_obj.save()

    otp_history.is_used = True
    otp_history.save()


def get_user_role(profile_obj=None, user=None):
    if user is not None:
        return Profile.objects.filter(user=user).first().role.name
    return profile_obj.role.name
