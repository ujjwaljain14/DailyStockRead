from dataclasses import dataclass


@dataclass
class StockCandidate:

    symbol: str

    source: str

    engine: str