# v1 数据字典

## 1. 输入文件

### `data.csv`

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `date` | 日期字符串 | 可被 `pandas.to_datetime` 解析 | 观测日期，输出时统一为 `YYYY-MM-DD` |
| `price` | 数值 | 大于 0 | 当期价格；真实股票数据默认取收盘价 |
| `volume` | 数值 | 大于等于 0 | 当期成交量 |

允许存在额外字段，但 v1 的清洗和统计只依赖上述三个字段。无效日期、
非数值、非正价格和负成交量会被剔除，并在 `v1_data_quality.csv` 中计数。

### `data_metadata.json`

| 字段 | 类型 | 说明 |
|---|---|---|
| `source` | 字符串 | 数据来源，例如 AkShare 或模拟数据 |
| `source_note` | 字符串 | 写入分析报告的数据来源说明 |
| `symbol` | 字符串，可选 | 股票代码 |
| `start_date` | 字符串，可选 | 数据请求起始区间 |
| `end_date` | 字符串，可选 | 数据请求结束区间 |
| `rows` | 整数，可选 | 数据行数 |
| `fields` | 数组，可选 | 标准字段清单 |

## 2. 输出文件

### `v1_clean.csv`

输入有效字段的清洗结果，并新增 `month` 字段，格式为 `YYYY-MM`。

### `v1_monthly_summary.csv`

| 字段 | 说明 |
|---|---|
| `month` | 自然月 |
| `observations` | 当月有效观测数 |
| `average_price` | 月均价格 |
| `median_price` | 月价格中位数 |
| `minimum_price` | 月最低价格 |
| `maximum_price` | 月最高价格 |
| `average_volume` | 月均成交量 |
| `total_volume` | 月成交量之和 |
| `price_change_pct` | 月均价格相对上月的百分比变化；首月为空 |

### `v1_data_quality.csv`

| 字段 | 说明 |
|---|---|
| `raw_rows` | 原始行数 |
| `clean_rows` | 清洗后有效行数 |
| `dropped_rows` | 剔除行数 |
| `invalid_or_missing_date` | 无效或缺失日期数 |
| `invalid_or_missing_price` | 无效或缺失价格数 |
| `invalid_or_missing_volume` | 无效或缺失成交量数 |
| `nonpositive_price` | 非正价格数 |
| `negative_volume` | 负成交量数 |
| `duplicate_rows` | 完全重复行数；只统计，不自动删除 |

### `v1_overall_statistics.csv`

总体有效观测数、时间范围、价格均值/中位数/标准差/范围、成交量均值/合计，
以及价格和成交量的 Pearson 相关系数。

### `v1_monthly_dashboard.png`

上方面板为月均价折线图，下方面板为月成交量柱状图。

### `v1_report.md`

根据数据质量、总体统计与月度结果自动生成的分析报告，包括数据来源和限制说明。

## 3. 统计口径

- 月份按日期所属自然月聚合。
- 月均价变化率使用 `(本月均价 / 上月均价 - 1) * 100`。
- 相关系数仅用于描述样本内的线性关系，不代表因果关系。
- 默认数据为模拟数据，不能用于投资决策或真实市场结论。
