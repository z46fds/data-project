import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import requests

from fetch_data import fetch_stock_history, market_symbol, normalize_hist_data, write_dataset


class FetchDataTest(unittest.TestCase):
    def test_builds_exchange_prefixed_symbol(self):
        self.assertEqual(market_symbol("000001"), "sz000001")
        self.assertEqual(market_symbol("600000"), "sh600000")
        self.assertEqual(market_symbol("830799"), "bj830799")
        self.assertEqual(market_symbol("SZ000001"), "sz000001")

    def test_rejects_invalid_symbol(self):
        with self.assertRaisesRegex(ValueError, "六位数字"):
            market_symbol("001")

    def test_fetch_falls_back_to_sina_when_eastmoney_disconnects(self):
        fallback = pd.DataFrame(
            {"date": ["2026-01-01"], "close": [10.0], "volume": [100]}
        )
        with patch(
            "fetch_data.ak.stock_zh_a_hist",
            side_effect=requests.ConnectionError("temporary failure"),
        ), patch(
            "fetch_data.ak.stock_zh_a_daily",
            return_value=fallback,
        ) as daily:
            raw, source = fetch_stock_history("000001", "20260101", "20260131")

        self.assertEqual(source, "AkShare.stock_zh_a_daily")
        self.assertIs(raw, fallback)
        daily.assert_called_once_with(
            symbol="sz000001",
            start_date="20260101",
            end_date="20260131",
            adjust="",
        )

    def test_normalizes_akshare_columns(self):
        raw = pd.DataFrame(
            {
                "日期": ["2026-01-03", "2026-01-01", "2026-01-02"],
                "收盘": ["10.5", "9.8", "10.1"],
                "成交量": [300, 100, 200],
                "开盘": [9, 9, 9],
            }
        )

        normalized = normalize_hist_data(raw)

        self.assertEqual(normalized.columns.tolist(), ["date", "price", "volume"])
        self.assertEqual(
            normalized["date"].tolist(),
            ["2026-01-01", "2026-01-02", "2026-01-03"],
        )
        self.assertEqual(normalized["volume"].tolist(), [100, 200, 300])

    def test_accepts_already_normalized_columns(self):
        raw = pd.DataFrame(
            {"date": ["2026-01-01"], "price": [10.0], "volume": [100]}
        )

        normalized = normalize_hist_data(raw)

        self.assertEqual(normalized.iloc[0].to_dict(), {
            "date": "2026-01-01",
            "price": 10.0,
            "volume": 100,
        })

    def test_sort_is_stable_for_same_date_duplicates(self):
        raw = pd.DataFrame(
            {
                "date": ["2026-01-01", "2026-01-01"],
                "price": [10.0, 11.0],
                "volume": [100, 200],
            }
        )

        normalized = normalize_hist_data(raw)

        self.assertEqual(normalized["price"].tolist(), [10.0, 11.0])

    def test_rejects_missing_source_column(self):
        raw = pd.DataFrame({"日期": ["2026-01-01"], "收盘": [10.0]})

        with self.assertRaisesRegex(ValueError, "缺少必要列"):
            normalize_hist_data(raw)

    def test_write_dataset_outputs_csv_and_metadata(self):
        raw = pd.DataFrame(
            {
                "日期": ["2026-01-01"],
                "收盘": [10.0],
                "成交量": [100],
            }
        )

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            output = base / "data.csv"
            metadata = base / "data_metadata.json"

            normalized = write_dataset(
                raw,
                output,
                metadata,
                symbol="000001",
                start_date="20260101",
                end_date="20260131",
            )

            self.assertEqual(len(normalized), 1)
            self.assertTrue(output.is_file())
            self.assertTrue(metadata.is_file())
            metadata_text = metadata.read_text(encoding="utf-8")
            self.assertIn("AkShare.stock_zh_a_hist", metadata_text)
            self.assertIn('"rows": 1', metadata_text)


if __name__ == "__main__":
    unittest.main()
