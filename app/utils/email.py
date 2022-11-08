import smtplib
import ssl

from app.core.config import settings


def send_email(email_to: str, email_subject: str, email_message: str) -> None:
    """
    Send email to "receiver_email" with message_text.
    """
    if not settings.SEND_EMAILS_TO_USERS:
        return

    message = (
        f"From: {settings.EMAILS_FROM_NAME}\nSubject: {email_subject}\n{email_message}"
    )
    context = ssl.create_default_context()
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(user=settings.SMTP_USER, password=settings.SMTP_PASSWORD)
        server.sendmail(from_addr=settings.SMTP_USER, to_addrs=email_to, msg=message)


def send_new_account_email(email_to: str, fullname: str) -> None:
    """
    Send email to new user.
    """
    subject = f"{settings.PROJECT_NAME} - New Account"
    message = (
        f"You have successfully registered. Congratulations, {fullname}!\n"
        f"Go to dashboard - {settings.SERVER_HOST}"
    )
    send_email(email_to=email_to, email_subject=subject, email_message=message)


def send_reset_password_email(email_to: str, fullname: str, token: str) -> None:
    """
    Send email with temporary JWT token.
    """
    subject = f"{settings.PROJECT_NAME} - Reset Password"
    message = (
        f"We received a request to recover the password for {fullname} with email"
        f" {email_to}\nReset your password by clicking the link"
        f" below:\n{settings.SERVER_HOST}/reset-password?token={token}\nThe reset"
        " password link will expire in"
        f" {settings.EMAIL_RESET_TOKEN_EXPIRE_MINUTES} minutes.\nIf you didn't request"
        " a password recovery you can disregard this email."
    )
    send_email(email_to=email_to, email_subject=subject, email_message=message)
