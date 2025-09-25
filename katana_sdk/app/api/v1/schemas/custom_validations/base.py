import re
import os
import logging
from django.core.exceptions import ValidationError
from ninja.errors import HttpError
from http import HTTPStatus
from datetime import datetime
from django.core.validators import URLValidator
from typing import List


def required_field(field, field_name):
    """
    Check if a field is required.

    Args:
        field: The field to check.
        field_name (str): The name of the field for error message.

    Raises:
        HttpError: If the field is None or an empty string.
    """
    if field is None or (isinstance(field, str) and field.strip() == ""):
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, f"{field_name} is required.")


def validate_length(
    value, field_name, is_required: bool = True, min_length=None, max_length=None
):
    if is_required:
        required_field(value, field_name)
    # to validate length of value
    if value:
        if max_length and len(value) > max_length:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY, f"{field_name} exceeds character limit"
            )

        if min_length and len(value) < min_length:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"{field_name} should have at least {min_length} character",
            )


def is_numeric_only(
    value, field_name, is_required: bool = True, without_spaces: bool = False
):
    if is_required:
        required_field(value, field_name)
    # to check if value is only numeric or not
    pattern = r"^[0-9\s]+$"
    msg = f"In {field_name}, enter numbers."

    if without_spaces:
        pattern = r"^\d+$"
        msg = f"In {field_name}, enter numbers only, No spaces."

    if value:
        if not re.match(pattern, str(value)):
            raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, msg)


def validate_bool_type(value, field_name, is_required: bool = True):
    if is_required:
        required_field(value, field_name)

    if value:
        if not isinstance(value, bool):
            if value in ("true", "1", "True"):
                return True
            if value in ("False", "false", "0"):
                return False
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"{field_name} field should be boolean.",
            )


def validate_float_type(value, field_name, is_required: bool = True):
    if is_required:
        required_field(value, field_name)

    if value:
        try:
            return float(value)
        except Exception as e:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"{field_name} field should be float.",
            )


def is_alphabetic_only(
    value, field_name, is_required: bool = True, without_spaces: bool = False
):
    if is_required:
        required_field(value, field_name)
    # to check if value is only numeric or not
    pattern = r"^[a-zA-Z\s]+$"
    msg = f"In {field_name}, enter alphabets only."

    if without_spaces:
        pattern = r"^[a-zA-Z]+$"
        msg = f"In {field_name}, enter alphabets only, no spaces."

    if value:
        if not re.match(pattern, value):
            raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, msg)


def is_alphanumeric(
    value, field_name, is_required: bool = True, without_spaces: bool = False
):
    if is_required:
        required_field(value, field_name)
    # to check if value is only numeric or not
    pattern = r"^(?=.*\d)[A-Za-z0-9\s]+$"
    msg = f"In {field_name}, alphanumeric characters only."

    if without_spaces:
        pattern = r"^(?=.*\d)[A-Za-z0-9]+$"
        msg = f"In {field_name}, alphanumeric characters only, no spaces."

    if value:
        if not re.match(pattern, value):
            raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, msg)


def check_file_size(file_path):
    # to check file size, can't more than 4mb
    file_size = os.path.getsize(file_path)

    # convert bytes into mb
    file_size_in_mb = file_size / (1024 * 1024)

    if file_size_in_mb >= 4:
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Max file size is 4 MB.")


def valid_file_formats(file_path, list_of_valid_file_formats):
    # to check valid file formats
    _, file_format = os.path.splitext(file_path)

    if file_format.lower() not in valid_file_formats:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "Invalid file format. Accepted formats: ".join(list_of_valid_file_formats),
        )


def pwd_match(pwd, c_pwd):
    if pwd != c_pwd:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "Passwords do not match.",
        )


def validate_email(email, is_required=True):
    """
    Validate an email address.

    Args:
        email (str): The email address to validate.

    Returns:
        str: The validated email address.

    Raises:
        HttpError: If the email is missing or invalid.
    """
    if is_required:
        required_field(email, "Email")

    if email:
        if not re.match(r"^[\w\.-]+[+]{0,1}[\w\.-]+@[\w\.-]+$", email):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "Invalid email input.",
            )

        if len(email) > 254:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "Email address is too long. It should be 254 characters or less.",
            )


def validate_int_list(value, field_name, is_required=True):
    if is_required:
        required_field(value, field_name)

    if value:
        if not isinstance(value, list):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"{field_name} must be a list.",
            )

        if not all(isinstance(item, int) for item in value):
            try:
                [int(i) for i in value]
            except Exception as e:
                raise HttpError(
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    f"All elements in {field_name} must be integers.",
                )

        if len(value) != len(set(value)):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"Some duplicate {field_name} IDs found.",
            )


def validate_dict_list(value, field_name, is_required=True):
    if is_required:
        required_field(value, field_name)

    if not isinstance(value, list):
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            f"{field_name} must be a list.",
        )

    if not all(isinstance(item, dict) for item in value):
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            f"All items in '{field_name}' must be dictionaries.",
        )


def validate_contact_number(value, field_name, is_required: bool = True):
    if is_required:
        required_field(value, field_name)

    if value:
        contact_number = re.sub(r"\s", "", value)
        # Additional validation if needed
        if not re.match(r"^\d+$", contact_number):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"Invalid {field_name} format.",
            )


def validate_address(value, field_name, is_required: bool = True):
    if is_required:
        required_field(value, field_name)

    if value:
        address_pattern = (
            r"^[a-zA-z0-9]{1,250}[.&,()/\ -]{0,}[a-zA-z.0-9&,()/\ -]{1,250}$"
        )
        if not re.match(address_pattern, value):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"Invalid {field_name} format.",
            )


def validate_str_with_comma(value, field_name, is_required: bool = True):
    if is_required:
        required_field(value, field_name)

    if value:
        str_pattern = r"^[a-zA-Z\s,',]+$"
        if not re.match(str_pattern, value):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"Invalid {field_name} format.",
            )


def validate_delivery_mode_for_hospital(values):
    is_delivery_by_fax = getattr(values, "is_delivery_by_fax", False)
    is_delivery_by_mail = getattr(values, "is_delivery_by_mail", False)
    fax_number = getattr(values, "fax_number", None)
    delivery_email = getattr(values, "delivery_email", None)

    if is_delivery_by_fax is None:
        values.is_delivery_by_fax = False

    if is_delivery_by_mail is None:
        values.is_delivery_by_mail = False

    if not is_delivery_by_fax and not is_delivery_by_mail:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "At least one delivery mode should be selected!",
        )

    if is_delivery_by_fax and fax_number is None:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "Fax number is required as you have selected fax as delivery mode!",
        )

    if is_delivery_by_mail and delivery_email is None:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "Delivery email is required as you selected mail as delivery mode!",
        )


def validate_delivery_mode_for_laboratory(values):
    is_delivery_by_fax = getattr(values, "is_delivery_by_fax", False)
    is_delivery_by_health_link = getattr(values, "is_delivery_by_health_link", False)
    is_delivery_mail = getattr(values, "is_delivery_mail", False)
    is_delivery_by_web_link = getattr(values, "is_delivery_by_web_link", False)

    fax_number = getattr(values, "fax_number", None)
    health_link = getattr(values, "health_link", None)
    delivery_email = getattr(values, "delivery_email", None)
    web_link = getattr(values, "web_link", None)

    if is_delivery_by_fax is None:
        values.is_delivery_by_fax = False

    if is_delivery_by_health_link is None:
        values.is_delivery_by_health_link = False

    if is_delivery_mail is None:
        values.is_delivery_by_mail = False

    if is_delivery_by_web_link is None:
        values.is_delivery_by_web_link = False

    if (
        not is_delivery_by_fax
        and not is_delivery_by_health_link
        and not is_delivery_mail
        and not is_delivery_by_web_link
    ):
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "At least one delivery mode should be selected!",
        )

    if is_delivery_by_fax and fax_number is None:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "Fax number is required as you have selected fax as delivery mode!",
        )

    if is_delivery_by_health_link and health_link is None:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "Health link is required as you selected health link as delivery_mode!",
        )

    if is_delivery_mail and delivery_email is None:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "Delivery email is required as you selected mail as delivery_mode!",
        )

    if is_delivery_by_web_link and web_link is None:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "Web link is required as you selected is_delivery_by_mail as delivery_mode!",
        )


def validate_string_with_data(value, field_name, is_required: bool = True):
    if is_required:
        required_field(value, field_name)

    if value:
        str_pattern = r"^[a-zA-z0-9]{1,100}[.&,()/\ -]{0,}[a-zA-z.0-9&,()/\ -]{1,250}$"
        if not re.match(str_pattern, value):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"Invalid {field_name} format.",
            )


def is_date_string(s, date_format="%Y-%m-%d"):
    """Check if the string `s` is a valid date.

    Args:
        s (str): The string to check.
        date_format (str, optional): The format to attempt parsing the string with. Defaults to "%Y-%m-%d".

    Returns:
        bool: True if `s` is a valid date string according to `date_format`, False otherwise.
    """
    try:
        datetime.strptime(s, date_format)
        return True
    except ValueError:
        return False


def validate_date_type(value, field_name, is_required: bool = True):
    if is_required:
        required_field(value, field_name)

    if value:
        if not is_date_string(value):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"Invalid {field_name} format.",
            )


def validate_dob(value: str, field_name: str = "DOB", is_required: bool = True):
    if is_required:
        required_field(value, field_name)

    if value:
        if not is_date_string(value):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"Invalid {field_name} format.",
            )

        try:
            dob_date = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"Invalid {field_name} format. Expected YYYY-MM-DD.",
            )

        today = datetime.today().date()
        age = (today - dob_date).days // 365

        if age < 18:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"{field_name} must indicate age of at least 18 years.",
            )

        if age > 100:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"{field_name} cannot be older than 100 years.",
            )


def empty_string_checker(value):
    if not value.strip():
        return None
    return value


def split_list(target_list):
    try:
        if len(target_list) == 1 and "," in target_list[0]:
            list_values = [value for value in target_list[0].split(",") if value != ""]
        else:
            # Remove empty strings from list_values if it's not necessary to split
            list_values = [value for value in target_list if value != ""]

        return list_values
    except Exception as e:
        return target_list


def validate_location(cls, user_lat, user_long, is_required=True):
    # Convert latitude and longitude to float
    validate_float_type(user_lat, "Latitude", is_required)
    validate_float_type(user_long, "Longitude", is_required)

    if is_required:
        # Validate latitude
        if not (-90 <= user_lat <= 90):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY, "Latitude must be between -90 and 90."
            )
        # Validate longitude
        if not (-180 <= user_long <= 180):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "Longitude must be between -180 and 180.",
            )

    return True


def is_int_type(value, field_name, is_required: bool = True):
    if is_required:
        required_field(value, field_name)
    if not isinstance(value, int):
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY, f"{field_name} is not of int type"
        )


def validate_int_size(
    value, field_name, is_required: bool = True, min_size=None, max_size=None
):
    if is_required:
        required_field(value, field_name)

    if value:
        if max_size and value > max_size:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"{field_name} exceeds {max_size} value",
            )

        if min_size and value < min_size:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"{field_name} should have at least {min_size} size",
            )


def validate_float_size(
    value: float,
    field_name: str,
    is_required: bool = True,
    min_size: float = None,
    max_size: float = None,
):
    if is_required:
        required_field(value, field_name)

    if value is not None:
        if max_size and value > max_size:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"{field_name} exceeds {max_size} value",
            )

        if min_size and value < min_size:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"{field_name} should have at least {min_size} size",
            )


def is_valid_url(value, field_name, is_required: bool = True):
    if is_required:
        required_field(value, field_name)

    validate = URLValidator()
    if value:
        try:
            validate(value)
        except ValidationError:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY, f"{field_name} url is not valid"
            )


def validate_code_names(value: list[str], field_name, is_required: bool = True):
    if is_required and not value:
        raise HttpError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            f"{field_name} list should have at least one entry.",
        )

    pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    for name in value:
        if not isinstance(name, str) or not pattern.match(name):
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY, f"Some of code names are not valid."
            )
