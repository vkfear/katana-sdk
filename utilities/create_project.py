
import os
import sys
import subprocess

def create_django_project(project_name):
    try:
        if not os.path.exists(project_name):
            os.makedirs(project_name)
            
        subprocess.run(
            ["django-admin", "startproject", "config", project_name],
            check=True
        )
        print(f" Django project '{project_name}' created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error while creating project: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python utilities/create_project.py <project_name>")
    else:
        project_name = sys.argv[1]
        create_django_project(project_name)
