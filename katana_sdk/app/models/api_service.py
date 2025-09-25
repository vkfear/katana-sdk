from django.db import models
from .base import BaseModel


class ApiService(BaseModel):
    """
    This class represents an API service within the application.
    It is used to manage and track different API services that the application interacts with.

    Attributes:
        code_name (models.CharField): A unique identifier for the API service.
            This is a string field with a maximum length of 255 characters.
        is_active (models.BooleanField): A boolean flag indicating whether the API service
            is currently active or not. Defaults to False.

    Methods:
        __str__(self): Provides a string representation of the ApiService instance.
            This representation includes the `code_name` of the service.

    Meta:
        db_table (str): Specifies the name of the database table ('api_service')
            used for storing ApiService records. This is used by the ORM to map the class to the database.

    Example:
        >>> api_service = ApiService(code_name="WeatherAPI", is_active=True)
        >>> str(api_service)
        'WeatherAPI'
    """

    code_name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code_name}"

    class Meta:
        db_table = "api_service"
