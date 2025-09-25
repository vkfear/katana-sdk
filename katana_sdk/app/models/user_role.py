from django.db import models
from .base import BaseModel
from .api_service import ApiService


class UserType(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    CONTNET_MANAGER = "CONTNET_MANAGER", "Content Manager"
    NORMAL_USER = "NORMAL_USER", "Normal User"


class UserRole(BaseModel):

    name = models.CharField(max_length=30, choices=UserType.choices, unique=True)
    services = models.ManyToManyField(ApiService, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = "user_role"
