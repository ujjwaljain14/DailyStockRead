from pathlib import Path

from playwright.sync_api import sync_playwright

from config import (
    BASE_URL,
    HEADLESS,
    SLOW_MO
)

from reports.pdf_report import (
    create_pdf_report
)

from delivery.emailer import send_email

from charts.chart_setup import (
    configure_chart,
    set_period,
    reset_chart_view
)

from charts.stock_actions import (
    search_stock,
    capture_screenshot
)

from engine.decision_engine import (
    get_trade_candidates
)


def clear_old_screenshots():

    print("Clearing old screenshots...")

    for file in Path("screenshots").glob("*.png"):
        file.unlink()

def clear_old_reports():

    print("Clearing old reports...")

    for file in Path("reports/output").glob("*.pdf"):
        file.unlink()


def process_stock(page, symbol: str):
    print(f"\nProcessing {symbol}")

    search_stock(page, symbol)

    for period in ["Daily", "Weekly"]:

        set_period(page, period)
        reset_chart_view(page)

        capture_screenshot(
            page,
            symbol,
            period
        )


def run_chart_pipeline():

    stocks = get_trade_candidates()

    clear_old_screenshots()

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

        page.wait_for_load_state("networkidle")

        page.wait_for_timeout(10000)

        configure_chart(page)

        for candidate in stocks:

            try:

                process_stock(
                    page,
                    candidate.symbol
                )

            except Exception as e:

                print(f"Failed processing {candidate.symbol}: {e}")

        browser.close()

    print("\nGenerating PDF report...")

    create_pdf_report(stocks)

    print("\nSending email...")

    send_email(
        subject=(
            "Daily Rotational Report"
        )
    )

    clear_old_screenshots()
    clear_old_reports()

    print("\nDone.")
