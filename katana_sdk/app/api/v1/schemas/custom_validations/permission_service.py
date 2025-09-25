from .base import *


def api_service_validate_attributes(cls, values):
    code_names = getattr(values, "code_names", None)
    validate_code_names(code_names, "Code name", is_required=False)

    return values
