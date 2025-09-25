from django.core.management.base import BaseCommand, CommandError
from app.models import UserRole, UserType

# from app.api.accessibility.base import logger


class Command(BaseCommand):
    help = "This command will get or create UserRole in database."

    def handle(self, *args, **kwargs):
        # to add user types in the database
        try:
            UserRole.objects.get_or_create(name=UserType.ADMIN)
            UserRole.objects.get_or_create(name=UserType.MANAGER)
            UserRole.objects.get_or_create(name=UserType.TECHNICIAN)
            UserRole.objects.get_or_create(name=UserType.NORMAL_USER)
            UserRole.objects.get_or_create(name=UserType.FIELD_RELATIONSHIP_MANAGER)
            self.stdout.write(self.style.SUCCESS("User Roles added successfully."))
        except Exception as e:
            # logger.error(str(e))
            raise CommandError(f"error: {str(e)}")
