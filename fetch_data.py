"""Fetch and normalize daily stock history for the v1 analysis pipeline."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import akshare as ak
import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = BASE_DIR / "data.csv"
DEFAULT_METADATA = BASE_DIR / "data_metadata.json"

COLUMN_ALIASES = {
    "date": ("date", "日期"),
    "price": ("price", "close", "收盘", "收盘价"),
    "volume": ("volume", "成交量"),
}


def normalize_hist_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Convert AkShare-style history columns to the v1 input contract."""
    resolved: dict[str, str] = {}
    missing: list[str] = []
    for target, aliases in COLUMN_ALIASES.items():
        source = next((name for name in aliases if name in raw.columns), None)
        if source is None:
            missing.append(f"{target}（{'/'.join(aliases)}）")
        else:
            resolved[target] = source

    if missing:
        raise ValueError(f"缺少必要列: {', '.join(missing)}")

    normalized = raw.loc[:, list(resolved.values())].copy()
    normalized.columns = list(resolved.keys())
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
    normalized["price"] = pd.to_numeric(normalized["price"], errors="coerce")
    normalized["volume"] = pd.to_numeric(normalized["volume"], errors="coerce")

    valid = (
        normalized["date"].notna()
        & normalized["price"].notna()
        & normalized["volume"].notna()
        & (normalized["price"] > 0)
        & (normalized["volume"] >= 0)
    )
    normalized = (
        normalized.loc[valid]
        .sort_values("date", kind="mergesort")
        .reset_index(drop=True)
    )
    if normalized.empty:
        raise ValueError("数据源没有可用记录")

    normalized["date"] = normalized["date"].dt.strftime("%Y-%m-%d")
    return normalized


def market_symbol(symbol: str) -> str:
    """Return the exchange-prefixed symbol expected by Sina."""
    symbol = symbol.lower()
    if re.fullmatch(r"(?:sh|sz|bj)\d{6}", symbol):
        return symbol
    if not re.fullmatch(r"\d{6}", symbol):
        raise ValueError("股票代码应为六位数字，或以 sh/sz/bj 开头")
    if symbol.startswith("6"):
        return f"sh{symbol}"
    if symbol.startswith(("0", "3")):
        return f"sz{symbol}"
    if symbol.startswith(("4", "8")):
        return f"bj{symbol}"
    raise ValueError(f"无法识别股票交易所: {symbol}")


def fetch_stock_history(
    symbol: str,
    start_date: str,
    end_date: str,
) -> tuple[pd.DataFrame, str]:
    """Download A-share history, falling back to Sina if Eastmoney is unavailable."""
    try:
        raw = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
        )
        return raw, "AkShare.stock_zh_a_hist"
    except requests.RequestException:
        raw = ak.stock_zh_a_daily(
            symbol=market_symbol(symbol),
            start_date=start_date,
            end_date=end_date,
            adjust="",
        )
        return raw, "AkShare.stock_zh_a_daily"


def write_dataset(
    raw: pd.DataFrame,
    output: Path,
    metadata_path: Path,
    *,
    symbol: str,
    start_date: str,
    end_date: str,
    source: str = "AkShare.stock_zh_a_hist",
) -> pd.DataFrame:
    """Normalize, persist and describe a downloaded dataset."""
    normalized = normalize_hist_data(raw)
    output.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(output, index=False)

    metadata = {
        "source": source,
        "source_note": (
            f"AkShare 股票 {symbol} 日线数据，区间 "
            f"{start_date} 至 {end_date}；price 使用收盘价，volume 使用成交量。"
        ),
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "rows": len(normalized),
        "fields": ["date", "price", "volume"],
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return normalized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="下载并标准化 AkShare A股日线数据")
    parser.add_argument("--symbol", default="000001", help="六位股票代码")
    parser.add_argument("--start-date", default="20230101", help="起始日期 YYYYMMDD")
    parser.add_argument("--end-date", default="20231231", help="结束日期 YYYYMMDD")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw, source = fetch_stock_history(args.symbol, args.start_date, args.end_date)
    normalized = write_dataset(
        raw,
        args.output,
        args.metadata,
        symbol=args.symbol,
        start_date=args.start_date,
        end_date=args.end_date,
        source=source,
    )
    print(f"已写入 {len(normalized)} 行: {args.output}")
    print(f"数据说明: {args.metadata}")
    print(normalized.head().to_string(index=False))


if __name__ == "__main__":
    main()
