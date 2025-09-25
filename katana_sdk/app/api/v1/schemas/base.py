from typing import Optional, List
from enum import IntEnum
from pydantic import constr, Field, model_validator, field_validator
from ninja.errors import HttpError
from http import HTTPStatus
from ninja import Schema, ModelSchema
from datetime import date

base_exclusion_list = [
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
    "reason_to_deactivate",
    "last_deactivated_at",
]

reason_to_deactivate_msg = "A reason must be provided to deactivate selected records."


class Base(Schema):
    """
    Base schema for identifying instances.

    This class defines the basic structure for identifying a particular instance in the system,
    using an ID field.

    Attributes:
        id (int): The unique identifier of a particular instance. Defaults to `None`.
    """

    id: int = Field(description="ID of Particular Instance", default=None)


class CategoryBaseOut(Base):
    name: str = Field(description="Name of the category")


def validate_attributes(cls, values):
    reason_to_deactivate = getattr(values, "reason_to_deactivate", None)

    if not hasattr(values, "ids"):
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Ids are mandatory field.")

    ids = getattr(values, "ids")
    if not isinstance(ids, list):
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Ids must be of list type.")

    if not ids:
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Ids list cannot be empty.")

    if not hasattr(values, "is_active"):
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY, "The 'is_active' field is required."
        )

    is_active = getattr(values, "is_active", False)

    if is_active:
        if reason_to_deactivate:
            raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Reason is not required ")

    else:
        if not reason_to_deactivate:
            raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, reason_to_deactivate_msg)

    return values


class ActionBase(Schema):
    """
    A base schema for actions that involve a list of IDs and an active status.

    Attributes:
        ids (List): A list of identifiers associated with the action.
                    This could represent resources or entities being affected by the action.
        is_active (bool): A flag indicating whether the action is active or inactive.

    This schema is used as a foundation for actions or operations that require
    tracking a set of IDs and whether the action should be considered active.
    It can be extended or used directly in cases where these two properties are needed.
    """

    ids: List[int]
    is_active: bool
    reason_to_deactivate: Optional[str] = Field(
        default=None, description="why you want to deactivate."
    )

    _validate_attributes = model_validator(mode="before")(validate_attributes)


class UserBase(Schema):
    """
    A base schema for representing basic user information.

    Attributes:
        first_name (Optional[str]): The user's first name. This field is optional.
        last_name (Optional[str]): The user's last name. This field is optional.
        email (Optional[str]): The user's email address. This field is optional.

    This schema is used to store and validate basic user information. It can be extended
    or used directly to handle user-related data, such as when creating or updating user profiles.
    The fields are optional, allowing for flexibility in partial data submissions.
    """

    username: str


class UserRoleBase(Schema):
    """
    A base schema for representing a user's role.

    Attributes:
        id (int): The unique identifier for the user role.
        name (str): The name of the user role, such as "Admin", "User", or "Editor".

    This schema is used to represent basic information about a user role. It can be used
    to manage and validate user roles in the system, including assigning or updating roles.
    The `id` field is typically used to uniquely identify the role, while the `name` field
    represents the role's designation.
    """

    id: int
    name: str


class DateEnum(IntEnum):
    """
    An enumeration representing different time periods based on days.

    This enum is used to define common time intervals for filtering or date-related operations,
    such as retrieving data for the last day, week, month, quarter, or year.

    Attributes:
        LAST_DAY (int): Represents the last day (1 day).
        LAST_WEEK (int): Represents the last week (7 days).
        LAST_MONTH (int): Represents the last month (30 days).
        LAST_QUARTER (int): Represents the last quarter (90 days).
        LAST_YEAR (int): Represents the last year (365 days).

    Each of these values corresponds to the number of days in the respective time period.
    """

    LAST_DAY = 1
    LAST_WEEK = 7
    LAST_MONTH = 30
    LAST_QUARTER = 90
    LAST_YEAR = 365


class BaseFilters(Schema):
    is_active: Optional[bool] = Field(default=None, description="active status filter")
    created_at_from: Optional[DateEnum] = Field(
        default=None, description="created at from date"
    )
    updated_at_from: Optional[DateEnum] = Field(
        default=None, description="updated at from date"
    )
    start_date: Optional[date] = Field(
        default=None, description="created at start date"
    )
    end_date: Optional[date] = Field(default=None, description="created at end date")


class BaseOut(Base):
    name: str
