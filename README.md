# 金融数据分析练习

用 pandas 读取数据集，做描述性统计与可视化。

当前包含两个可复现阶段：

- **v0**：读取 CSV，完成基础描述性统计和直方图。
- **v1**：清洗数据，按月聚合价格与成交量，生成图表和文字结论。

## 环境

- Python 3.14
- 依赖见 `requirements.txt`

## 运行

```bash
python3 -m pip install -r requirements.txt
python3 v0_read_data.py
python3 v1_analysis.py
```

## 输出

| 文件 | 内容 |
| --- | --- |
| `hist.png` | 指定数值列的直方图（30 个区间） |
| `summary.txt` | 数据行数、列名、均值、标准差、最小值、最大值 |
| `v1_clean.csv` | 完成日期解析、类型转换和无效记录剔除后的数据 |
| `v1_monthly_summary.csv` | 月度观测数、均价、中位数、极值、成交量与月均价涨幅 |
| `v1_data_quality.csv` | 无效日期、缺失或非法数值、非正价格、负成交量及重复记录统计 |
| `v1_overall_statistics.csv` | 总体价格、成交量、时间范围和价格—成交量相关系数 |
| `v1_monthly_dashboard.png` | 月均价走势与月度成交量双面板图 |
| `v1_report.md` | 数据来源、质量、总体指标、月度结论与限制说明 |

终端会同时打印同样的统计结果。

## 目录结构

```
data-project/
├── data.csv            # 数据集，200 行
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
└── README.md
```

## 数据来源

`data.csv` 是由脚本生成的模拟价格数据，200 行。

真实数据获取脚本为 `fetch_data.py`，因接口不稳定，本仓库默认使用可复现的模拟数据。

## v1 口径

- 日期无法解析、价格或成交量无法转成数字的记录会被剔除。
- 价格必须大于 0，成交量不得小于 0。
- 完全重复记录只统计、不自动删除，避免误删合法的同日期观测。
- 月度价格变化率以上月平均价格为基准；第一个月没有变化率。
- 价格与成交量相关系数只描述样本关系，不代表因果关系。

## 说明

- `data.csv` 是可复现的模拟价格数据，仅用于验证分析流程，不代表真实市场结论。
- 脚本使用 matplotlib 的 `Agg` 后端，可在无图形界面的终端中直接运行，不会弹出窗口。

## 测试

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖必填列检查、日期与数值清洗、月度聚合、结论生成，以及完整运行后所有输出文件的生成。
