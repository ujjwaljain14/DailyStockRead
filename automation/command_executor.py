from watchlists.watchlist_manager import (
    add_stock,
    remove_stock,
    list_stocks,
    save_watchlist
)


def execute_commands(
    commands: list[dict]
):

    for command in commands:

        action = command["action"]

        if action == "add":

            add_stock(
                command["symbol"]
            )

        elif action == "remove":

            remove_stock(
                command["symbol"]
            )

        elif action == "list":

            list_stocks()

        elif action == "clear":

            save_watchlist([])

            print(
                "Watchlist cleared"
            )