-- ============================================================
-- Query 05 · Real staking yield: issuance vs burn (net supply change)
-- 目的：把"验证者名义收益"折算为"实际收益率"——即扣除净发行
--       （发行 - 销毁）稀释后的持币购买力变化。
-- 平台：Dune Analytics (DuneSQL)
-- ============================================================
WITH consensus AS (
    -- 共识层发行总量（ETH/日）
    SELECT
        block_date                       AS day,
        SUM(CAST(income AS DOUBLE)) / 1e9 AS issuance_eth
    FROM beacon.validator_income
    WHERE block_date >= DATE '2022-09-15'
    GROUP BY 1
),
burn AS (
    SELECT
        DATE_TRUNC('day', time)          AS day,
        SUM(CAST(base_fee_per_gas AS DOUBLE) * CAST(gas_used AS DOUBLE)) / 1e18
                                         AS burned_eth
    FROM ethereum.blocks
    WHERE time >= TIMESTAMP '2022-09-15'
    GROUP BY 1
)
SELECT
    c.day,
    c.issuance_eth,
    COALESCE(b.burned_eth, 0)                         AS burned_eth,
    c.issuance_eth - COALESCE(b.burned_eth, 0)        AS net_issuance_eth,
    -- 以流通量近似（示例用固定 120,000,000 ETH 作分母，可替换为真实 supply 表）
    (c.issuance_eth - COALESCE(b.burned_eth, 0)) / 120e6 * 365
                                                      AS annualized_net_supply_growth
FROM consensus c
LEFT JOIN burn b ON c.day = b.day
ORDER BY c.day;
-- 解读：net_issuance_eth < 0 的天数占比，即"EIP-1559 + PoS 使 ETH 通缩"的时点占比；
--       验证者的"实际收益率" = 名义质押收益率 + 净发行（稀释/反稀释）效应。
