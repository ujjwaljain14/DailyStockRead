from datetime import datetime
import imaplib
import email

from email.header import decode_header

from dotenv import load_dotenv

from automation.thread_manager import (
    is_tracked_message
)

import os


from automation.command_parser import (
    parse_commands
)

from automation.command_executor import (
    execute_commands
)


load_dotenv()


EMAIL_USER = os.getenv(
    "EMAIL_USER"
)

EMAIL_TO = os.getenv(
    "EMAIL_TO"
)

EMAIL_PASS = os.getenv(
    "EMAIL_PASS"
)

IMAP_SERVER = os.getenv(
    "EMAIL_IMAP_SERVER",
    "imap.gmail.com"
)


def extract_email_body(msg):

    if msg.is_multipart():

        for part in msg.walk():

            content_type = (
                part.get_content_type()
            )

            content_disposition = str(
                part.get(
                    "Content-Disposition"
                )
            )

            if (
                content_type == "text/plain"
                and "attachment"
                not in content_disposition
            ):

                payload = (
                    part.get_payload(
                        decode=True
                    )
                )

                if payload:

                    return payload.decode(
                        errors="ignore"
                    )

    else:

        payload = msg.get_payload(
            decode=True
        )

        if payload:

            return payload.decode(
                errors="ignore"
            )

    return ""


def process_unread_emails():

    mail = imaplib.IMAP4_SSL(
        IMAP_SERVER
    )

    mail.login(
        EMAIL_USER,
        EMAIL_PASS
    )

    mail.select("inbox")
    status, messages = mail.search(None, 'TO', EMAIL_TO, 'UNSEEN')

    email_ids = (
        messages[0]
        .split()
    )

    print(
        f"Found {len(email_ids)} unread emails"
    )

    for email_id in email_ids:

        _, msg_data = mail.fetch(
            email_id,
            "(RFC822)"
        )

        raw_email = (
            msg_data[0][1]
        )

        msg = email.message_from_bytes(
            raw_email
        )

        subject, encoding = decode_header(
            msg["Subject"]
        )[0]

        if isinstance(subject, bytes):

            subject = subject.decode(
                encoding or "utf-8",
                errors="ignore"
            )

        print(
            f"\nProcessing email: {subject}"
        )

        in_reply_to = msg.get(
            "In-Reply-To"
        )

        if not in_reply_to:

            print(
                "Skipping: no In-Reply-To"
            )

            continue

        if not is_tracked_message(
            in_reply_to.strip()
        ):

            print(
                "Skipping: unrelated thread"
            )

            continue

        body = extract_email_body(
            msg
        )

        print("\nEmail Body:\n")

        print(body)

        commands = parse_commands(
            body
        )

        if not commands:

            print(
                "No valid commands found"
            )

            continue

        print(
            f"Parsed commands: "
            f"{commands}"
        )

        execute_commands(commands)

        mail.store(
            email_id,
            '+FLAGS',
            '\\Seen'
        )

    mail.logout()


if __name__ == "__main__":

    process_unread_emails()
