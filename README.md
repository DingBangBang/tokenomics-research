# Tokenomics · 区块链经济学及应用趋势研究

> **研究笔记（Research Notes）** — 一个 *研究驱动型* 的 Portfolio。
> 这里不发布代码仓库，而是发布可复现的**经济学研究笔记**：用链上数据回答一个具体的经济学问题，并把它变成有逻辑的论点。
>
> 作者：**Bonnie Bennett** — Senior Data Analyst / Data Scientist
> 🔗 个人网站：https://dingbangbang.github.io/

---

## 为什么是"研究笔记"而不是"代码仓库"

交易所的研究部、合规部、战略部真正稀缺的，不是"会跑数据"的人，而是**能把数据翻译成经济学论点**的人。
本仓库刻意采用一种**先提出问题 → 建立经济模型 → 用链上数据检验 → 给出政策建议**的写作范式：

- **选题聚焦**：不泛泛谈"区块链经济学"，每个 Note 只回答一个可被证伪的具体问题。
- **数据支撑**：所有结论都用公开的链上数据（Dune Analytics / Etherscan）复算，SQL 全部开源。
- **输出形式**：一份 3,000–5,000 字的研究报告，含文献综述、数据可视化、结论与政策建议。

---

## 📚 研究笔记索引

| No. | 标题 | 主题 | 状态 |
| --- | --- | --- | --- |
| 01 | [当 Gas 费变成"税"：EIP-1559 的销毁机制与以太坊验证者实际收益率](research/01-eip1559-gas-fee-redistribution.md) | Tokenomics · 费用市场 · 验证者收益 | ✅ 已发布 |

后续计划中的选题：

- **02** — MEV 再分配：PBS 与 Builder 市场的价值捕获（谁拿走了排序权租金？）
- **03** — L2 的"数据税"：Blob 空间定价与 Rollup 成本转嫁
- **04** — 质押收益率的期限结构：共识层通胀 vs 执行层费用

---

## 📁 仓库结构

```
.
├── README.md                                   # 本文件：研究笔记索引
├── research/
│   └── 01-eip1559-gas-fee-redistribution.md    # Note 01 完整研究报告
├── queries/                                    # 可复现的 DuneSQL 查询
│   ├── 01_daily_gas_and_fee_decomposition.sql
│   ├── 02_burn_timeseries.sql
│   ├── 03_validator_revenue_structure.sql
│   ├── 04_burn_vs_tip_correlation.sql
│   └── 05_real_yield_and_issuance.sql
├── data/
│   └── README.md                               # 数据来源、口径、Dune 查询 ID 登记表
└── references/
    └── bibliography.md                          # 参考文献（学术论文 + 链上数据源）
```

---

## 🔁 如何复现

1. 注册 [Dune Analytics](https://dune.com)，把 `queries/` 下的 SQL 逐个保存为查询并运行。
2. 在 `data/README.md` 里登记你生成的 **query ID**，替换报告正文中的 `{{dune_query_id}}` 占位符。
3. 报告中的图表使用 Dune 官方 iframe 嵌入（见 `research/` 内 `## 数据可视化` 一节），也可直接用 Dashboards 分享链接。

## ⚖️ 免责声明

本仓库为**学术与求职作品展示**用途，所有内容仅代表个人观点，不构成任何投资、财务或法律建议。链上数据口径随时间变化，引用请注明时点。

## 📬 联系

- Email: dingbangchu@gmail.com
- GitHub: [@DingBangBang](https://github.com/DingBangBang)
- LinkedIn: [in/bonniebennett333](https://www.linkedin.com/in/bonniebennett333/)

## 📄 许可

文字内容采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，SQL 代码采用 MIT 许可。
