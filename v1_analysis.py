"""Data-project v1: cleaned, monthly analysis pipeline."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MATPLOTLIB_CACHE_DIR = BASE_DIR / ".matplotlib-cache"
MATPLOTLIB_CACHE_DIR.mkdir(exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(MATPLOTLIB_CACHE_DIR)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


REQUIRED_COLUMNS = ("date", "price", "volume")


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate required fields and keep valid, positive observations."""
    missing = [column for column in REQUIRED_COLUMNS if column not in raw.columns]
    if missing:
        raise ValueError(f"缺少必要列: {', '.join(missing)}")

    cleaned = raw.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned["price"] = pd.to_numeric(cleaned["price"], errors="coerce")
    cleaned["volume"] = pd.to_numeric(cleaned["volume"], errors="coerce")

    valid = (
        cleaned["date"].notna()
        & cleaned["price"].notna()
        & cleaned["volume"].notna()
        & (cleaned["price"] > 0)
        & (cleaned["volume"] >= 0)
    )
    cleaned = cleaned.loc[valid].sort_values("date").reset_index(drop=True)
    cleaned["month"] = cleaned["date"].dt.strftime("%Y-%m")
    return cleaned


def monthly_summary(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Aggregate prices and volume by calendar month."""
    summary = (
        cleaned.groupby("month", sort=True)
        .agg(
            observations=("price", "size"),
            average_price=("price", "mean"),
            median_price=("price", "median"),
            minimum_price=("price", "min"),
            maximum_price=("price", "max"),
            average_volume=("volume", "mean"),
            total_volume=("volume", "sum"),
        )
        .sort_index()
    )
    summary["price_change_pct"] = summary["average_price"].pct_change() * 100
    return summary


def build_report(
    summary: pd.DataFrame,
    clean_rows: int,
    dropped_rows: int,
) -> str:
    """Build a short, evidence-based Markdown report from monthly metrics."""
    if summary.empty:
        raise ValueError("月度汇总为空，无法生成报告")

    high_month = summary["average_price"].idxmax()
    low_month = summary["average_price"].idxmin()
    volume_month = summary["total_volume"].idxmax()
    changes = summary["price_change_pct"].dropna()

    change_line = "最大月均价涨幅：暂无可计算月份"
    if not changes.empty:
        change_month = changes.idxmax()
        change_line = (
            f"最大月均价涨幅：{change_month}（{changes.loc[change_month]:.2f}%）"
        )

    return "\n".join(
        [
            "# Data Project v1 分析报告",
            "",
            "## 数据概览",
            "",
            f"- 有效记录：{clean_rows} 行",
            f"- 清理剔除：{dropped_rows} 行",
            f"- 覆盖月份：{summary.index.min()} 至 {summary.index.max()}",
            "",
            "## 月度结论",
            "",
            f"- 最高月均价：{high_month}（{summary.loc[high_month, 'average_price']:.2f}）",
            f"- 最低月均价：{low_month}（{summary.loc[low_month, 'average_price']:.2f}）",
            f"- 成交量最高：{volume_month}（{summary.loc[volume_month, 'total_volume']:.0f}）",
            f"- {change_line}",
            "",
            "## 说明",
            "",
            "本报告描述样本内的价格与成交量变化，不将相关性解释为因果关系。",
            "",
        ]
    )


def run_pipeline(base_dir: str | Path | None = None) -> dict[str, object]:
    """Run the complete v1 pipeline and write reproducible artifacts."""
    base = Path(base_dir) if base_dir is not None else BASE_DIR
    input_path = base / "data.csv"
    if not input_path.is_file():
        raise FileNotFoundError(f"找不到输入文件: {input_path}")

    raw = pd.read_csv(input_path)
    cleaned = clean_data(raw)
    summary = monthly_summary(cleaned)
    dropped_rows = len(raw) - len(cleaned)

    clean_path = base / "v1_clean.csv"
    summary_path = base / "v1_monthly_summary.csv"
    chart_path = base / "v1_monthly_dashboard.png"
    report_path = base / "v1_report.md"

    cleaned.to_csv(clean_path, index=False, date_format="%Y-%m-%d")
    summary.to_csv(summary_path, index_label="month", float_format="%.6f")

    fig, (price_ax, volume_ax) = plt.subplots(
        2,
        1,
        figsize=(11, 7),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 2]},
    )
    month_labels = summary.index.tolist()
    price_ax.plot(
        month_labels,
        summary["average_price"],
        color="#1f5f8b",
        marker="o",
        linewidth=2,
    )
    price_ax.set_title("Monthly Price and Volume Overview")
    price_ax.set_ylabel("Average price")
    price_ax.grid(axis="y", alpha=0.25)

    volume_ax.bar(month_labels, summary["total_volume"], color="#72a98f")
    volume_ax.set_ylabel("Total volume")
    volume_ax.set_xlabel("Month")
    volume_ax.grid(axis="y", alpha=0.25)
    volume_ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)

    report = build_report(summary, clean_rows=len(cleaned), dropped_rows=dropped_rows)
    report_path.write_text(report, encoding="utf-8")

    return {
        "clean_rows": len(cleaned),
        "dropped_rows": dropped_rows,
        "months": len(summary),
        "clean_path": clean_path,
        "summary_path": summary_path,
        "chart_path": chart_path,
        "report_path": report_path,
    }


if __name__ == "__main__":
    result = run_pipeline()
    print(f"v1 完成：有效 {result['clean_rows']} 行，剔除 {result['dropped_rows']} 行")
    print(f"月度汇总：{result['summary_path']}")
    print(f"图表：{result['chart_path']}")
    print(f"报告：{result['report_path']}")
