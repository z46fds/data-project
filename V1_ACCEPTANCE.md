# v1 验收记录

- 验收日期：2026-11-19
- Python：3.14.7
- 输入：`data.csv`
- 原始记录：200 行
- 有效记录：200 行
- 剔除记录：0 行
- 覆盖月份：2026-01 至 2026-12
- 自动化测试：19 项，全部通过
- 真实接口回退验证：东方财富接口断开时，Sina 回退成功获取 7 行测试数据
- 连续执行两次：6 个输出文件 SHA-256 完全一致

## 运行命令

```bash
python3 v1_analysis.py
```

## 测试命令

```bash
python3 -m unittest discover -s tests -v
```

## 验收结果

- `v1_clean.csv`、`v1_monthly_summary.csv`、`v1_data_quality.csv`、
  `v1_overall_statistics.csv`、`v1_monthly_dashboard.png`、`v1_report.md`
  均能自动重新生成。
- 输入缺少必要列、数据全部无效、来源说明缺失等失败路径均有测试或安全默认值。
- 真实数据获取脚本会把 AkShare 的“日期、收盘、成交量”转换为统一字段。
- AkShare 东方财富接口不可用时，会自动尝试 Sina 接口。
- README 已包含运行命令、输入约束、输出说明和限制条件。

## 已知限制

- 默认数据为模拟数据，结论只用于验证分析流程。
- 当前只做描述性统计，不做因果推断或交易策略评价。
- 当前是单表离线分析，尚未加入 SQL、统计模型和回测模块。
