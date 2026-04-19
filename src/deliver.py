"""Gmail SMTP delivery with attachment.

Requires 2-Step Verification on the Gmail account and an App Password.
Generate at: https://myaccount.google.com/apppasswords
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path

from src.config import (
    GMAIL_SENDER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL,
    EMAIL_SUBJECT, EMAIL_BODY,
)


def send_email(attachment_path, date_str, date_long_str, n_ok, n_total):
    """Send the daily file via Gmail SMTP."""
    if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
        raise RuntimeError(
            "Missing GMAIL_SENDER or GMAIL_APP_PASSWORD in environment. "
            "Set these as GitHub Secrets."
        )

    msg = MIMEMultipart()
    msg["From"] = GMAIL_SENDER
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = EMAIL_SUBJECT.format(date=date_str)

    body = EMAIL_BODY.format(
        date_long=date_long_str, n_ok=n_ok, n_total=n_total,
    )
    msg.attach(MIMEText(body, "plain"))

    # Attach the xlsx
    path = Path(attachment_path)
    with open(path, "rb") as f:
        part = MIMEBase("application",
                        "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition",
                    f'attachment; filename="{path.name}"')
    msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_SENDER, [RECIPIENT_EMAIL], msg.as_string())

    return True
