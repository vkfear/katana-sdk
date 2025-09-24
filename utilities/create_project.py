

import os
import argparse
from django.core.management import call_command
import django

def create_django_project(project_name: str):
    try:
        
        if not os.path.exists(project_name):
            os.makedirs(project_name)

        
        call_command("startproject", "config", project_name)

        print(f" Django project '{project_name}' created successfully!")

    except Exception as e:
        print(f"Error while creating project: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=" new Django project with an inner 'config' folder."
    )
    parser.add_argument(
        "project_name",
        type=str,
        help="Name of the Django project ."
    )
    args = parser.parse_args()

    create_django_project(args.project_name)
