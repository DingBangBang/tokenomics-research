-- ============================================================
-- Query 01 · Ethereum daily gas usage & fee decomposition
-- 目的：得到每日 gas 用量、总费用、被销毁的 base fee 与付给验证者
--       的 priority fee（tip）的时间序列，用于 EIP-1559 前后对比。
-- 平台：Dune Analytics (DuneSQL / Trino)
-- 口径：仅统计成功交易 (success = true)；剔除失败交易可避免高估 tip。
-- ============================================================
SELECT
    DATE_TRUNC('day', block_time)                                   AS day,
    COUNT(*)                                                        AS tx_count,
    SUM(gas_used)                                                   AS gas_used,
    -- 用户实际支付的执行层总费用（ETH）
    SUM(gas_used * effective_gas_price) / 1e18                      AS total_fee_eth,
    -- 被销毁的 base fee（EIP-1559 之后才有，之前为 0）
    SUM(gas_used * base_fee_per_gas) / 1e18                         AS base_fee_burned_eth,
    -- 付给验证者的优先费（tip）
    SUM(gas_used * COALESCE(priority_fee_per_gas, gas_price - base_fee_per_gas)) / 1e18
                                                                    AS priority_fee_eth,
    AVG(base_fee_per_gas)  / 1e9                                    AS avg_base_fee_gwei,
    AVG(priority_fee_per_gas) / 1e9                                 AS avg_priority_fee_gwei
FROM ethereum.transactions
WHERE block_time >= TIMESTAMP '2020-01-01'
  AND success = true
GROUP BY 1
ORDER BY 1;
-- 备注：ethereum.transactions 中包含 base_fee_per_gas / priority_fee_per_gas /
--       effective_gas_price 字段；若字段名随 spellbook 版本变化，请以
--       ethereum.blocks 的 base_fee_per_gas 为准做交叉校验。
