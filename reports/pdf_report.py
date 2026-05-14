from collections import defaultdict
from pathlib import Path

from reportlab.lib.pagesizes import A4

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from models.stock_candidate import (
    StockCandidate
)


SCREENSHOT_DIR = Path("screenshots")

OUTPUT_DIR = Path("reports/output")

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


REPORT_PATH = (
    OUTPUT_DIR / "daily_report.pdf"
)


SECTION_TITLES = {
    "smallcap100":
        "NIFTY SMALLCAP 100",

    "midcap100":
        "NIFTY MIDCAP 100",

    "nifty100":
        "NIFTY 100"
}


IMAGE_WIDTH = 500
IMAGE_HEIGHT = 280


styles = getSampleStyleSheet()


def build_image(path: Path):

    image = Image(
        str(path),
        width=IMAGE_WIDTH,
        height=IMAGE_HEIGHT
    )

    return image


def group_candidates_by_source(
    candidates: list[StockCandidate]
):

    grouped = defaultdict(list)

    for candidate in candidates:

        grouped[candidate.source].append(
            candidate
        )

    return grouped


def create_pdf_report(
    candidates: list[StockCandidate]
):

    grouped_candidates = (
        group_candidates_by_source(
            candidates
        )
    )

    doc = SimpleDocTemplate(
        str(REPORT_PATH),
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elements = []

    for source, stocks in grouped_candidates.items():

        section_title = (
            SECTION_TITLES.get(
                source,
                source.upper()
            )
        )

        elements.append(
            Paragraph(
                section_title,
                styles["Heading1"]
            )
        )

        elements.append(Spacer(1, 20))

        for candidate in stocks:

            symbol = candidate.symbol

            elements.append(
                Paragraph(
                    symbol,
                    styles["Heading2"]
                )
            )

            elements.append(Spacer(1, 10))

            for period in [
                "Daily",
                "Weekly"
            ]:

                elements.append(
                    Paragraph(
                        period,
                        styles["Heading3"]
                    )
                )

                image_path = (
                    SCREENSHOT_DIR /
                    f"{symbol}_{period}.png"
                )

                if image_path.exists():

                    elements.append(
                        build_image(image_path)
                    )

                    elements.append(
                        Spacer(1, 20)
                    )

                else:

                    elements.append(
                        Paragraph(
                            "Screenshot not found",
                            styles["BodyText"]
                        )
                    )

            elements.append(Spacer(1, 30))

        elements.append(PageBreak())

    doc.build(elements)

    print(
        f"PDF report generated: "
        f"{REPORT_PATH}"
    )

    return REPORT_PATH