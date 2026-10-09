# Tokenomics · Research Notes on Blockchain Economics & Trends

> **Research Notes** — a *research-driven* portfolio.
> This repo does not ship a codebase; it ships **reproducible economics research notes**: each one answers a specific economic question with on-chain data and turns the data into an argument.
>
> Author: **Bonnie Bennett** — Senior Data Analyst / Data Scientist
> 🔗 Personal site: https://dingbangbang.github.io/
>
> 🌐 Language: **English** · [中文版](README.md)

---

## Why "research notes" instead of a code repository

What research, compliance and strategy desks at exchanges actually lack is not people who *can run data*, but people who can **translate data into an economic argument**.
This repository deliberately follows one writing pattern: **pose a question → build an economic model → test it with on-chain data → give policy recommendations**.

- **Focused topics** — no hand-wavy "blockchain economics"; each note answers a single falsifiable question.
- **Data-backed** — every claim is recomputed from public data (Dune Analytics / Blockchair / Binance / DefiLlama); all SQL and code are open.
- **Deliverable** — a 3,000–5,000-word research report with a literature review, data visualisations, conclusions and policy recommendations.

---

## 📚 Index of research notes

| No. | Title | Topic | Documents | Key finding (one-liner) | Status |
| --- | --- | --- | --- | --- | --- |
| 01 | [When Gas Fees Become a Tax: EIP-1559's Burn Mechanism and Ethereum Validator Real Yield](research/01-eip1559-gas-fee-redistribution.en.md) | Tokenomics · Fee market · Validator revenue | [中文](research/01-eip1559-gas-fee-redistribution.md) · [EN](research/01-eip1559-gas-fee-redistribution.en.md) | The burn does not squeeze tips in the time series, but it imposes a **structural tax of ~64% (mean)** τ = burn/(burn+tip) on validator revenue — seigniorage redistributed to all holders. | ✅ |
| 02 | [Value Distribution in the MEV-Boost Era: Validators, Builders and Searchers](research/02-mev-boost-value-distribution.en.md) | Micro · MEV · PBS | [中文](research/02-mev-boost-value-distribution.md) · [EN](research/02-mev-boost-value-distribution.en.md) | Under PBS, ordering-rights rent has migrated from validators to builders/searchers: the **top-3 builders capture ~40% of MEV value (HHI ≈ 0.09)**; validators get the auction residual. | ✅ |
| 03 | [The Subsidy Efficiency of Liquidity Mining: How Much Incentive Becomes Real Volume?](research/03-liquidity-mining-subsidy-efficiency.en.md) | Meso · Protocol games · Token incentives | [中文](research/03-liquidity-mining-subsidy-efficiency.md) · [EN](research/03-liquidity-mining-subsidy-efficiency.en.md) | The median DeFi pool yield is only **0.6% subsidised**, yet **146 pools are >90% subsidised** — this polarisation key to protocol sustainability. | ✅ |
| 04 | [Does High Funding Predict a Pullback? Evidence from Crypto Derivatives](research/04-funding-rate-market-top-signal.en.md) | Macro · Derivatives · Market cycle | [中文](research/04-funding-rate-market-top-signal.md) · [EN](research/04-funding-rate-market-top-signal.en.md) | At the daily horizon funding is a **very weak contrarian signal** (`corr ≈ −0.064`) — a crowding gauge, not a reliable timing switch. | ✅ |

Planned topics:

- **05** — The L2 "data tax": blob-space pricing and rollup cost pass-through
- **06** — The term structure of staking yield: consensus issuance vs execution-layer fees

---

## 📁 Repository structure

```
.
├── README.md                                   # 中文版主 README
├── README.en.md                                # this file (English)
├── research/
│   ├── 01-eip1559-gas-fee-redistribution.md        # Note 01 (中文)
│   ├── 01-eip1559-gas-fee-redistribution.en.md     # Note 01 (English)
│   ├── 02-mev-boost-value-distribution.md          # Note 02 (中文)
│   ├── 02-mev-boost-value-distribution.en.md       # Note 02 (English)
│   ├── 03-liquidity-mining-subsidy-efficiency.md   # Note 03 (中文)
│   ├── 03-liquidity-mining-subsidy-efficiency.en.md # Note 03 (English)
│   ├── 04-funding-rate-market-top-signal.md        # Note 04 (中文)
│   └── 04-funding-rate-market-top-signal.en.md     # Note 04 (English)
├── queries/                                    # reproducible DuneSQL queries
├── tools/                                      # chartlib.py + build_charts.py (real data → SVG)
├── assets/charts/                              # generated SVG charts (no Dune needed)
├── data/                                       # raw JSON data + provenance
└── references/bibliography.md                  # academic papers + data sources
```

---

## 🔁 How to reproduce

1. Register on [Dune Analytics](https://dune.com) and save each SQL under `queries/` as a query.
2. Register your **query IDs** in `data/README.md` and replace the `{{dune_query_id}}` placeholders in the report text.
3. To regenerate the charts **without Dune**, run our own pipeline (public, key-less APIs):
   ```bash
   python3 tools/build_charts.py        # fetches Blockchair / Binance / DefiLlama / MEV relay data
   ```
   This writes raw JSON into `data/` and renders `assets/charts/*.svg`. No API keys, no matplotlib, no Dune.

## ⚖️ Disclaimer

This repository is for **academic and job-application portfolio** purposes. All content represents the author's personal views and is not investment, financial or legal advice. On-chain data is time-sensitive; cite its snapshot date.

## 📬 Contact

- Email: dingbangchu@gmail.com
- GitHub: [@DingBangBang](https://github.com/DingBangBang)
- LinkedIn: [in/bonniebennett333](https://www.linkedin.com/in/bonniebennett333/)

## 📄 License

Text is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); SQL and code under MIT.
