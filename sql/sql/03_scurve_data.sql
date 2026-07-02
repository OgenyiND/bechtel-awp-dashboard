USE BechtelAWP;

-- Weekly cumulative planned vs actual for the S-curve chart in Power BI
WITH weeks AS (
    SELECT DISTINCT
        DATEADD(DAY, 1 - DATEPART(WEEKDAY, planned_start), planned_start) AS week_start
    FROM work_packages
    WHERE planned_start IS NOT NULL
),
planned_cumulative AS (
    SELECT
        w.week_start,
        SUM(wp.planned_qty) OVER (ORDER BY w.week_start) AS cumulative_planned
    FROM weeks w
    JOIN work_packages wp
        ON DATEADD(DAY, 1 - DATEPART(WEEKDAY, wp.planned_start), wp.planned_start) <= w.week_start
    WHERE wp.planned_start IS NOT NULL
),
actual_cumulative AS (
    SELECT
        DATEADD(DAY, 1 - DATEPART(WEEKDAY, dp.progress_date), dp.progress_date) AS week_start,
        SUM(dp.qty_installed) AS weekly_actual
    FROM daily_progress dp
    WHERE dp.qty_installed IS NOT NULL AND dp.qty_installed > 0
    GROUP BY DATEADD(DAY, 1 - DATEPART(WEEKDAY, dp.progress_date), dp.progress_date)
)
SELECT
    p.week_start,
    MAX(p.cumulative_planned)                               AS cumulative_planned,
    SUM(a.weekly_actual) OVER (ORDER BY p.week_start)      AS cumulative_actual
FROM planned_cumulative p
LEFT JOIN actual_cumulative a ON a.week_start = p.week_start
GROUP BY p.week_start, a.weekly_actual
ORDER BY p.week_start;