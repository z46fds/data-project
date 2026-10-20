import akshare as ak

df = ak.stock_zh_a_hist(
    symbol="000001", period="daily",
    start_date="20230101", end_date="20231231"
)
df.to_csv("data.csv", index=False)
print("行数:", len(df))
print("列名:", df.columns.tolist())
print(df.head())
