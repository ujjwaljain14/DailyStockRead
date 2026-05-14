from playwright.sync_api import Page
from config import SCREENSHOT_DIR


def search_stock(page: Page, stock: str):

    search_box = page.locator("input").nth(0)

    search_box.click()

    search_box.fill(stock)

    search_box.press("Enter")

    # Wait for chart/network to settle
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2500)

    print(f"Loaded {stock}")


def capture_screenshot(
    page: Page,
    stock: str,
    period: str
):

    screenshot_path = (
        SCREENSHOT_DIR /
        f"{stock}_{period}.png"
    )

    chart = page.locator("canvas").first

    chart.screenshot(
        path=str(screenshot_path),
        animations="disabled"
    )

    print(f"Saved screenshot: {screenshot_path.name}")
    