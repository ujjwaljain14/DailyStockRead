import json
from pathlib import Path
import requests
import pandas as pd
from models.stock_candidate import (
    StockCandidate
)


DOWNLOAD_DIR = Path("engine/data/downloads")

STATE_FILE = Path(
    "engine/data/state/rotation_state.json"
)


INDEX_URLS = {
    "smallcap100":
        "https://www.niftyindices.com/IndexConstituent/ind_niftysmallcap100list.csv",

    "midcap100":
        "https://www.niftyindices.com/IndexConstituent/ind_niftymidcap100list.csv",

    "nifty100":
        "https://www.niftyindices.com/IndexConstituent/ind_nifty100list.csv"
}


BATCH_SIZE = 10


def load_state():
    print("Loading rotation state...")

    if not STATE_FILE.exists():

        return {
            "smallcap100": 0,
            "midcap100": 0,
            "nifty100": 0
        }

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state: dict):

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


def download_index_csv(
    index_name: str,
    url: str
):

    file_path = DOWNLOAD_DIR / f"{index_name}.csv"

    print(f"Downloading {index_name}...")

    response = requests.get(
        url,
        headers={
            "User-Agent":
            "Mozilla/5.0"
        },
        timeout=30
    )

    response.raise_for_status()

    with open(file_path, "wb") as f:
        f.write(response.content)

    print(f"Downloaded {index_name}")

    return file_path

def load_symbols(csv_path: Path):

    df = pd.read_csv(csv_path)

    symbols = (
        df["Symbol"]
        .dropna()
        .astype(str)
        .tolist()
    )

    return symbols


def get_rotated_batch(
    symbols: list[str],
    start: int
):

    end = start + BATCH_SIZE

    if end <= len(symbols):

        batch = symbols[start:end]

    else:

        overflow = end - len(symbols)

        batch = (
            symbols[start:]
            + symbols[:overflow]
        )

    next_index = end % len(symbols)

    return batch, next_index


def cleanup_downloads():

    for file in DOWNLOAD_DIR.glob("*.csv"):
        file.unlink()

    print("Downloaded CSV files cleaned")


def get_rotational_stocks():

    state = load_state()

    selected_stocks = []

    try:

        for index_name, url in INDEX_URLS.items():

            print(f"\nProcessing {index_name}...")

            csv_path = download_index_csv(
                index_name,
                url
            )

            symbols = load_symbols(csv_path)

            batch, next_index = (
                get_rotated_batch(
                    symbols,
                    state[index_name]
                )
            )

            state[index_name] = next_index

            for symbol in batch:

                selected_stocks.append(
                    StockCandidate(
                        symbol=f"{symbol}.IN",
                        source=index_name,
                        engine="rotational"
                    )
                )

            print(
                f"Selected "
                f"{len(batch)} stocks "
                f"from {index_name}"
            )

        save_state(state)

    finally:

        cleanup_downloads()

    return selected_stocks