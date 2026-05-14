from pathlib import Path

BASE_URL = "https://stockcharts.com/acp/?s=TCS.IN"

BASE_DIR = Path(__file__).resolve().parent

SCREENSHOT_DIR = BASE_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

HEADLESS = True#False
SLOW_MO = 300