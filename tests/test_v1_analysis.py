import tempfile
import unittest
from pathlib import Path

import pandas as pd

from v1_analysis import (
    build_report,
    clean_data,
    data_quality,
    monthly_summary,
    overall_statistics,
    run_pipeline,
)


class V1AnalysisTest(unittest.TestCase):
    def test_repository_contains_default_input_dataset(self):
        from v1_analysis import BASE_DIR

        self.assertTrue((BASE_DIR / "data.csv").is_file())

    def test_clean_data_parses_and_filters_invalid_rows(self):
        raw = pd.DataFrame(
            {
                "date": ["2026-01-01", "2026-01-15", "2026-02-01", "bad-date", "2026-03-01", "2026-04-01"],
                "price": [100.0, 110.0, 121.0, 80.0, -2.0, None],
                "volume": [10, 20, 30, 40, 50, 60],
            }
        )

        cleaned = clean_data(raw)

        self.assertEqual(len(cleaned), 3)
        self.assertEqual(list(cleaned["month"].unique()), ["2026-01", "2026-02"])
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned["date"]))
        self.assertTrue((cleaned["price"] > 0).all())
        self.assertTrue((cleaned["volume"] >= 0).all())
        self.assertTrue(cleaned["date"].is_monotonic_increasing)

    def test_clean_data_rejects_missing_required_column(self):
        raw = pd.DataFrame({"date": ["2026-01-01"], "price": [100.0]})

        with self.assertRaisesRegex(ValueError, "缺少必要列"):
            clean_data(raw)

    def test_monthly_summary_computes_counts_prices_volume_and_change(self):
        cleaned = clean_data(
            pd.DataFrame(
                {
                    "date": ["2026-01-01", "2026-01-15", "2026-02-01"],
                    "price": [100.0, 110.0, 121.0],
                    "volume": [10, 20, 30],
                }
            )
        )

        summary = monthly_summary(cleaned)

        jan = summary.loc["2026-01"]
        feb = summary.loc["2026-02"]
        self.assertEqual(int(jan["observations"]), 2)
        self.assertAlmostEqual(float(jan["average_price"]), 105.0)
        self.assertAlmostEqual(float(jan["minimum_price"]), 100.0)
        self.assertAlmostEqual(float(jan["maximum_price"]), 110.0)
        self.assertEqual(int(jan["total_volume"]), 30)
        self.assertAlmostEqual(float(feb["average_price"]), 121.0)
        self.assertAlmostEqual(float(feb["price_change_pct"]), 15.238095, places=5)

    def test_data_quality_reports_detailed_invalid_counts(self):
        raw = pd.DataFrame(
            {
                "date": ["2026-01-01", "2026-01-01", "bad-date", "2026-01-02", "2026-01-03", "2026-01-04"],
                "price": [100.0, 100.0, 80.0, None, -1.0, 90.0],
                "volume": [10, 10, 20, 30, 40, -5],
            }
        )
        cleaned = clean_data(raw)

        quality = data_quality(raw, cleaned)

        self.assertEqual(quality["raw_rows"], 6)
        self.assertEqual(quality["clean_rows"], 2)
        self.assertEqual(quality["dropped_rows"], 4)
        self.assertEqual(quality["invalid_or_missing_date"], 1)
        self.assertEqual(quality["invalid_or_missing_price"], 1)
        self.assertEqual(quality["invalid_or_missing_volume"], 0)
        self.assertEqual(quality["nonpositive_price"], 1)
        self.assertEqual(quality["negative_volume"], 1)
        self.assertEqual(quality["duplicate_rows"], 1)

    def test_overall_statistics_computes_price_volume_and_correlation(self):
        cleaned = clean_data(
            pd.DataFrame(
                {
                    "date": ["2026-01-01", "2026-01-15"],
                    "price": [100.0, 110.0],
                    "volume": [10, 20],
                }
            )
        )

        overall = overall_statistics(cleaned)

        self.assertEqual(overall["observations"], 2)
        self.assertEqual(overall["start_date"], "2026-01-01")
        self.assertEqual(overall["end_date"], "2026-01-15")
        self.assertAlmostEqual(overall["average_price"], 105.0)
        self.assertAlmostEqual(overall["median_price"], 105.0)
        self.assertAlmostEqual(overall["price_std"], 7.071068, places=5)
        self.assertEqual(overall["total_volume"], 30)
        self.assertAlmostEqual(overall["price_volume_correlation"], 1.0)

    def test_report_identifies_high_low_and_most_active_month(self):
        summary = pd.DataFrame(
            {
                "observations": [2, 1, 3],
                "average_price": [105.0, 121.0, 109.0],
                "median_price": [105.0, 121.0, 109.0],
                "minimum_price": [100.0, 121.0, 90.0],
                "maximum_price": [110.0, 121.0, 130.0],
                "average_volume": [15.0, 30.0, 85.0],
                "total_volume": [30, 30, 255],
                "price_change_pct": [None, 15.238095, -9.917355],
            },
            index=pd.Index(["2026-01", "2026-02", "2026-03"], name="month"),
        )

        report = build_report(summary, clean_rows=6, dropped_rows=2)

        self.assertIn("有效记录：6 行", report)
        self.assertIn("清理剔除：2 行", report)
        self.assertIn("最高月均价：2026-02（121.00）", report)
        self.assertIn("最低月均价：2026-01（105.00）", report)
        self.assertIn("成交量最高：2026-03（255）", report)
        self.assertIn("最大月均价涨幅：2026-02（15.24%）", report)

    def test_pipeline_writes_all_v1_outputs(self):
        raw = pd.DataFrame(
            {
                "date": ["2026-01-01", "2026-01-15", "2026-02-01", "bad-date"],
                "price": [100.0, 110.0, 121.0, 80.0],
                "volume": [10, 20, 30, 40],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "data.csv").write_text(raw.to_csv(index=False), encoding="utf-8")

            result = run_pipeline(base_dir=base)

            for name in [
                "v1_clean.csv",
                "v1_monthly_summary.csv",
                "v1_data_quality.csv",
                "v1_overall_statistics.csv",
                "v1_monthly_dashboard.png",
                "v1_report.md",
            ]:
                path = base / name
                self.assertTrue(path.is_file(), name)
                self.assertGreater(path.stat().st_size, 0, name)
            self.assertEqual(result["clean_rows"], 3)
            self.assertEqual(result["dropped_rows"], 1)
            report = (base / "v1_report.md").read_text(encoding="utf-8")
            self.assertIn("模拟数据", report)
            self.assertIn("无效或缺失日期：1 行", report)

    def test_pipeline_rejects_csv_without_valid_rows(self):
        raw = pd.DataFrame(
            {
                "date": ["bad-date"],
                "price": [-1.0],
                "volume": [-10],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "data.csv").write_text(raw.to_csv(index=False), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "清洗后没有有效记录"):
                run_pipeline(base_dir=base)


if __name__ == "__main__":
    unittest.main()
