-- ============================================================
-- Query 03 · Post-Merge validator revenue structure
-- 目的：拆解 The Merge（2022-09-15）之后验证者的日收入结构：
--       ① 共识层发行奖励（issuance）
--       ② 执行层优先费（priority fee / tip）
--       ③ MEV-boost 区块的额外执行层收入（近似）
-- 平台：Dune Analytics (DuneSQL)
-- ============================================================
WITH exec AS (
    -- 执行层：付给验证者（fee recipient）的 priority fee
    SELECT
        DATE_TRUNC('day', block_time) AS day,
        SUM(gas_used * COALESCE(priority_fee_per_gas, gas_price - base_fee_per_gas)) / 1e18
                                      AS exec_tip_eth
    FROM ethereum.transactions
    WHERE block_time >= TIMESTAMP '2022-09-15'
      AND success = true
    GROUP BY 1
),
consensus AS (
    -- 共识层：验证者发行奖励（attestation + proposal），Dune 已聚合到 validator 级
    SELECT
        block_date                    AS day,
        SUM(CAST(income AS DOUBLE)) / 1e9 AS consensus_reward_eth   -- income 单位 Gwei
    FROM beacon.validator_income
    WHERE block_date >= DATE '2022-09-15'
      AND income > 0
    GROUP BY 1
)
SELECT
    COALESCE(e.day, c.day)                     AS day,
    COALESCE(c.consensus_reward_eth, 0)        AS consensus_reward_eth,
    COALESCE(e.exec_tip_eth, 0)                AS exec_tip_eth,
    COALESCE(c.consensus_reward_eth, 0)
      + COALESCE(e.exec_tip_eth, 0)            AS total_validator_revenue_eth,
    COALESCE(e.exec_tip_eth, 0)
      / NULLIF(COALESCE(c.consensus_reward_eth, 0) + COALESCE(e.exec_tip_eth, 0), 0)
                                               AS exec_share
FROM consensus c
FULL OUTER JOIN exec e ON c.day = e.day
ORDER BY day;
-- 备注：beacon.validator_income 的单位为 Gwei；若表名/单位随 spellbook 变化，
--       请以 dune.beacon 数据集文档为准，并把 MEV 收入单独用 mev 相关表补充。
