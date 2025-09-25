import time

from django.utils.deprecation import MiddlewareMixin
from moto.efs.urls import response

from app.models import APILog
import ast
import json


def dict_converter(data):
    try:
        result = ast.literal_eval(data)
    except (ValueError, SyntaxError):
        result = [data]
    return result


class RequestResponseLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs the details of HTTP requests and responses for debugging and monitoring purposes.

    This middleware intercepts incoming HTTP requests and outgoing responses, logging important
    information such as request method, URL, headers, body content (with sensitive information masked),
    and the response status and body. The logged data is stored in a database model `APILog` for later analysis.

    Attributes:
        log_dict (dict or None): A dictionary that holds the log data for the current request.
        start_time (float or None): The timestamp when the request was received, used to calculate the response time.

    Methods:
        process_request(request): Processes the incoming request, extracting relevant data (headers, body, etc.).
        process_response(request, response): Processes the outgoing response, calculating the response time
                                              and logging the response status, body, and time taken.
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.log_dict = None
        self.start_time = None

    def process_request(self, request):

        self.start_time = time.time()
        excluded_paths = ["/admin/", "swagger/", "/api/v1/docs", "openapi.json"]
        self.log_dict = None

        if any(excluded_path in request.path for excluded_path in excluded_paths):
            return None

        log_dict = dict()
        log_dict["method"] = request.method
        log_dict["path"] = request.path
        log_dict["query_params"] = request.GET.urlencode()

        content_type = request.content_type
        log_dict["content_type"] = content_type
        if content_type == "application/json":
            if request.body:
                body = request.body.decode("utf-8")
                data = json.loads(body)
                for key in data:
                    if "password" in key.lower():
                        data[key] = "*****"

                    if "refresh" in key.lower():
                        data[key] = "*****"

                updated_body = json.dumps(data)
                log_dict["request_body"] = dict_converter(updated_body)
        elif content_type.startswith("multipart/form-data"):
            # Handle form-data
            if request.POST:
                log_dict["request_body"] = dict_converter(request.POST)
            if request.FILES:
                log_dict["request_files_info"] = []
                for f in request.FILES.values():
                    file_dict = dict()
                    file_dict["file_name"] = f.name
                    file_dict["file_size"] = f.size
                    log_dict["request_files_info"].append(file_dict)
        elif content_type == "application/x-www-form-urlencoded":
            # Handle URL-encoded form data
            if request.POST:
                log_dict["request_body"] = dict_converter(request.POST)

        self.log_dict = log_dict

        return None

    def process_response(self, request, response):
        if self.log_dict is None:
            return response

        log_dict = self.log_dict
        log_dict["status_code"] = response.status_code
        response_content_type = response.get("Content-Type", "")
        if "application/json" in response_content_type:
            response_content = response.content.decode("utf-8")

        else:
            response_content = "Response may be in file."

        log_dict["response_body"] = (
            dict_converter(response_content) if response.content else None
        )
        response_time_ms = (time.time() - self.start_time) * 1000
        log_dict["response_time_ms"] = round(response_time_ms, 2)

        if "response_body" in log_dict and log_dict["response_body"] is not None:
            if "token" in log_dict["response_body"]:
                token = log_dict["response_body"]["token"]

                if "access" in token:
                    token["access"] = "******"

                if "refresh" in token:
                    token["refresh"] = "******"

        created_by = None if request.user.is_anonymous else request.user
        query = APILog(**log_dict, created_by=created_by)
        query.save()

        self.log_dict = None
        self.start_time = None

        return response
