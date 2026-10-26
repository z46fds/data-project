# 金融数据分析练习

用 pandas 读取数据集，做描述性统计与可视化。

这是主线项目的 **v0**：把真实数据读进来，算出统计量，画出一张图。

## 环境

- Python 3.14
- 依赖见 `requirements.txt`

## 运行

```bash
python3 -m pip install -r requirements.txt
python3 v0_read_data.py
```

## 输出

| 文件 | 内容 |
| --- | --- |
| `hist.png` | 指定数值列的直方图（30 个区间） |
| `summary.txt` | 数据行数、列名、均值、标准差、最小值、最大值 |

终端会同时打印同样的统计结果。

## 目录结构

```
data-project/
├── data.csv            # 数据集，200 行
├── fetch_data.py       # 获取真实数据的脚本
├── v0_read_data.py     # v0 主脚本：读数据 + 统计 + 画图
├── requirements.txt    # 依赖清单
├── hist.png            # 生成物：直方图
├── summary.txt         # 生成物：统计摘要
└── README.md
```

## 数据来源

`data.csv` 是由脚本生成的模拟价格数据，200 行。

真实数据获取脚本为 `fetch_data.py`，因接口不稳定，本仓库默认使用可复现的模拟数据。

## 说明

脚本使用 matplotlib 的 `Agg` 后端，可在无图形界面的终端中直接运行，不会弹出窗口。
