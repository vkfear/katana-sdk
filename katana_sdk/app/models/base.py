from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class BaseModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s_created_by",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by",
    )
    reason_to_deactivate = models.CharField(max_length=151, null=True, blank=True)
    last_deactivated_at = models.DateTimeField(blank=True, null=True)

    def update_model_object(self, user, payload, is_update=True):
        """
        to update model object instance fields

        Params:
            user: requested user
            payload: Data in dict format to update
        """
        for attr, value in payload.items():
            setattr(self, attr, value)

        if is_update:
            self.updated_at = timezone.now()
            self.updated_by = user

        self.clean()
        self.save()

    class Meta:
        abstract = True
