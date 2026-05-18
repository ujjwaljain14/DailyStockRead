import json

from pathlib import Path


WATCHLIST_FILE = Path(
    "watchlists/subscribed_stocks.json"
)


def load_watchlist():

    if not WATCHLIST_FILE.exists():

        return []

    with open(
        WATCHLIST_FILE,
        "r"
    ) as f:

        data = json.load(f)

    return data.get(
        "stocks",
        []
    )


def save_watchlist(
    stocks: list[str]
):

    with open(
        WATCHLIST_FILE,
        "w"
    ) as f:

        json.dump(
            {
                "stocks": sorted(
                    list(set(stocks))
                )
            },
            f,
            indent=4
        )


def add_stock(
    symbol: str
):

    symbol = (
        symbol.upper()
        .replace(".IN", "")
    )

    symbol = f"{symbol}.IN"

    stocks = load_watchlist()

    if symbol in stocks:

        print(
            f"{symbol} already exists"
        )

        return

    stocks.append(symbol)

    save_watchlist(stocks)

    print(f"Added {symbol}")


def remove_stock(
    symbol: str
):

    symbol = (
        symbol.upper()
        .replace(".IN", "")
    )

    symbol = f"{symbol}.IN"

    stocks = load_watchlist()

    if symbol not in stocks:

        print(
            f"{symbol} not found"
        )

        return

    stocks.remove(symbol)

    save_watchlist(stocks)

    print(f"Removed {symbol}")


def list_stocks():

    stocks = load_watchlist()

    print("\nWatchlist:\n")

    for stock in stocks:

        print(stock)

    return stocks