# Stock Chart Automation

Automated daily technical-analysis reports for Indian equities (NSE). The system drives a real charting tool (StockCharts.com's ACP), captures Daily/Weekly chart screenshots with a standard indicator set (SMA 50/100/200 + RSI), compiles them into a PDF, and emails the report — with zero manual intervention. Stock selection is fully pluggable: today it supports a **rotational NIFTY-index engine** and a **user-managed watchlist controlled entirely by replying to email**.

Everything runs on GitHub Actions, on a daily cron, with state persisted back to the repo.

---

## What it does

1. **Picks stocks to chart** — either by rotating through batches of NIFTY 100 / Midcap 100 / Smallcap 100 constituents, or from a watchlist you maintain via email.
2. **Opens a headless browser**, navigates to the ACP charting tool, and configures the chart once (removes default indicators, adds SMA50/SMA100/SMA200 + RSI).
3. **For each stock**, searches it, switches between Daily and Weekly timeframes, and screenshots the chart canvas.
4. **Builds a PDF report**, grouped by source (index/watchlist), with one section per stock and one image per timeframe.
5. **Emails the PDF** and tracks the outgoing `Message-ID` so replies to that email can be recognized later.
6. **Listens for reply commands** (`+SYMBOL`, `-SYMBOL`, `LIST`, `CLEAR`) in unread emails that are replies to a tracked report, and updates the watchlist accordingly before the next run.

Two independent daily workflows exist:

| Workflow | Entry point | Stock source |
|---|---|---|
| `daily.yml` | `main.py` → `run_chart_pipeline()` | Rotational NIFTY-index engine |
| `daily_watchlist_report.yml` | `watchlist_main.py` → `run_watchlist_pipeline()` | User watchlist (`subscribed_stocks.json`), updated via email commands first |

---

## Why the architecture is clean

The codebase is organized by **responsibility**, not by feature, so each layer only knows about the layer directly below it:

```
config.py                  # single source of truth for URLs, paths, browser settings

models/                    # plain data — StockCandidate is the shared currency
  stock_candidate.py       #   between every engine, pipeline, and report

engine/                    # WHAT to chart
  decision_engine.py        - thin facade; swap the underlying engine here
  engines/
    nifty_rotational_engine.py  - one interchangeable strategy implementation
  data/                     - engine-owned scratch space (downloads/state)

watchlists/                # WHAT to chart (alternate source)
  watchlist_manager.py      - CRUD over subscribed_stocks.json

charts/                    # HOW to drive the chart UI
  chart_setup.py            - one-time chart configuration (indicators, popups)
  stock_actions.py          - per-stock actions (search, screenshot)

pipeline/                  # ORCHESTRATION — wires engine + charts + reports + delivery
  chart_pipeline.py
  watchlist_pipeline.py

reports/                   # WHAT comes out
  pdf_report.py             - turns StockCandidates + screenshots into a PDF

delivery/                  # HOW it leaves the system
  emailer.py                - sends the PDF, records the Message-ID

automation/                # THE FEEDBACK LOOP
  thread_manager.py         - tracks which sent emails are "listening" for replies
  command_parser.py         - text -> structured commands
  command_executor.py       - structured commands -> watchlist mutations
  email_command_listener.py - IMAP polling glue that ties the above together

main.py / watchlist_main.py  # entry points — each is a one-line call into a pipeline
```

**Key design properties:**

- **Single shared contract (`StockCandidate`)** — every engine, the watchlist, the pipelines, and the PDF report all speak the same small dataclass (`symbol`, `source`, `engine`). Adding a new stock source never requires touching `charts/`, `reports/`, or `delivery/`.
- **Browser automation is fully decoupled from stock selection.** `charts/chart_setup.py` and `charts/stock_actions.py` know nothing about *why* a symbol was chosen — they just take a `Page` and a string. This is what makes two independent pipelines possible with almost no duplication.
- **Pipelines are the only orchestrators.** `pipeline/chart_pipeline.py` and `pipeline/watchlist_pipeline.py` are the only files that import from more than one layer. Nothing lower in the stack reaches "up" — engines don't know about email, charts don't know about PDFs, reports don't know about engines.
- **State is externalized and file-backed** (`rotation_state.json`, `subscribed_stocks.json`, `tracked_threads.json`), so a stateless GitHub Actions runner can pick up exactly where the last run left off — the workflow simply commits the changed JSON back to the repo.
- **The email command loop is a self-contained subsystem.** `thread_manager` (tracking), `command_parser` (parsing), and `command_executor` (side effects) are each independently testable and swappable — parsing has zero knowledge of IMAP, and execution has zero knowledge of email at all.
- **Config is centralized.** `config.py` is the only place that knows the target URL, headless/slow-mo settings, and screenshot directory, so environment-specific tuning (e.g. debugging with `HEADLESS = False`) never touches business logic.

---

## How to extend it

The layering above is designed to make the common extensions additive rather than invasive:

- **Add a new stock-selection strategy** (e.g. momentum screener, sector rotation, RSI oversold scan): drop a new module in `engine/engines/`, have it return `list[StockCandidate]`, and point `decision_engine.py` at it (or add it alongside the existing one). No other layer changes.
- **Add a new indicator or chart layout**: extend `charts/chart_setup.py` (e.g. `add_indicator(page, "MACD")`) — `configure_chart()` is the only place that needs a new call.
- **Add a new report format** (e.g. HTML digest, Slack summary): add a module under `reports/` that consumes the same `list[StockCandidate]` + `screenshots/` contract; the pipelines just call it alongside or instead of `create_pdf_report`.
- **Add a new delivery channel** (Telegram, Slack, WhatsApp): add a module under `delivery/` with the same "attach latest report" shape as `emailer.py`.
- **Add a new email command** (e.g. `PAUSE`, `SET <symbol> <period>`): extend `command_parser.parse_commands` to emit a new `action`, then handle it in `command_executor.execute_commands`. Parsing and execution are decoupled, so this is a two-line change in each file.
- **Run more frequently or on new markets**: `config.BASE_URL` and the watchlist/rotation JSON files are the only India/NSE-specific coupling; pointing them at a different symbol suffix and index source set is enough to retarget the whole pipeline.

---

## Setup

**Dependencies** (`requirements.txt`): `playwright`, `python-dotenv`, `pandas`, `requests`, `reportlab`.

```bash
pip install -r requirements.txt
playwright install --with-deps chromium
```

**Environment variables** (used by `delivery/emailer.py` and `automation/email_command_listener.py`, typically via a `.env` file locally or GitHub Secrets in CI):

| Variable | Purpose |
|---|---|
| `EMAIL_USER` | SMTP/IMAP login (sender) |
| `EMAIL_PASS` | SMTP/IMAP app password |
| `EMAIL_TO` | Report recipient |
| `EMAIL_IMAP_SERVER` | IMAP host for command listening (defaults to `imap.gmail.com`) |

**Run locally:**

```bash
python main.py            # rotational engine pipeline
python watchlist_main.py  # watchlist pipeline
```

**Run in CI:** handled by `.github/workflows/daily.yml` and `.github/workflows/daily_watchlist_report.yml`, both scheduled around 9 PM IST and also triggerable manually via `workflow_dispatch`. Each workflow commits any resulting state changes (watchlist, rotation index, tracked threads) back to the repository so the next run continues seamlessly.
