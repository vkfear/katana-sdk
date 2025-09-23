import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http import HTTPStatus
from django.core.exceptions import ValidationError
from app.models.email_template import EmailTemplate
from app.api.v1.base_imports import *
from config import settings

logger = logging.getLogger(__name__)

EMAIL = settings.EMAIL
EMAIL_PASSWORD = settings.EMAIL_PASSWORD


def send_html_email(to_email, subject, html_content):
    """
    Sends an HTML email using SMTP.
    """
    try:
        message = MIMEMultipart("alternative")
        message["From"] = EMAIL
        message["To"] = to_email
        message["Subject"] = subject

        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, EMAIL_PASSWORD)
        server.sendmail(EMAIL, to_email, message.as_string())
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
        raise HttpError(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            message=f"Failed to send email: {str(e)}",
        )


def send_email(event_type, to_email, context):
    """
    Fetch email template, generate content, and send email.
    """
    try:
        subject, html_content = EmailTemplate.generate_email_content(
            event_type, context
        )
        send_html_email(to_email, subject, html_content)

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        raise HttpError(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, message=str(e))

    except Exception as e:
        logger.error(f"Unexpected error while sending email: {str(e)}", exc_info=True)
        raise HttpError(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            message=f"Failed to send email: {str(e)}",
        )
