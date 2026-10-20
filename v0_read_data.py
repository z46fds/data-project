"""v0: 读入 CSV，做描述性统计，画一张直方图。"""
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data.csv")
print("行数:", len(df))
print("列名:", list(df.columns))

num_cols = df.select_dtypes(include="number").columns
if len(num_cols) == 0:
    raise SystemExit("这份数据里没有数值列，换一份数据")

col = num_cols[0]
print(f"\n统计列: {col}")
print("均值:  ", round(df[col].mean(), 2))
print("标准差:", round(df[col].std(), 2))
print("最小值:", df[col].min())
print("最大值:", df[col].max())

df[col].hist(bins=30)
plt.title(f"Distribution of {col}")
plt.xlabel(col)
plt.ylabel("count")
plt.tight_layout()
plt.savefig("hist.png", dpi=150)
print("\n图已保存: hist.png")
