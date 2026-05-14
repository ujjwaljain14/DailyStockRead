from playwright.sync_api import Page

from charts.stock_actions import search_stock


def close_popup(page: Page):

    try:
        page.locator("acp-tour-modal").get_by_role(
            "button",
            name="Close"
        ).click(timeout=3000)

        print("Popup closed")

    except:
        print("No popup found")

def remove_indicator(page: Page, indicator: str):

    try:

        item = page.locator(
            "chart-outline-item"
        ).filter(
            has_text=indicator
        )

        item.locator(".far").click()
        page.wait_for_timeout(1000)

        print(f"{indicator} removed")

    except Exception as e:

        print(f"Could not remove {indicator}: {e}")

def remove_indicators(page: Page, indicators: list[str]):

    for indicator in indicators:
        remove_indicator(page, indicator)

def remove_all_indicators(page: Page, except_indicators: list[str] = None):

    indicators = page.locator("chart-outline-item")

    count = indicators.count()
    indicator_names = [indicators.nth(i).inner_text() for i in range(count)]
    print(f"Found indicators: {indicator_names}")
    if except_indicators:
        indicator_names = [name for name in indicator_names if name.strip() not in except_indicators]
    remove_indicators(page, indicator_names)


def add_indicator(page: Page, indicator: str, value: list = None):

    try:

        search = page.get_by_role("textbox", name="Search")

        search.click()
        search.fill(indicator)

        page.get_by_role(
            "button",
            name=f" {indicator}"
        ).click()

        if value:

            for idx, val in enumerate(value):

                input_box = page.locator(
                    "indicator-edit-panel acp-input input"
                ).nth(idx)

                input_box.click()

                input_box.press("Control+A")

                input_box.type(str(val), delay=100)

                input_box.press("Enter")

                page.wait_for_timeout(1000)
        
        page.locator(".close-window-button").click()

        print(f"{indicator} added")

    except Exception as e:

        print(f"Could not add {indicator}: {e}")

def add_indicators(page: Page, indicators: list[dict]):
    for indicator in indicators:
        add_indicator(page, indicator["indicator"], indicator.get("value"))

def change_sma50_color(page: Page):

    try:
        page.locator("#chartOutlinePanel").get_by_text("SMA(50)").click()

        page.get_by_role(
            "button",
            name="toggle color picker dialog"
        ).click()

        page.locator(
            ".pcr-app.visible > .pcr-swatches > button:nth-child(12)"
        ).click()

        page.locator(".close-window-button").click()

        print("SMA50 color changed")

    except Exception as e:
        print(f"Could not change SMA50 color: {e}")


def add_sma100(page: Page):

    try:
        search = page.get_by_role("textbox", name="Search")

        search.click()
        search.fill("sma")

        page.get_by_role(
            "button",
            name=" Moving Average - Simple"
        ).click()

        page.locator(
            ".acp-sidebar-slider-form-group > acp-input > .au-target"
        ).first.click()

        page.locator(
            ".acp-sidebar-slider-form-group > acp-input > .au-target"
        ).first.fill("100")

        page.get_by_role(
            "button",
            name="toggle color picker dialog"
        ).click()

        page.locator(
            ".pcr-app.visible > .pcr-swatches > button:nth-child(13)"
        ).click()

        page.get_by_role(
            "button",
            name="   Close"
        ).click()

        print("SMA100 added")

    except Exception as e:
        print(f"Could not add SMA100: {e}")


def add_rsi(page: Page):

    try:
        search = page.get_by_role("textbox", name="Search")

        search.click()
        search.fill("rsi")

        page.get_by_role(
            "button",
            name=" RSI"
        ).click()

        page.locator(".close-window-button").click()

        print("RSI added")

    except Exception as e:
        print(f"Could not add RSI: {e}")


def close_side_panel(page: Page):

    try:
        page.locator(".close-window-button").click()

        print("Side panel closed")

    except Exception as e:
        print(f"Could not close panel: {e}")

def set_period(page: Page, period: str):

    try:

        period_button = page.locator(
            "button:has-text('Daily'), button:has-text('Weekly')"
        ).first

        current_text = period_button.inner_text().strip()

        if current_text == period:

            print(f"Already on {period}")

            return

        period_button.click()

        page.wait_for_timeout(500)

        page.get_by_role(
            "link",
            name=period
        ).click()

        page.wait_for_load_state("networkidle")

        page.wait_for_timeout(1500)

        print(f"Period set to {period}")

    except Exception as e:

        print(f"Could not set period {period}: {e}")
        
def set_best_range(page: Page):

    try:

        # Open range dropdown
        page.get_by_role(
            "button",
            name=" Range "
        ).click()

        page.wait_for_timeout(1000)

        preferred_ranges = [
            "3 Years",
            "2 Years",
            "1.5 Years",
            "1 Year",
            "9 Months",
            "6 Months",
            "3 Months",
            "1 Month"
        ]

        for range_name in preferred_ranges:

            option = page.get_by_role(
                "link",
                name=range_name
            )

            if option.count() > 0 and option.is_enabled():

                try:

                    option.click(timeout=2000)

                    print(f"Range set to {range_name}")

                    page.wait_for_timeout(2000)

                    return

                except:
                    pass

        print("No suitable range found")

    except Exception as e:
        print(f"Could not set range: {e}")  


def configure_chart(page: Page):

    close_popup(page)

    page.wait_for_timeout(2000)

    search_stock(page, '$NIFTY')

    remove_all_indicators(page, except_indicators=["Volume"])

    add_indicators(page, [
        {"indicator":"Moving Average - Simple", "value":[50]},
        {"indicator":"Moving Average - Simple", "value":[100]},
        {"indicator":"Moving Average - Simple", "value":[200]},
        {"indicator":"RSI"}])

    close_side_panel(page)

    # set_best_range(page)

    page.wait_for_timeout(3000)

    print("Chart configured")