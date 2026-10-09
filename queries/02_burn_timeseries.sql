-- ============================================================
-- Query 02 · Cumulative ETH burn since EIP-1559
-- 目的：计算自 EIP-1559（2021-08-05，block 12,965,000）以来的
--       累计销毁量，作为"通缩型财政政策"的规模度量。
-- 平台：Dune Analytics (DuneSQL)
-- ============================================================
WITH daily AS (
    SELECT
        DATE_TRUNC('day', time)                     AS day,
        SUM(CAST(base_fee_per_gas AS DOUBLE) * CAST(gas_used AS DOUBLE)) / 1e18
                                                    AS eth_burned
    FROM ethereum.blocks
    WHERE time >= TIMESTAMP '2021-08-05'
    GROUP BY 1
)
SELECT
    day,
    eth_burned,
    SUM(eth_burned)   OVER (ORDER BY day)           AS cum_eth_burned,
    AVG(eth_burned)   OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
                                                    AS eth_burned_7d_ma
FROM daily
ORDER BY day;
-- 交叉校验：可将本结果与 ultrasound.money / Etherscan 的 "ETH Burned" 指标对齐。
