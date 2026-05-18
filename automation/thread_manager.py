import json

from pathlib import Path


THREAD_FILE = Path(
    "automation/tracked_threads.json"
)


def load_tracked_threads():

    if not THREAD_FILE.exists():

        return []

    with open(
        THREAD_FILE,
        "r"
    ) as f:

        data = json.load(f)

    return data.get(
        "message_ids",
        []
    )


def save_tracked_threads(
    message_ids: list[str]
):

    with open(
        THREAD_FILE,
        "w"
    ) as f:

        json.dump(
            {
                "message_ids": message_ids
            },
            f,
            indent=4
        )


def add_message_id(
    message_id: str
):

    message_ids = (
        load_tracked_threads()
    )

    if message_id not in message_ids:

        message_ids.append(
            message_id
        )

    save_tracked_threads(
        message_ids
    )


def is_tracked_message(
    message_id: str
):

    message_ids = (
        load_tracked_threads()
    )

    return message_id in message_ids