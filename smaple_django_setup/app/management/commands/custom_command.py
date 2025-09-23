import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate model, api, schema, validation, and accessibility files"

    def add_arguments(self, parser):
        parser.add_argument(
            "model_name", type=str, help="Name of the model class (e.g., Book)"
        )
        parser.add_argument("file_name", type=str, help="Base file name (e.g., book)")

    def handle(self, *args, **options):
        model_name = options["model_name"]
        file_name = options["file_name"]

        # Base app name where files will be created
        base_app = "app"

        # Directories
        folders = {
            "models": os.path.join(base_app, "models"),
            "api": os.path.join(base_app, "api"),
            "v1": os.path.join(base_app,"api","v1"),
            "accessibility": os.path.join(base_app,"api","accessibility"),
            "schemas": os.path.join(base_app, "api","v1","schemas"),
            "custom_validations": os.path.join(base_app,"api","v1","schemas","custom_validations"),

        }

        # Ensure directories exist
        for folder in folders.values():
            os.makedirs(folder, exist_ok=True)

        # File paths
        files_to_create = {
            "model": os.path.join(folders["models"], f"{file_name}.py"),
            "v1": os.path.join(folders["v1"], f"{file_name}.py"),
            "schema": os.path.join(folders["schemas"], f"{file_name}.py"),
            "validation": os.path.join(folders["custom_validations"], f"{file_name}.py"),
            "accessibility": os.path.join(folders["accessibility"], f"{file_name}.py"),
        }

        # Model file content
        model_content = f"""from django.db import models


class {model_name}(models.Model):
    pass
"""

        
        empty_content = "# Auto-generated file\n"
 
        created_files = []

        for key, path in files_to_create.items():
            if key == "model":
                content = model_content
            else:
                content = empty_content

            # Create or overwrite the file
            with open(path, "w") as f:
                f.write(content)
            created_files.append(path)

        # Print final result
        self.stdout.write(self.style.SUCCESS("Files created:"))
        for f in created_files:
            self.stdout.write(f"    {f}")
import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate model, api, schema, validation, and accessibility files"

    def add_arguments(self, parser):
        parser.add_argument(
            "model_name", type=str, help="Name of the model class (e.g., Book)"
        )
        parser.add_argument("file_name", type=str, help="Base file name (e.g., book)")

    def handle(self, *args, **options):
        model_name = options["model_name"]
        file_name = options["file_name"]

        # Base app name where files will be created
        base_app = "app"

        # Directories
        folders = {
            "models": os.path.join(base_app, "models"),
            "api": os.path.join(base_app, "api"),
            "v1": os.path.join(base_app,"api","v1"),
            "accessibility": os.path.join(base_app,"api","accessibility"),
            "schemas": os.path.join(base_app, "api","v1","schemas"),
            "custom_validations": os.path.join(base_app,"api","v1","schemas","custom_validations"),

        }

        # Ensure directories exist
        for folder in folders.values():
            os.makedirs(folder, exist_ok=True)

        # File paths
        files_to_create = {
            "model": os.path.join(folders["models"], f"{file_name}.py"),
            "v1": os.path.join(folders["v1"], f"{file_name}.py"),
            "schema": os.path.join(folders["schemas"], f"{file_name}.py"),
            "validation": os.path.join(folders["custom_validations"], f"{file_name}.py"),
            "accessibility": os.path.join(folders["accessibility"], f"{file_name}.py"),
        }

        # Model file content
        model_content = f"""from django.db import models


class {model_name}(models.Model):
    pass
"""

        
        empty_content = "# Auto-generated file\n"
 
        created_files = []

        for key, path in files_to_create.items():
            if key == "model":
                content = model_content
            else:
                content = empty_content

            # Create or overwrite the file
            with open(path, "w") as f:
                f.write(content)
            created_files.append(path)

        # Print final result
        self.stdout.write(self.style.SUCCESS("Files created:"))
        for f in created_files:
            self.stdout.write(f"    {f}")
import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate model, api, schema, validation, and accessibility files"

    def add_arguments(self, parser):
        parser.add_argument(
            "model_name", type=str, help="Name of the model class (e.g., Book)"
        )
        parser.add_argument("file_name", type=str, help="Base file name (e.g., book)")

    def handle(self, *args, **options):
        model_name = options["model_name"]
        file_name = options["file_name"]

        # Base app name where files will be created
        base_app = "app"

        # Directories
        folders = {
            "models": os.path.join(base_app, "models"),
            "api": os.path.join(base_app, "api"),
            "v1": os.path.join(base_app,"api","v1"),
            "accessibility": os.path.join(base_app,"api","accessibility"),
            "schemas": os.path.join(base_app, "api","v1","schemas"),
            "custom_validations": os.path.join(base_app,"api","v1","schemas","custom_validations"),

        }

        # Ensure directories exist
        for folder in folders.values():
            os.makedirs(folder, exist_ok=True)

        # File paths
        files_to_create = {
            "model": os.path.join(folders["models"], f"{file_name}.py"),
            "v1": os.path.join(folders["v1"], f"{file_name}.py"),
            "schema": os.path.join(folders["schemas"], f"{file_name}.py"),
            "validation": os.path.join(folders["custom_validations"], f"{file_name}.py"),
            "accessibility": os.path.join(folders["accessibility"], f"{file_name}.py"),
        }

        # Model file content
        model_content = f"""from django.db import models


class {model_name}(models.Model):
    pass
"""

        
        empty_content = "# Auto-generated file\n"
 
        created_files = []

        for key, path in files_to_create.items():
            if key == "model":
                content = model_content
            else:
                content = empty_content

            # Create or overwrite the file
            with open(path, "w") as f:
                f.write(content)
            created_files.append(path)

        # Print final result
        self.stdout.write(self.style.SUCCESS("Files created:"))
        for f in created_files:
            self.stdout.write(f"    {f}")
