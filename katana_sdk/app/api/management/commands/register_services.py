from django.core.management.base import BaseCommand, CommandError
from app.api.v1.router import router as api_router
from app.models import ApiService


class Command(BaseCommand):
    help = "Registers all api as services."

    def handle(self, *args, **kwargs):
        """
        Handles the registration of API services.

        This method extracts the function names from the router's URLs and retrieves the OpenAPI schema.
        It then iterates over the paths in the schema, constructing a unique code name for each API service
        based on the method and the function name. Each unique service is added to a payload list, which
        is then used to bulk create or update ApiService instances in the database.

        The method ensures that all ApiService instances are marked as inactive before updating or creating
        new instances based on the payload. It also handles any exceptions that occur during the process
        and logs the error.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None: The method updates the database but does not return any value.

        Raises:
            CommandError: If an exception occurs during the process.
        """
        try:
            # Extract function names from the router's URLs
            function_names = set()
            payload = []

            for path_operations in api_router.urls:
                if isinstance(path_operations, list):
                    for pattern in path_operations:
                        code_name = pattern.name
                        if pattern.name in function_names:
                            raise ValueError(
                                f"Duplicate function name detected: {code_name}..please change function name."
                            )
                        function_names.add(code_name)
                        if "openapi" not in code_name and "root" not in code_name:
                            payload.append(
                                ApiService(code_name=pattern.name, is_active=True)
                            )

            ApiService.objects.update(is_active=False)
            ApiService.objects.bulk_create(
                payload,
                update_fields=["code_name", "is_active"],
                update_conflicts=True,
                unique_fields=["code_name"],
            )
            self.stdout.write(self.style.SUCCESS("Services registered successfully."))
        except Exception as e:
            raise CommandError(f"error: {str(e)}")
