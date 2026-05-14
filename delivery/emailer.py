import os
import smtplib

from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")


REPORT_PATH = Path(
    "reports/output/daily_report.pdf"
)


def send_email():

    if not REPORT_PATH.exists():

        print("PDF report not found")

        return

    msg = EmailMessage()

    msg["Subject"] = (
        "Daily StockCharts Report"
    )

    msg["From"] = EMAIL_USER

    msg["To"] = EMAIL_TO

    msg.set_content(
        "Attached is today's stock report PDF."
    )

    with open(REPORT_PATH, "rb") as f:

        file_data = f.read()

        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="pdf",
            filename=REPORT_PATH.name
        )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:

        smtp.login(
            EMAIL_USER,
            EMAIL_PASS
        )

        smtp.send_message(msg)

    print("Email sent successfully")