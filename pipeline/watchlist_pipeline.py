from pathlib import Path

from playwright.sync_api import (
    sync_playwright
)

from config import (
    BASE_URL,
    HEADLESS,
    SLOW_MO
)

from delivery.emailer import (
    send_email
)

from charts.chart_setup import (
    configure_chart,
    set_period
)

from charts.stock_actions import (
    search_stock,
    capture_screenshot
)

from reports.pdf_report import (
    create_pdf_report
)

from models.stock_candidate import (
    StockCandidate
)

from watchlists.watchlist_manager import (
    load_watchlist
)


def get_watchlist_candidates():

    symbols = load_watchlist()

    return [

        StockCandidate(
            symbol=symbol,
            source="watchlist",
            engine="watchlist"
        )

        for symbol in symbols
    ]


def run_watchlist_pipeline():

    stocks = (
        get_watchlist_candidates()
    )

    if not stocks:

        print(
            "No subscribed stocks found"
        )

        return

    for file in Path(
        "screenshots"
    ).glob("*.png"):

        file.unlink()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO
        )

        context = browser.new_context(
            viewport={
                "width": 1920,
                "height": 1080
            }
        )

        page = context.new_page()

        print("Opening ACP...")

        page.goto(BASE_URL)

        page.wait_for_load_state(
            "networkidle"
        )

        page.wait_for_timeout(10000)

        configure_chart(page)

        for stock in stocks:

            try:

                print(
                    f"\nProcessing "
                    f"{stock.symbol}"
                )

                search_stock(
                    page,
                    stock.symbol
                )

                for period in [
                    "Daily",
                    "Weekly"
                ]:

                    set_period(
                        page,
                        period
                    )

                    capture_screenshot(
                        page,
                        stock.symbol,
                        period
                    )

            except Exception as e:

                print(
                    f"Failed processing "
                    f"{stock.symbol}: {e}"
                )

        browser.close()

    print(
        "\nGenerating PDF report..."
    )

    create_pdf_report(stocks)

    print("\nSending email...")

    send_email(
        subject=(
            "Daily Watchlist Report"
        )
    )

    for file in Path(
        "screenshots"
    ).glob("*.png"):

        file.unlink()

    print("\nDone.")