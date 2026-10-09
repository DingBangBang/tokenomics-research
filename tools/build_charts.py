#!/usr/bin/env python3
"""
build_charts.py — fetch REAL on-chain data (no Dune, no API keys) and render
the SVG charts used by the research notes.

Data sources (all public, no key):
  · Ethereum gas / burn  -> Blockchair aggregated API (ethereum/blocks, .../transactions)
  · MEV-Boost bids       -> Flashbots / ultrasound / Agnostic relay public bidtrace API
  · DeFi fees & yields   -> DefiLlama open API
  · Funding rates/prices -> Binance USDⓈ-M Futures public API

Run:  python3 tools/build_charts.py
Outputs: data/*.json (raw), assets/charts/*.svg (rendered)
"""
import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime, timezone

import chartlib as c

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
CHARTS = os.path.join(ROOT, "assets", "charts")
os.makedirs(DATA, exist_ok=True)
os.makedirs(CHARTS, exist_ok=True)


def _try_urllib(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": "research-notes/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


PROXY = "http://127.0.0.1:7897"  # local Clash/mixed proxy; helps domains reset on direct connect


def _try_curl(url, timeout=50, proxy=None):
    cmd = ["curl", "-sS", "--http1.1", "--max-time", str(timeout),
           "-H", "User-Agent: research-notes/1.0"]
    if proxy:
        cmd += ["-x", proxy]
    cmd.append(url)
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode == 0 and p.stdout.strip():
        return json.loads(p.stdout)
    raise RuntimeError(p.stderr.strip() or f"curl rc={p.returncode}")


def fetch_curl_only(url, timeout=12, tries=1):
    """Fast fetch for endpoints that may hang; tries the local proxy first."""
    last = None
    for _ in range(tries):
        for proxy in (PROXY, None):
            try:
                return _try_curl(url, timeout=timeout, proxy=proxy)
            except Exception as e:  # noqa: BLE001
                last = e
                time.sleep(0.4)
    raise RuntimeError(f"curl-only fetch failed: {url} :: {last}")


def fetch(url, tries=4):
    """Fetch JSON robustly. The curl CLI is tried first because some exchange
    endpoints reject/hang Python's TLS handshake; urllib is a fallback."""
    last = None
    for i in range(tries):
        for fn in (_try_curl, _try_urllib, _try_curl):
            try:
                return fn(url)
            except Exception as e:  # noqa: BLE001
                last = e
        time.sleep(1.2 * (i + 1))
    raise RuntimeError(f"fetch failed: {url} :: {last}")


def save_json(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def save_svg(name, svg):
    with open(os.path.join(CHARTS, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print("  wrote", name, f"({len(svg)} bytes)")


def month_ranges(start="2021-08-05", end=None):
    end = end or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    out = []
    y, m = s.year, s.month
    while (y, m) <= (e.year, e.month):
        first = f"{y:04d}-{m:02d}-01"
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        last = (datetime(ny, nm, 1)).strftime("%Y-%m-%d")
        out.append((max(first, start), min(last, end)))
        y, m = ny, nm
    return out


def note01():
    print("NOTE 01 · Blockchair gas/burn …")
    end = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rng = f"2021-08-05..{end}"
    db = fetch("https://api.blockchair.com/ethereum/blocks?a=date,sum(gas_used),"
               f"avg(base_fee_per_gas)&q=time({rng})&limit=2000").get("data", [])
    dt = {r["date"]: r for r in fetch(
        "https://api.blockchair.com/ethereum/transactions?a=date,sum(gas_used),"
        f"avg(gas_price)&q=time({rng})&limit=2000").get("data", [])}
    daily = {}
    for r in db:
        day = r["date"]
        gas = r.get("sum(gas_used)") or 0
        bfee = r.get("avg(base_fee_per_gas)") or 0
        gp = (dt.get(day) or {}).get("avg(gas_price)") or 0
        burn = gas * bfee / 1e18
        total = gas * gp / 1e18
        daily[day] = {"gas_used": gas, "burn": burn, "total_fee": total,
                      "tip": max(total - burn, 0.0), "base_fee_gwei": bfee / 1e9,
                      "gas_price_gwei": gp / 1e9}
    save_json("n01_daily_fees.json", daily)

    mon = {}
    for d in sorted(daily):
        m = mon.setdefault(d[:7], {"burn": 0.0, "tip": 0.0, "total": 0.0, "bfee": []})
        r = daily[d]
        m["burn"] += r["burn"]; m["tip"] += r["tip"]; m["total"] += r["total_fee"]
        m["bfee"].append(r["base_fee_gwei"])
    keys = sorted(mon)
    lab = [k.replace("-", "/")[2:] for k in keys]
    burn_m = [mon[k]["burn"] for k in keys]
    tip_m = [mon[k]["tip"] for k in keys]
    tau_m = [mon[k]["burn"] / mon[k]["total"] * 100 if mon[k]["total"] else 0 for k in keys]
    bfee_m = [sum(mon[k]["bfee"]) / len(mon[k]["bfee"]) for k in keys]
    cum, run = [], 0.0
    for k in keys:
        run += mon[k]["burn"]; cum.append(run)

    save_svg("n01_01_monthly_burn.svg", c.line_chart(
        lab, [("Monthly ETH burned", burn_m)],
        "EIP-1559 月度 ETH 销毁量", "Monthly ETH burned by the base-fee mechanism (real, Blockchair)",
        "图 1-1 · 月度销毁量 · 数据: Blockchair aggregated API · 估算口径: avg(base_fee_per_gas) × Σ gas_used",
        ylabel="ETH burned / month"))
    save_svg("n01_02_cumulative_burn.svg", c.line_chart(
        lab, [("Cumulative ETH burned", cum)],
        "累计销毁量（通缩型财政政策的规模）", "Cumulative ETH burned since EIP-1559 (real)",
        "图 1-2 · 累计销毁量 · 数据: Blockchair · 估算口径同上",
        ylabel="ETH (cumulative)"))
    save_svg("n01_03_tau_time.svg", c.line_chart(
        lab, [("tau = burn / total fee (%)", tau_m)],
        "结构性税率 τ 的时间序列", "Share of fees burned rather than paid to producers (real, estimated)",
        "图 1-3 · τ = burn / (burn + tip) · 数据: Blockchair blocks + transactions",
        ylabel="τ (%)"))
    save_svg("n01_04_fee_decomposition.svg", c.line_chart(
        lab, [("Burned (burn)", burn_m), ("Paid to producers (tip)", tip_m)],
        "费用拆分：销毁 vs 验证者收入", "Monthly fee split between burn and producer tips (real)",
        "图 1-4 · 费用分解 · 数据: Blockchair",
        ylabel="ETH / month"))
    save_svg("n01_05_tau_vs_congestion.svg", c.scatter_chart(
        [("month", bfee_m, tau_m)],
        "τ 与拥堵（平均 base fee）的关系", "Structural tax τ vs congestion: τ rises with base fee",
        "图 1-5 · τ vs 平均 base fee · 数据: Blockchair · 每点 = 一个月",
        xlabel="平均 base fee (Gwei)", ylabel="τ (%)"))
    return {
        "days": len(daily), "months": len(keys),
        "cum_burn_eth": round(run, 1),
        "tau_mean": round(sum(tau_m) / len(tau_m), 2),
        "tau_min": round(min(tau_m), 2), "tau_max": round(max(tau_m), 2),
        "tip_total_eth": round(sum(tip_m), 1),
        "first_month": keys[0], "last_month": keys[-1],
    }


# ============================================================
# NOTE 02 — MEV-Boost value distribution (relay bidtrace APIs)
# ============================================================
RELAYS = {
    "Flashbots": "https://boost-relay.flashbots.net",
    "ultrasound": "https://relay.ultrasound.money",
    "Agnostic": "https://agnostic-relay.net",
    "Aestus": "https://aestus.live",
    "Titan": "https://titanrelay.xyz",
}
BIDTRACE = "/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"


def note02():
    print("NOTE 02 · MEV-Boost relay bids …")
    by_relay, allrows = {}, []
    for name, base in RELAYS.items():
        try:
            rows = fetch_curl_only(base + BIDTRACE, timeout=14, tries=1)
        except Exception as e:  # noqa: BLE001
            print("  relay fail", name, e)
            continue
        if not isinstance(rows, list):
            continue
        vals = []
        for r in rows:
            try:
                v = int(r["value"]) / 1e18
            except Exception:  # noqa: BLE001
                continue
            rec = {"relay": name, "value": v, "gas_used": int(r.get("gas_used") or 0),
                   "num_tx": int(r.get("num_tx") or 0), "builder": r.get("builder_pubkey", "")}
            allrows.append(rec)
            vals.append(v)
        if vals:
            by_relay[name] = {"n": len(vals), "avg": sum(vals) / len(vals),
                              "max": max(vals), "min": min(vals)}
        time.sleep(0.3)
    save_json("n02_mev_blocks.json", allrows)
    save_json("n02_relay_summary.json", by_relay)
    vals_all = [r["value"] for r in allrows]

    save_svg("n02_01_mev_value_hist.svg", c.histogram(
        vals_all, "区块 MEV 价值分布（proposer payload value）",
        "Distribution of per-block MEV value delivered by builders (ETH, real, recent sample)",
        "图 2-1 · 每区块 MEV 价值分布 · 数据: MEV-Boost relay 公开 bidtrace API · 样本 = 各 relay 最近 100 块",
        bins=24, xlabel="MEV value per block (ETH)"))

    agg = {}
    for r in allrows:
        b = agg.setdefault(r["builder"], {"n": 0, "value": 0.0})
        b["n"] += 1; b["value"] += r["value"]
    tot_v = sum(b["value"] for b in agg.values()) or 1
    top = sorted(agg.items(), key=lambda kv: kv[1]["value"], reverse=True)[:10]
    save_svg("n02_02_builder_concentration.svg", c.bar_chart(
        [k[:12] for k, _ in top], [("value share %", [v["value"] / tot_v * 100 for _, v in top])],
        "构建者集中度：Top-10 拿走的价值份额",
        "Concentration of MEV value among top builders (real)",
        "图 2-2 · 构建者价值份额 · 数据: relay bidtrace · 标签为 builder_pubkey 前 12 位",
        ylabel="share of MEV value (%)", show_every=1))

    save_svg("n02_03_value_vs_gas.svg", c.scatter_chart(
        [("block", [r["gas_used"] / 1e6 for r in allrows], [r["value"] for r in allrows])],
        "MEV 价值 vs 区块 gas 使用量",
        "MEV value vs gas used per block (loose relationship)",
        "图 2-3 · MEV vs gas_used · 数据: relay bidtrace",
        xlabel="gas_used (M gas)", ylabel="MEV value (ETH)"))

    rnames = list(by_relay.keys())
    save_svg("n02_04_relay_avg_value.svg", c.bar_chart(
        rnames, [("avg MEV per block (ETH)", [by_relay[n]["avg"] for n in rnames])],
        "各 relay 的单区块平均 MEV 价值",
        "Average MEV value per block by relay (real, recent sample)",
        "图 2-4 · relay 对比 · 数据: 各 relay 公开 API · 每 relay 最近 100 块",
        ylabel="avg MEV (ETH)", show_every=1))

    shares = [v["value"] / tot_v for _, v in agg.items()]
    return {
        "blocks": len(allrows), "relays": list(by_relay.keys()),
        "avg_block_mev_eth": round(sum(vals_all) / len(vals_all), 4) if vals_all else 0,
        "max_block_mev_eth": round(max(vals_all), 3) if vals_all else 0,
        "builders_seen": len(agg),
        "hhi": round(sum(s * s for s in shares), 4),
        "top3_value_share_pct": round(sum(sorted(shares, reverse=True)[:3]) * 100, 1),
        "relay_summary": {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in by_relay.items()},
    }


# ============================================================
# NOTE 03 — Liquidity-mining subsidy efficiency (DefiLlama)
# ============================================================
FEE_PROTOCOLS = ["uniswap", "curve-dex", "aave", "lido", "compound-finance",
                 "pancakeswap-amm", "balancer", "sushiswap", "gmx", "pendle",
                 "eigenlayer", "ethena"]


def note03():
    print("NOTE 03 · DefiLlama fees & yields …")
    fees = {}
    for slug in FEE_PROTOCOLS:
        try:
            d = fetch(f"https://api.llama.fi/summary/fees/{slug}?dataType=dailyFees")
            fees[d.get("name", slug)] = {
                "total30d": d.get("total30d") or 0,
                "total7d": d.get("total7d") or 0,
                "totalAllTime": d.get("totalAllTime") or 0,
                "chart": d.get("totalDataChart") or [],
            }
        except Exception as e:  # noqa: BLE001
            print("  fees fail", slug, e)
        time.sleep(0.2)
    save_json("n03_protocol_fees.json", {k: {kk: vv for kk, vv in v.items() if kk != "chart"}
                                         for k, v in fees.items()})

    pools = fetch("https://yields.llama.fi/pools").get("data", [])
    big = [p for p in pools if (p.get("tvlUsd") or 0) >= 1_000_000
           and p.get("apyBase") is not None and p.get("apyReward") is not None]
    save_json("n03_pools_sample.json", big[:800])

    # reward share = subsidy / total yield
    rshare = []
    for p in big:
        tot = (p["apyBase"] or 0) + (p["apyReward"] or 0)
        if tot > 0:
            rshare.append(p["apyReward"] / tot * 100)
    save_svg("n03_01_reward_share_hist.svg", c.histogram(
        rshare, "收益率中有多少来自代币补贴？", "Share of pool yield coming from token rewards vs organic fees (real)",
        "图 3-1 · 补贴占比分布 · 数据: DefiLlama yields API · 样本 = TVL ≥ 1M USD 且含 base/reward APY 的池子",
        bins=20, xlabel="reward share of total APY (%)"))

    top = sorted(big, key=lambda p: p.get("tvlUsd") or 0, reverse=True)[:120]
    save_svg("n03_02_reward_vs_base.svg", c.scatter_chart(
        [("pool", [p["apyBase"] for p in top], [p["apyReward"] for p in top])],
        "基础收益 vs 代币补贴（按 TVL 前 120 池）",
        "Organic (base) APY vs reward (subsidy) APY for the largest pools (real)",
        "图 3-2 · base APY vs reward APY · 数据: DefiLlama  · 每点 = 一个池子",
        xlabel="base APY (%)", ylabel="reward APY (%)"))

    top_fees = sorted(fees.items(), key=lambda kv: kv[1]["total30d"], reverse=True)[:12]
    save_svg("n03_03_protocol_fees.svg", c.bar_chart(
        [k for k, _ in top_fees], [("30d fees (USD)", [v["total30d"] / 1e6 for _, v in top_fees])],
        "协议真实收入（30 天费用，百万美元）",
        "Real protocol revenue: 30-day fees in USD millions (real)",
        "图 3-3 · 协议 30 天费用 · 数据: DefiLlama fees API",
        ylabel="30d fees (USD m)", show_every=1))

    save_svg("n03_04_tvl_vs_reward.svg", c.scatter_chart(
        [("pool", [p["tvlUsd"] / 1e6 for p in top], [p["apyReward"] for p in top])],
        "补贴强度 vs TVL", "Does a high reward APY attract TVL? (real)",
        "图 3-4 · TVL vs reward APY · 数据: DefiLlama yields · 每点 = 一个池子",
        xlabel="pool TVL (USD m)", ylabel="reward APY (%)"))

    # subsidy "burn ratio": median reward share; and count of pools that are 100% subsidised
    return {
        "protocols": len(fees), "pools_sample": len(big),
        "reward_share_mean_pct": round(sum(rshare) / len(rshare), 1) if rshare else 0,
        "reward_share_median_pct": round(sorted(rshare)[len(rshare) // 2], 1) if rshare else 0,
        "pools_gt_90pct_subsidised": sum(1 for x in rshare if x > 90),
        "top_fees_30d_usd": [[k, round(v["total30d"])] for k, v in top_fees[:6]],
    }


# ============================================================
# NOTE 04 — Funding rate as a market-top signal (Binance Futures)
# ============================================================
def hl_post(payload, timeout=30, tries=3):
    """POST to the Hyperliquid info API (hourly funding + daily candles)."""
    last = None
    for _ in range(tries):
        p = subprocess.run(
            ["curl", "-sS", "--http1.1", "--max-time", str(timeout), "-X", "POST",
             "https://api.hyperliquid.xyz/info",
             "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
            capture_output=True, text=True)
        if p.returncode == 0 and p.stdout.strip():
            try:
                return json.loads(p.stdout)
            except Exception as e:  # noqa: BLE001
                last = e
        else:
            last = p.stderr.strip() or f"curl rc={p.returncode}"
        time.sleep(1.0)
    raise RuntimeError(f"hl_post failed {payload.get('type')} :: {last}")


def note04():
    print("NOTE 04 · Hyperliquid funding & price …")
    now = int(time.time() * 1000)
    days = 365
    start = now - days * 86400000

    # hourly funding, paged in 20-day windows (API caps at 500 points/call)
    fund, t, step = [], start, 20 * 86400000
    while t < now:
        try:
            fund += hl_post({"type": "fundingHistory", "coin": "BTC",
                             "startTime": t, "endTime": min(t + step, now)})
        except Exception as e:  # noqa: BLE001
            print("   funding window fail", t, e)
        t += step
    seen = {}
    for r in fund:
        seen[r["time"]] = r
    fund = [seen[k] for k in sorted(seen)]

    candles = hl_post({"type": "candleSnapshot",
                       "req": {"coin": "BTC", "interval": "1d",
                               "startTime": start, "endTime": now}})
    save_json("n04_funding.json", fund[-2000:])
    save_json("n04_candles.json", candles[-600:])

    # daily total funding rate (%) = sum of hourly rates in the day
    from collections import defaultdict
    day_fund = defaultdict(float)
    for r in fund:
        d = datetime.fromtimestamp(r["time"] / 1000, timezone.utc).strftime("%Y-%m-%d")
        day_fund[d] += float(r["fundingRate"])
    fmean = {d: v * 100 for d, v in day_fund.items()}  # percent per day

    close = {}
    for k in candles:
        d = datetime.fromtimestamp(k["t"] / 1000, timezone.utc).strftime("%Y-%m-%d")
        close[d] = float(k["c"])
    cdays = sorted(close)
    cidx = {d: i for i, d in enumerate(cdays)}

    # align funding -> daily funding with forward returns
    rows = []
    for d in sorted(fmean):
        if d in close:
            idx = cidx[d]
            fwd1 = (close[cdays[idx + 1]] / close[d] - 1) * 100 if idx + 1 < len(cdays) else None
            fwd7 = (close[cdays[idx + 7]] / close[d] - 1) * 100 if idx + 7 < len(cdays) else None
            rows.append({"day": d, "funding": fmean[d], "close": close[d], "fwd1": fwd1, "fwd7": fwd7})
    rows = [r for r in rows if r["fwd7"] is not None]
    save_json("n04_merged.json", rows)

    # dual-axis: price vs 7d-MA funding
    srows = rows[-400:]
    labels = [r["day"][5:] for r in srows]
    price = [r["close"] for r in srows]
    fma = []
    for i in range(len(srows)):
        w = [srows[j]["funding"] for j in range(max(0, i - 6), i + 1)]
        fma.append(sum(w) / len(w))
    save_svg("n04_01_price_vs_funding.svg", c.line_chart(
        labels, [("BTC price", price)], "BTC 价格 vs 资金费率（7 日均值）",
        "BTC mark price versus funding rate; positive = longs pay shorts", 
        "图 4-1 · 价格 vs 资金费率 · 数据: Hyperliquid BTC 永续 · 右轴 = 资金费率 7 日均值 (%)",
        ylabel="BTC price (USDT)", y2=("Funding 7d MA (%)", fma), y2label="funding rate (%)"))

    # histogram of daily funding
    save_svg("n04_02_funding_hist.svg", c.histogram(
        [r["funding"] for r in rows], "日度资金费率分布",
        "Distribution of daily (8h-mean) funding rates (real)",
        "图 4-2 · 资金费率分布 · 数据: Hyperliquid · 正值 = 多头付费给空头",
        bins=22, xlabel="daily funding rate (%)"))

    # decile analysis: funding decile vs mean forward 7d return
    sr = sorted(rows, key=lambda r: r["funding"])
    n = len(sr)
    k = 10
    labels_d, means = [], []
    for i in range(k):
        grp = sr[i * n // k:(i + 1) * n // k]
        labels_d.append(f"D{i+1}")
        means.append(sum(g["fwd7"] for g in grp) / len(grp))
    save_svg("n04_03_decile_forward.svg", c.bar_chart(
        labels_d, [("mean fwd 7d return (%)", means)],
        "按资金费率分位：未来 7 日平均收益",
        "Mean forward 7-day return by funding-rate decile (D10 = most expensive longs)",
        "图 4-3 · 资金费率十分位 vs 未来 7 日收益 · 数据: Hyperliquid",
        ylabel="mean forward 7d return (%)", show_every=1))

    # scatter funding vs fwd7
    save_svg("n04_04_scatter.svg", c.scatter_chart(
        [("day", [r["funding"] for r in rows], [r["fwd7"] for r in rows])],
        "资金费率 vs 未来 7 日收益",
        "Funding rate vs subsequent 7-day return (real); slope of the dashed line = relationship",
        "图 4-4 · funding vs 未来 7 日收益 · 数据: Hyperliquid · 每点 = 一日",
        xlabel="daily funding rate (%)", ylabel="forward 7d return (%)"))

    # stats
    fs = [r["funding"] for r in rows]
    xs = fs
    ys = [r["fwd7"] for r in rows]
    mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
    sy = (sum((y - my) ** 2 for y in ys)) ** 0.5
    corr = cov / (sx * sy) if sx * sy else 0
    top_dec = means[-1]; bot_dec = means[0]
    return {
        "days": len(rows), "funding_mean_pct": round(mx, 4),
        "funding_min_pct": round(min(fs), 4), "funding_max_pct": round(max(fs), 4),
        "negative_funding_days": sum(1 for x in fs if x < 0),
        "corr_funding_fwd7": round(corr, 4),
        "top_decile_fwd7": round(top_dec, 2), "bottom_decile_fwd7": round(bot_dec, 2),
        "span": [rows[0]["day"], rows[-1]["day"]],
    }


def main():
    import sys
    results = {}
    todo = {"01": note01, "02": note02, "03": note03, "04": note04}
    only = sys.argv[1:] or list(todo)
    for key in only:
        if key in todo:
            try:
                results[key] = todo[key]()
                save_json(f"summary_{key}.json", results[key])
                print("DONE", key, json.dumps(results[key], ensure_ascii=False))
            except Exception as e:  # noqa: BLE001
                print("FAIL", key, repr(e))
    print(json.dumps(results, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
