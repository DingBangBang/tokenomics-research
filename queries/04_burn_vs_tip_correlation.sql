-- ============================================================
-- Query 04 · Does a higher burn squeeze validator tips?
-- 目的：检验核心假设——销毁量（拥堵/需求）上升时，验证者的
--       tip 收入是被"挤压"还是同步上升。
-- 方法：把日序列按销毁量分位数分桶，比较各桶的日 tip 收入与
--       单位 gas 的 tip（tip per gas），并给出相关系数。
-- 平台：Dune Analytics (DuneSQL)
-- ============================================================
WITH daily AS (
    SELECT
        DATE_TRUNC('day', block_time)                                            AS day,
        SUM(gas_used * base_fee_per_gas) / 1e18                                  AS burn_eth,
        SUM(gas_used * COALESCE(priority_fee_per_gas, gas_price - base_fee_per_gas)) / 1e18
                                                                                 AS tip_eth,
        SUM(gas_used)                                                            AS gas_used
    FROM ethereum.transactions
    WHERE block_time >= TIMESTAMP '2021-08-05'
      AND success = true
    GROUP BY 1
),
bucketed AS (
    SELECT
        day, burn_eth, tip_eth, gas_used,
        tip_eth / NULLIF(gas_used, 0)                       AS tip_per_gas_eth,
        NTILE(10) OVER (ORDER BY burn_eth)                  AS burn_decile
    FROM daily
)
SELECT
    burn_decile,
    COUNT(*)                                   AS days,
    AVG(burn_eth)                              AS avg_burn_eth,
    AVG(tip_eth)                               AS avg_tip_eth,
    AVG(tip_per_gas_eth)                       AS avg_tip_per_gas_eth,
    CORR(burn_eth, tip_eth)      OVER ()       AS corr_burn_tip,
    CORR(burn_eth, tip_per_gas_eth) OVER ()    AS corr_burn_tip_per_gas
FROM bucketed
GROUP BY burn_decile
ORDER BY burn_decile;
-- 解读：若 corr_burn_tip > 0 且各 decile 的 avg_tip_eth 随 burn 上升而上升，
--       则"销毁挤压 tip"的假说在时序上不成立——二者由同一需求因子驱动。
