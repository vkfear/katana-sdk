from app.api.v1.base_imports import *
from app.api.utils.send_html_email import send_email
from app.models.email_template import EmailType
from .html_style_contants import EMAIL_STYLES


def send_sign_up_otp_mail(to_mail, data_dict):
    context = {**EMAIL_STYLES, "name": to_mail, "otp": data_dict["otp"]}
    send_email(event_type=EmailType.SIGNUP_OTP, to_email=to_mail, context=context)


def send_sign_in_otp_mail(to_mail, data_dict):
    context = {**EMAIL_STYLES, "name": to_mail, "otp": data_dict["otp"]}
    send_email(event_type=EmailType.LOGIN_OTP, to_email=to_mail, context=context)


def send_forgot_mail(to_mail, data_dict):
    context = {
        **EMAIL_STYLES,
        "name": to_mail,
        "name": data_dict["name"],
        "otp": data_dict["otp"],
    }
    send_email(event_type=EmailType.FORGOT_PASSWORD, to_email=to_mail, context=context)


def send_sign_up_or_sign_in_email(to_mail, is_created, data_dict):
    if is_created:
        send_sign_up_otp_mail(to_mail=to_mail, data_dict=data_dict)
    else:
        send_sign_in_otp_mail(to_mail=to_mail, data_dict=data_dict)
