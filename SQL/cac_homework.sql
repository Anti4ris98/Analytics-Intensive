-- ============================================================
--  SQL Homework — CAC по каналах
--  Движок: BigQuery | Таблица: marketing_ads_raw
-- ============================================================


-- ============================================================
--  ОСНОВНОЙ ЗАПРОС: CAC и воронка по каналам за весь период
-- ============================================================

WITH

-- ШАГ 1: Дедупликация
-- Данные кумулятивные: за один день по одному ad_id бывает 3-6 снапшотов.
-- Оставляем только последний снапшот за каждый (ad_id, date).
deduped AS (
    SELECT
        source,
        campaign_id,
        adset_id,
        ad_id,
        date,
        spend,
        impressions,
        clicks,
        installs,
        registrations,
        timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY ad_id, date
            ORDER BY timestamp DESC
        ) AS rn
    FROM `marketing_ads_raw`
),

latest_snapshots AS (
    SELECT * EXCEPT (rn)
    FROM deduped
    WHERE rn = 1
),

-- ШАГ 2: Дневные метрики по (source, date)
-- Суммируем по каналу и дню — теперь каждая строка = реальные дневные показатели.
daily_metrics AS (
    SELECT
        source,
        date,
        SUM(spend)         AS daily_spend,
        SUM(impressions)   AS daily_impressions,
        SUM(clicks)        AS daily_clicks,
        SUM(installs)      AS daily_installs,
        SUM(registrations) AS daily_registrations
    FROM latest_snapshots
    GROUP BY source, date
),

-- ШАГ 3: Агрегация по каналу за весь период
channel_totals AS (
    SELECT
        source,
        SUM(daily_spend)         AS total_spend,
        SUM(daily_impressions)   AS total_impressions,
        SUM(daily_clicks)        AS total_clicks,
        SUM(daily_installs)      AS total_installs,
        SUM(daily_registrations) AS total_registrations
    FROM daily_metrics
    GROUP BY source
)

-- ШАГ 3 (финал): Считаем все метрики + CAC + LTV/CAC (бонус)
SELECT
    source,

    -- Затраты
    ROUND(total_spend, 2)                                                          AS total_spend,

    -- CPM: стоимость 1000 показов
    ROUND(SAFE_DIVIDE(total_spend, total_impressions) * 1000, 2)                  AS cpm,

    -- CTR: % кликов от показов
    ROUND(SAFE_DIVIDE(total_clicks, total_impressions) * 100, 2)                  AS ctr_pct,

    -- CR Click → Install: % установок от кликов
    ROUND(SAFE_DIVIDE(total_installs, total_clicks) * 100, 2)                     AS cr_click_install_pct,

    -- CR Install → Reg: % регистраций от установок
    ROUND(SAFE_DIVIDE(total_registrations, total_installs) * 100, 2)              AS cr_install_reg_pct,

    -- CAC: сколько стоит 1 зарегистрированный пользователь
    ROUND(SAFE_DIVIDE(total_spend, total_registrations), 2)                       AS cac,

    -- БОНУС: LTV из прошлого воркшопа (захардкожены по условию)
    CASE source
        WHEN 'tiktok' THEN 8.50
        WHEN 'meta'   THEN 6.20
        WHEN 'google' THEN 12.40
    END                                                                            AS ltv,

    -- БОНУС: LTV / CAC — насколько канал прибыльный
    ROUND(
        SAFE_DIVIDE(
            CASE source
                WHEN 'tiktok' THEN 8.50
                WHEN 'meta'   THEN 6.20
                WHEN 'google' THEN 12.40
            END,
            SAFE_DIVIDE(total_spend, total_registrations)
        ),
        2
    )                                                                              AS ltv_cac_ratio

FROM channel_totals
ORDER BY cac ASC;   -- от самого дешёвого привлечения к самому дорогому


-- ============================================================
--  БОНУС: CAC по месяцам — динамика эффективности каналов
-- ============================================================

WITH

deduped AS (
    SELECT
        source,
        ad_id,
        date,
        spend,
        registrations,
        timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY ad_id, date
            ORDER BY timestamp DESC
        ) AS rn
    FROM `marketing_ads_raw`
),

latest_snapshots AS (
    SELECT * EXCEPT (rn)
    FROM deduped
    WHERE rn = 1
),

monthly_metrics AS (
    SELECT
        source,
        DATE_TRUNC(date, MONTH)    AS month,
        SUM(spend)                 AS monthly_spend,
        SUM(registrations)         AS monthly_registrations
    FROM latest_snapshots
    GROUP BY source, DATE_TRUNC(date, MONTH)
)

SELECT
    source,
    month,
    ROUND(monthly_spend, 2)                                        AS monthly_spend,
    monthly_registrations,
    ROUND(SAFE_DIVIDE(monthly_spend, monthly_registrations), 2)    AS cac
FROM monthly_metrics
ORDER BY month ASC, source ASC;


-- ============================================================
--  ПРОВЕРОЧНЫЙ ЗАПРОС: убеждаемся что дедупликация прошла корректно
--  После неё на каждый (ad_id, date) должна быть ровно 1 строка.
-- ============================================================

WITH deduped AS (
    SELECT
        ad_id,
        date,
        ROW_NUMBER() OVER (
            PARTITION BY ad_id, date
            ORDER BY timestamp DESC
        ) AS rn
    FROM `marketing_ads_raw`
)
SELECT
    MAX(rn) AS max_rows_per_ad_date  -- должно быть 1
FROM deduped
WHERE rn = 1
;
-- Альтернативная проверка: найти дубли (если запрос вернёт строки — дедупликация не сработала)
-- SELECT ad_id, date, COUNT(*) AS cnt
-- FROM latest_snapshots
-- GROUP BY ad_id, date
-- HAVING cnt > 1;
