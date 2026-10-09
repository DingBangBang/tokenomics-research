# 数据来源与口径登记表（Data Provenance）

本文件用于登记每一项结论背后的**数据来源、口径、Dune 查询 ID 与快照时点**，保证研究可复现。

## 1. 数据集

| 数据 | Dune 表 / 平台 | 关键字段 | 说明 |
| --- | --- | --- | --- |
| 区块级费用 | `ethereum.blocks` | `time, number, gas_used, gas_limit, base_fee_per_gas` | base fee 时间序列的权威来源 |
| 交易级费用 | `ethereum.transactions` | `block_time, gas_used, base_fee_per_gas, priority_fee_per_gas, effective_gas_price, success` | tip 与总费用的分解来源 |
| 验证者发行奖励 | `beacon.validator_income` | `block_date, validator_index, income (Gwei)` | 共识层发行奖励（Merge 后） |
| 费用市场总览 | `gas.fees` (spellbook) | `blockchain, block_time, gas_used, gas_price, priority_fee` | 多链统一的费用表，可交叉校验 |
| MEV | Dune `mev` 数据集 / Flashbots | `block_number, value` | 补充执行层 MEV 收入 |
| 供应量 | `ethereum.supply` / Etherscan `ETH Supply` | — | 计算净发行与稀释率的真实分母 |

## 2. Dune 查询 ID 登记表

> 用 `queries/` 下的 SQL 在 Dune 上创建查询后，把生成的 **query ID / result ID** 填回下表，并同步替换报告正文里的 `{{...}}` 占位符。

| 查询文件 | Dune Query ID | Result ID | 是否用于正文图表 | 快照时点 |
| --- | --- | --- | --- | --- |
| `01_daily_gas_and_fee_decomposition.sql` | {{dune_query_id_01}} | {{dune_result_id_01}} | ✅ 图 6-1 | — |
| `02_burn_timeseries.sql` | {{dune_query_id_02}} | {{dune_result_id_02}} | ✅ 图 6-2 | — |
| `03_validator_revenue_structure.sql` | {{dune_query_id_03}} | {{dune_result_id_03}} | ✅ 图 6-3 | — |
| `04_burn_vs_tip_correlation.sql` | {{dune_query_id_04}} | {{dune_result_id_04}} | ✅ 表 6-1 | — |
| `05_real_yield_and_issuance.sql` | {{dune_query_id_05}} | {{dune_result_id_05}} | ✅ 图 6-4 | — |

## 3. 口径说明（务必先读）

1. **成功交易**：费用分解仅统计 `success = true` 的交易，避免失败交易的高 gas price 污染 tip 均值。
2. **时区**：所有 `DATE_TRUNC('day', ...)` 均使用 UTC。
3. **单位**：链上金额统一以 **WEI / Gwei** 存储，除以 `1e18` 得到 ETH，除以 `1e9` 得到 Gwei；`beacon.validator_income.income` 单位为 **Gwei**。
4. **Merge 分界**：执行层 tip 收入仅在 PoS（2022-09-15 之后）归属于验证者；此前归矿工。
5. **MEV 归属**：MEV-boost 的区块奖励经由 relay 支付给 proposer，未包含在 `priority_fee_per_gas` 中，需单独补充，否则会低估执行层收入。
6. **流通量**：实际收益率的分母应使用真实流通供应量，查询 05 中示例使用固定值，正式发布时须替换为 `ethereum.supply`。

## 4. 已知局限

- Dune 的 `priority_fee_per_gas` 在极早期区块可能缺失，需用 `gas_price - base_fee_per_gas` 回退。
- 销毁量口径存在"是否计入手续费燃烧 vs blob burn"的差异，跨源比较时需对齐。
- 本仓库数值为**快照**，随时间变化；引用请以最新 Dune 查询为准。
