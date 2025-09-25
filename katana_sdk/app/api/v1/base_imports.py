from http import HTTPStatus
from django.utils import timezone
from ninja import Header
from django.db.utils import IntegrityError
from django.db import transaction

# from app.api.accessibility.base import logger
from .router import router
from .auth_backend import token_auth, validate_role_for_service_access
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.db.models import Q
from django.core.exceptions import ValidationError
from app.models import UserType
from django.shortcuts import get_object_or_404
from ninja.decorators import decorate_view
from datetime import datetime
from django.db import transaction
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja import Query
from typing import List
