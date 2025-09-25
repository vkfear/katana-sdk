from http import HTTPStatus
import boto3
import os

import botocore
from botocore.exceptions import NoCredentialsError
import io

from ninja.errors import HttpError

from config import settings

S3_BASE_FOLDER = settings.S3_BASE_FOLDER


def create_s3_connection():
    """
    Creates and returns an S3 client connection using the boto3 library.

    This function establishes a connection to an S3-compatible object storage service
    (e.g., DigitalOcean Spaces) using the provided credentials and endpoint details
    from the application settings.

    Returns:
        boto3.client: An S3 client instance configured to interact with the specified
                      S3-compatible storage.

    Dependencies:
        - The function relies on the following settings:
            - settings.SPACES_ENDPOINT_URL: The endpoint URL for the S3-compatible service.
            - settings.SPACES_ACCESS_KEY: The access key for authentication.
            - settings.SPACES_SECRET_KEY: The secret key for authentication.
            - settings.SPACES_REGION_NAME: The region where the storage resides.

    Example:
        s3_client = create_s3_connection()
        response = s3_client.list_buckets()
        print(response)
    """
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.SPACES_ENDPOINT_URL,
        aws_access_key_id=settings.SPACES_ACCESS_KEY,
        aws_secret_access_key=settings.SPACES_SECRET_KEY,
        region_name=settings.SPACES_REGION_NAME,
    )
    return s3


def s3_file_upload(file, object_key, object_name):
    """
    Upload a file to an S3 bucket.

    Args:
        file: File object to upload.
        object_key: S3 object key.
        object_name: Name of the object in S3.

    Returns:
        A boolean indicating success or failure of the upload.
    """
    s3_client = create_s3_connection()
    bucket_name = settings.SPACES_BUCKET_NAME
    try:
        s3_client.put_object(Bucket=settings.SPACES_BUCKET_NAME, Key=f"{object_key}/")
        with io.BytesIO(file) as file_stream:
            s3_client.upload_fileobj(file_stream, bucket_name, object_name)
        return True
    except Exception as e:
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, str(e))


def validate_upload_file_to_spaces(
    file,
    folder_path,
    file_path,
    to_upload=True,
    max_size=3,
    skip_image_validation=False,
):
    """
    Validates and optionally uploads an image file to Spaces storage.

    This function checks if the uploaded file is a valid image (based on content type) and within the
    specified maximum file size. If validation passes and `to_upload` is True, the file is uploaded
    to the designated storage path.

    Args:
        file (File): The file object to validate and optionally upload.
        folder_path (str): The storage path folder where the file will be uploaded.
        file_path (str): The complete file path for storage.
        to_upload (bool, optional): If True, uploads the file after validation. Defaults to True.
        max_size (int, optional): Maximum allowed file size in MB. Defaults to 5.
        skip_image_validation (bool, optional): If True, skips the image type validation step. Defaults to False.

    Returns:
        bool: True if the upload process is successful (when `to_upload` is True), otherwise does not return anything.

    Raises:
        HttpError: If the file is not an image, exceeds the max size, or is empty.
    """
    if not skip_image_validation:
        content_type = file.content_type
        if "image" not in content_type:
            raise HttpError(HTTPStatus.BAD_REQUEST, "Uploaded file is not image")
    if file.size > max_size * 1024 * 1024:  # 5MB limit
        raise HttpError(HTTPStatus.BAD_REQUEST, f"File must be under {max_size} MB.")
    file_content = file.read()
    if len(file_content) == 0:
        raise HttpError(HTTPStatus.BAD_REQUEST, "Uploaded file is empty")
    if to_upload:
        s3_file_upload(file_content, folder_path, file_path)


def upload_and_validate_file(
    file, sub_folder_name, obj=None, max_size=5, skip_image_validation=True
):
    """
    Validates the uploaded file for basic integrity and uploads it to a designated storage path.

    This function verifies if the uploaded file object is valid and has a non-empty name attribute.
    If the file meets these criteria, it constructs a storage path based on a base folder, the specified
    sub-folder name, and the ID of an optional related object. The file is then uploaded to this path.

    If the file is invalid (missing or empty name), an HTTP error with status 422 is raised.

    Args:
        file (UploadedFile): The file object to validate and upload.
        sub_folder_name (str): Name of the sub-folder within the storage path where the file will be uploaded.
        obj (Model Instance, optional): A model instance, expected to have an `id` attribute, used to construct
                                        the storage path. Defaults to None.
        max_size (int, optional): The maximum allowed file size in MB. Defaults to 5.

    Returns:
        str: The full path to the uploaded file in the storage system upon successful upload.

    Raises:
        HttpError: If the uploaded file is invalid or if validation fails.
    """
    if file is None:
        return None
    if not hasattr(file, "name") or not file.name:
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, "Uploaded file is corrupt.")
    else:
        if obj is not None:
            folder_path = os.path.join(S3_BASE_FOLDER, sub_folder_name, str(obj.id))
        else:
            folder_path = os.path.join(S3_BASE_FOLDER, sub_folder_name)
        file_path = os.path.join(folder_path, file.name)
        validate_upload_file_to_spaces(
            file=file,
            folder_path=folder_path,
            file_path=file_path,
            to_upload=True,
            max_size=max_size,
            skip_image_validation=skip_image_validation,
        )
        return file_path


def return_pre_signed_url(object_name, bucket_name=settings.SPACES_BUCKET_NAME):
    """
    Generates and returns a pre-signed URL for accessing an object in an S3-compatible bucket.

    This function first checks if the object exists in the bucket before generating the URL.

    Args:
        object_name (str): The key (path) of the object in the bucket.
        bucket_name (str, optional): The name of the bucket containing the object.
                                     Defaults to settings.SPACES_BUCKET_NAME.

    Returns:
        str or None: The generated pre-signed URL if the object exists, or `None` if the object
                     does not exist or an error occurs.

    Raises:
        None explicitly, but exceptions are handled internally.

    Dependencies:
        - Requires `create_s3_connection()` to establish an S3 connection.
        - The following settings must be defined:
            - settings.SPACES_BUCKET_NAME: The name of the default bucket.
            - settings.PRE_SIGNED_URL_EXPIRATION_TIME: Expiration time for the pre-signed URL.

    Example:
        url = return_pre_signed_url("example-folder/example-file.jpg")
        if url:
            print(f"Access the object using this URL: {url}")
        else:
            print("Failed to generate the pre-signed URL or object does not exist.")
    """
    try:
        if not object_name:
            return None

        s3 = create_s3_connection()

        # Check if the object exists before generating the pre-signed URL
        try:
            s3.head_object(Bucket=bucket_name, Key=object_name)
        except s3.exceptions.ClientError as e:
            return None

        # Generate the pre-signed URL only if the object exists
        pre_signed_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=settings.PRE_SIGNED_URL_EXPIRATION_TIME,
        )
        return pre_signed_url

    except Exception as e:
        return None


def s3_file_delete(file_name, bucket_name=settings.SPACES_BUCKET_NAME):
    """
    Deletes a file from an S3-compatible storage bucket.

    This function removes the specified file from the given bucket using the established
    S3 connection. It handles credential-related errors gracefully.

    Args:
        file_name (str): The key (path) of the file to be deleted from the bucket.
        bucket_name (str, optional): The name of the bucket from which the file will be deleted.
                                     Defaults to settings.SPACES_BUCKET_NAME.

    Returns:
        bool: `True` if the file deletion is successful, `False` if a `NoCredentialsError` occurs.

    Exceptions:
        The function catches `NoCredentialsError` explicitly and suppresses other exceptions
        (if required, additional exception handling can be implemented).

    Dependencies:
        - Requires `create_s3_connection()` to establish an S3 connection.
        - The following settings must be defined:
            - settings.SPACES_BUCKET_NAME: The name of the default bucket.

    Example:
        success = s3_file_delete("example-folder/example-file.jpg")
        if success:
            print("File deleted successfully.")
        else:
            print("File deletion failed.")
    """
    s3 = create_s3_connection()
    try:
        s3.delete_object(Bucket=bucket_name, Key=file_name)
        return True
    except NoCredentialsError:
        return False
