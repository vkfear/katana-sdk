from app.models import Profile, UserRole

import logging

logger = logging.getLogger("db")


def get_user_role_name(user) -> str:
    """
    Retrieves the role name of a given user. This is useful for role-based access
    control throughout the application.

    Args:
        user: User object to find the lab ID for.
    Returns:
        user_role: Role of the user.
    """
    return Profile.objects.get(user=user).role.name


def get_user_role_obj_by_name(role_name) -> UserRole:
    """
    Retrieves the UserRole object based on a role name. This can be
    used when you need the actual UserRole object instead of just the name.

    Args:
        role_name: user_role name - string
    Returns:
        user_role: user_role object
    """
    return UserRole.objects.get(name=role_name)
