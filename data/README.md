# 数据来源与口径登记表（Data Provenance）

> **重要更新（Notes 01–04 的实际口径）**：报告中的全部图表**不依赖 Dune**，而是由本仓库自带的免 key 管线 [`../tools/build_charts.py`](../tools/build_charts.py) 实时抓取并渲染为 SVG。原始 JSON 见本目录 `n0X_*.json`，统计摘要见 `summary_0X.json`。

## 0. 免 key 实时数据管线（本次实际使用）

| 报告 | 数据源（公开、免 key） | 关键接口 | 原始文件 |
| --- | --- | --- | --- |
| Note 01 以太坊费用/销毁 | Blockchair aggregated API | `/ethereum/blocks?a=date,sum(gas_used),avg(base_fee_per_gas)`；`/ethereum/transactions?a=date,sum(gas_used),avg(gas_price)` | `n01_daily_fees.json` |
| Note 02 MEV-Boost | Flashbots / ultrasound / Agnostic / Aestus / Titan relay | `/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100` | `n02_mev_blocks.json`、`n02_relay_summary.json` |
| Note 03 DeFi 补贴/费用 | DefiLlama 开放 API | `/summary/fees/{protocol}?dataType=dailyFees`；`yields.llama.fi/pools` | `n03_protocol_fees.json`、`n03_pools_sample.json` |
| Note 04 资金费率/价格 | Hyperliquid info API（POST） | `fundingHistory`、`candleSnapshot` | `n04_funding.json`、`n04_candles.json` |

**说明**：部分交易域（Binance/OKX/Bybit）在直连时会被网络重置，管线优先使用 `curl`，并在需要时经由本机代理（`http://127.0.0.1:7897`）；Note 04 因此改用可稳定访问的 Hyperliquid。

**复现**：
```bash
python3 tools/build_charts.py           # 运行全部 01–04
python3 tools/build_charts.py 02 04     # 只运行指定笔记
```

---

## 1. 数据集（Dune 口径，供可选复算）

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
