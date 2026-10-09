# Tokenomics · 区块链经济学及应用趋势研究

> **研究笔记（Research Notes）** — 一个 *研究驱动型* 的 Portfolio。
> 这里不发布代码仓库，而是发布可复现的**经济学研究笔记**：用链上数据回答一个具体的经济学问题，并把它变成有逻辑的论点。
>
> 作者：**Bonnie Bennett** — Senior Data Analyst / Data Scientist
> 🔗 个人网站：https://dingbangbang.github.io/
>
> 🌐 语言：**中文** · [English version / 英文版 →](README_en.md)

---

## 为什么是"研究笔记"而不是"代码仓库"

我想，交易所的研究部、合规部、战略部真正稀缺的，不是"会跑数据"的人，而是**能把数据翻译成经济学论点**的人。
本仓库刻意采用一种**先提出问题 → 建立经济模型 → 用链上数据检验 → 给出政策建议**的写作范式：

- **选题聚焦**：不泛泛谈"区块链经济学"，每个 Note 只回答一个可被证伪的具体问题。
- **数据支撑**：所有结论都用公开数据（Dune Analytics / Blockchair / Binance / DefiLlama）复算，SQL 与代码全部开源。
- **输出形式**：一份 3,000–5,000 字的研究报告，含文献综述、数据可视化、结论与政策建议。

---

## 📚 研究笔记索引

| No. | 标题 | 主题 | 文档 | 核心结论 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 01 | [当 Gas 费变成"税"：EIP-1559 的销毁机制与以太坊验证者实际收益率](research/01-eip1559-gas-fee-redistribution.md) | Tokenomics · 费用市场 · 验证者收益 | [中文](research/01-eip1559-gas-fee-redistribution.md) · [EN](research/01-eip1559-gas-fee-redistribution_en.md) | 销毁并未在时序上"挤压"验证者 tip；但它相当于对验证者收入征收约 **64%（均值）的结构性税率** τ = burn/(burn+tip)——实质是把铸币税收入再分配给全体持币者。 | ✅ |
| 02 | [微观·MEV-Boost 时代的价值分配：验证者、构建者与搜索者的实证分析](research/02-mev-boost-value-distribution.md) | 微观 · MEV · PBS | [中文](research/02-mev-boost-value-distribution.md) · [EN](research/02-mev-boost-value-distribution_en.md) | PBS 时代排序权租金已从验证者转移到构建者/搜索者：**Top-3 构建者拿走约 40% 的 MEV 价值（HHI ≈ 0.09）**，验证者只拿到拍卖残余。 | ✅ |
| 03 | [流动性挖矿的补贴效率：代币激励有多少转化成了真实交易量？](research/03-liquidity-mining-subsidy-efficiency.md) | 中观 · 协议层博弈 · 代币激励 | [中文](research/03-liquidity-mining-subsidy-efficiency.md) · [EN](research/03-liquidity-mining-subsidy-efficiency_en.md) | DeFi 池子收益中位数仅 **0.6% 来自代币补贴**，但 **146 个池子 >90% 靠补贴**——补贴效率两极分化是判断协议可持续性的关键。 | ✅ |
| 04 | [高资金费率是否预示市场回调？——来自加密衍生品市场的实证](research/04-funding-rate-market-top-signal.md) | 宏观 · 衍生品 · 市场周期 | [中文](research/04-funding-rate-market-top-signal.md) · [EN](research/04-funding-rate-market-top-signal_en.md) | 日频上资金费率是**很弱的反向信号**（`corr ≈ −0.064`）；它是"拥挤度"指标，而非可靠的择时开关。 | ✅ |

后续计划中的选题：

- **05** — L2 的"数据税"：Blob 空间定价与 Rollup 成本转嫁
- **06** — 质押收益率的期限结构：共识层通胀 vs 执行层费用

---

## 📁 仓库结构

```
.
├── README.md                                   # 中文版主 README（本文件）
├── README_en.md                                # 英文版 README
├── research/
│   ├── 01-eip1559-gas-fee-redistribution.md        # Note 01 中文
│   ├── 01-eip1559-gas-fee-redistribution_en.md     # Note 01 EN
│   ├── 02-mev-boost-value-distribution.md          # Note 02 中文
│   ├── 02-mev-boost-value-distribution_en.md       # Note 02 EN
│   ├── 03-liquidity-mining-subsidy-efficiency.md   # Note 03 中文
│   ├── 03-liquidity-mining-subsidy-efficiency_en.md # Note 03 EN
│   ├── 04-funding-rate-market-top-signal.md        # Note 04 中文
│   └── 04-funding-rate-market-top-signal_en.md     # Note 04 EN
├── queries/                                    # 可复现的 DuneSQL 查询
├── tools/                                      # chartlib.py + build_charts.py + translate_charts.py（真实数据 → SVG）
├── assets/charts/                              # 生成的 SVG 图表（不依赖 Dune）
├── data/                                       # 抓取到的原始 JSON + 口径登记
└── references/bibliography.md                  # 参考文献（学术论文 + 链上数据源）
```

---

## 🔁 如何复现

1. 注册 [Dune Analytics](https://dune.com)，把 `queries/` 下的 SQL 逐个保存为查询并运行。
2. 在 `data/README.md` 里登记你生成的 **query ID**，替换报告正文中的 `{{dune_query_id}}` 占位符。
3. 若想**不依赖 Dune** 重新生成图表，运行本项目自带的取数+绘图管线（全部为公开、免 key 接口）：
   ```bash
   python3 tools/build_charts.py        # 抓取 Blockchair / Binance / DefiLlama / MEV relay 数据
   python3 tools/translate_charts.py    # 生成英文版图表 assets/charts/*_en.svg
   ```
   它会把原始 JSON 写入 `data/`，把 SVG 图表写入 `assets/charts/`（中文版 `*.svg` + 英文版 `*_en.svg`）。无需 API key、无需 matplotlib、无需 Dune。

## ⚖️ 免责声明

本仓库为**学术与求职作品展示**用途，所有内容仅代表个人观点，不构成任何投资、财务或法律建议。链上数据口径随时间变化，引用请注明时间点。

## 📬 联系

- Email: dingbangchu@gmail.com
- GitHub: [@DingBangBang](https://github.com/DingBangBang)
- LinkedIn: [in/bonniebennett333](https://www.linkedin.com/in/bonniebennett333/)

## 📄 许可

文字内容采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，SQL 代码采用 MIT 许可。
