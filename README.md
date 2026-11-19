# 金融时间序列描述性分析 v1

用 pandas 完成数据质量检查、清洗、月度聚合和可视化，并用一套可重复命令重新生成全部结果。

当前包含两个可复现阶段：

- **v0**：读取 CSV，完成基础描述性统计和直方图。
- **v1**：清洗数据，按月聚合价格与成交量，生成图表和文字结论。

## 环境

- Python 3.14
- 依赖见 `requirements.txt`

## 运行

```bash
python3 -m pip install -r requirements.txt
python3 v1_analysis.py
```

只运行 v1 时，第二条命令即可完成全部分析并覆盖对应结果文件。

## 输入数据

v1 读取项目根目录的 `data.csv`，最低要求如下：

| 字段 | 类型 | 约束 | 含义 |
|---|---|---|---|
| `date` | 日期字符串 | 可被 pandas 解析 | 观测日期 |
| `price` | 数值 | 必须大于 0 | 当期价格 |
| `volume` | 数值 | 必须大于等于 0 | 当期成交量 |

完整输入、输出说明见 [DATA_DICTIONARY.md](DATA_DICTIONARY.md)。

## 输出

| 文件 | 内容 |
| --- | --- |
| `hist.png` | v0 生成：指定数值列的直方图（30 个区间） |
| `summary.txt` | v0 生成：数据行数、列名、均值、标准差、最小值、最大值 |
| `v1_clean.csv` | 完成日期解析、类型转换和无效记录剔除后的数据 |
| `v1_monthly_summary.csv` | 月度观测数、均价、中位数、极值、成交量与月均价涨幅 |
| `v1_data_quality.csv` | 无效日期、缺失或非法数值、非正价格、负成交量及重复记录统计 |
| `v1_overall_statistics.csv` | 总体价格、成交量、时间范围和价格—成交量相关系数 |
| `v1_monthly_dashboard.png` | 月均价走势与月度成交量双面板图 |
| `v1_report.md` | 数据来源、质量、总体指标、月度结论与限制说明 |

v1 运行结束时，终端会打印完成状态和输出路径。

## 目录结构

```
data-project/
├── data.csv            # 默认模拟数据集，200 行
├── data_metadata.json  # 数据来源与口径说明
├── fetch_data.py       # 获取真实数据的脚本
├── v0_read_data.py     # v0 主脚本：读数据 + 统计 + 画图
├── v1_analysis.py      # v1 主脚本：清洗 + 月度聚合 + 图表 + 报告
├── tests/              # v1 自动化测试
├── requirements.txt    # 依赖清单
├── hist.png            # 生成物：直方图
├── summary.txt         # 生成物：统计摘要
├── v1_clean.csv        # 生成物：清洗结果
├── v1_monthly_summary.csv
├── v1_data_quality.csv
├── v1_overall_statistics.csv
├── v1_monthly_dashboard.png
├── v1_report.md
├── README.md
├── DATA_DICTIONARY.md
├── QFFE_PYTHON_CHECKLIST.md
└── V1_ACCEPTANCE.md
```

## 数据来源

仓库默认 `data.csv` 是可复现的模拟价格数据，共 200 行，仅用于验证分析流程。

如需替换为真实 A 股日线数据：

```bash
python3 fetch_data.py \
  --symbol 000001 \
  --start-date 20230101 \
  --end-date 20231231
```

脚本会把 AkShare 的“日期、收盘、成交量”标准化为 v1 所需的
`date,price,volume`，并同步更新 `data_metadata.json`。数据接口可能临时不可用，
因此仓库保留模拟数据作为离线可复现基线。

## v1 口径

- 日期无法解析、价格或成交量无法转成数字的记录会被剔除。
- 价格必须大于 0，成交量不得小于 0。
- 完全重复记录只统计、不自动删除，避免误删合法的同日期观测。
- 月度价格变化率以上月平均价格为基准；第一个月没有变化率。
- 价格与成交量相关系数只描述样本关系，不代表因果关系。

## 说明

- `data.csv` 是可复现的模拟价格数据，仅用于验证分析流程，不代表真实市场结论。
- 脚本使用 matplotlib 的 `Agg` 后端，可在无图形界面的终端中直接运行，不会弹出窗口。
- 相关系数只描述当前样本中的线性关系，不代表因果关系或可交易信号。
- 月均价变化率以上月均价为基准，首月为空值。
- 数据量有限时，月末统计容易受个别异常观测影响。

## 测试

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖输入列校验、日期与数值清洗、数据来源覆盖、月度聚合、结论生成，
以及完整运行后所有输出文件的生成。验收记录见 [V1_ACCEPTANCE.md](V1_ACCEPTANCE.md)。
