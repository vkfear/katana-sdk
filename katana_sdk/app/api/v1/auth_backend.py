from http import HTTPStatus

from django.core.exceptions import ObjectDoesNotExist
from ninja.security import HttpBearer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from ninja.errors import HttpError

from app.models import BlackListedToken, UserRole, UserType, Profile
from django.shortcuts import get_object_or_404
from functools import wraps

# from app.api.accessibility.base import logger
from user_agents import parse


class NinjaAuthBearer(HttpBearer):
    """Adapter for django-ninja"""

    def __init__(self, code_name=None):
        super().__init__()

    def authenticate(self, request, token: str):
        """
        to authenticate user login request
        it will validate access_token - access_token in headers
        raise exception if token is in BlackListedToken db table else it will authenticate user as per user roles and access of apis
        """
        # jwt_auth = JWTAuthentication()
        self.check_blacklisted_token(token)
        try:
            response = self.validate_jwt_token(request)
            request.user = response[0]
            request.user_id = response[1]["role_id"]
            request.user_role = response[1]["role_name"]
            request.logged_in = True
            return True
        except AuthenticationFailed:
            return None

    def validate_jwt_token(self, request):
        # to validate token
        jwt_auth = JWTAuthentication()
        return jwt_auth.authenticate(request)

    def check_blacklisted_token(self, token: str):
        # to check whether token is blacklisted or not
        if BlackListedToken.objects.filter(token=token).exists():
            raise HttpError(HTTPStatus.UNAUTHORIZED, "Token is expired.")


def token_auth():
    """
    To validate user based on role and role specific flag
    """
    return NinjaAuthBearer()


def validate_role_for_service_access(func):
    """
    Decorator to enforce role-based access control for services. This function checks if the
    user's role allows access to a specific service, and whether that service is active.

    Parameters:
        func (callable): The Django view function to wrap.

    Raises:
        HttpResponseForbidden: If the service is not accessible by the user based on their role or if the service is
        not active.

    Returns:
        callable: The wrapped view function that is only called if the user has the appropriate access rights.
    """

    @wraps(func)
    # decorator to get function name
    def wrapper(request, *args, **kwargs):
        user_role = request.user_role
        code_name = func.__name__

        user_role = get_object_or_404(UserRole, name=user_role)
        query = user_role.services.filter(code_name=code_name, is_active=True)

        codename_exist = query.exists()
        if codename_exist:
            validate_device_type_with_geo_fencing(request, user_role.name, **kwargs)
            return func(request, *args, **kwargs)
        else:
            raise HttpError(HTTPStatus.FORBIDDEN, "This service is not accessible.")

    return wrapper


def validate_device_type_login(func):
    """
    Decorator to validate the device type when logging in. This is particularly used to ensure
    that certain user roles are accessing the API from a mobile device as required.

    Parameters:
        func (callable): The Django view function to wrap.

    Returns:
        callable: The wrapped view function.
    """

    @wraps(func)
    # decorator to get function name
    def wrapper(request, *args, **kwargs):
        validate_device_type_with_geo_fencing(request, None, **kwargs)
        return func(request, *args, **kwargs)

    return wrapper


def validate_device_type_with_geo_fencing(request, user_role=None, **kwargs):
    """
    Function to validate device type based on user-agent and apply geo-fencing based on the user's
    role and current location. It ensures that certain roles are accessing the API from the
    correct device type and within a specified geographic radius.

    Parameters:
        request: The HTTP request object containing user and device details.
        user_role: Optional; the user role to check for specific access requirements.
        **kwargs: Additional keyword arguments.

    Raises:
        HttpResponseForbidden: If the user's role requires mobile access but the User-Agent
        indicates the request is not from a mobile device.
        Http404: If no active profile is found for the provided email address.
    """
    if hasattr(request, "logged_in") and request.logged_in:
        email = request.user.username
    else:
        email = kwargs["payload"].email

    profile_obj = fetch_user_profile(email)
    request.META["profile_obj"] = profile_obj
    request.META["user_role"] = profile_obj.role.name
    # user_role = user_role or profile_obj.role.name


def fetch_user_profile(email):
    """
    Fetches the active user profile based on the email address from the request. Ensures that the user
    exists and the profile is active.

    Parameters:
        email (str): The email address of the user.

    Raises:
        HttpError: If no active profile is found, or if any unexpected error occurs.
    """
    try:
        return Profile.objects.get(user__username__iexact=email, is_active=True)
    except ObjectDoesNotExist as e:
        # logger.error(
        #     f"Unexpected error during identifying for the user {email}: {str(e)}",
        #     exc_info=True,
        # )
        raise HttpError(
            HTTPStatus.NOT_FOUND,
            "We can’t find an account for that email address.",
        )


def validate_user_agent(request, user_role):
    """
    Validates the user agent of the request to ensure that certain user roles are accessing the API
    from a mobile device. This is particularly important for roles that require mobility, such as
    nurses or couriers.

    Parameters:
        request: The HTTP request object which includes the User-Agent header.
        user_role (str): The role of the user which determines if mobile access is mandatory.

    Raises:
        HttpError: If the user's role requires mobile access but the User-Agent indicates the
                   request is not from a mobile device, or if the User-Agent parsing fails.

    Usage:
        This function should be used in scenarios where mobile access is a requirement for
        certain user roles, enhancing security and functionality by enforcing device-based access control.
    """
    try:
        user_agent_string = request.headers.get("User-Agent", None)
        user_agent = parse(user_agent_string)
        if (
            user_role in [UserType.NURSE, UserType.OT_ADMIN, UserType.COURIER]
            and not user_agent.is_mobile
        ):
            raise HttpError(
                HTTPStatus.FORBIDDEN,
                "Access restricted to mobile devices only.",
            )
    except Exception as e:
        raise HttpError(
            HTTPStatus.FORBIDDEN,
            "Access restricted to mobile devices only.",
        )
