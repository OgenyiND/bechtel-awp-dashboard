USE BechtelAWP;

SELECT
    discipline,
    COUNT(*)                                        AS total_packages,
    SUM(planned_qty)                                AS total_planned_qty,
    SUM(actual_qty)                                 AS total_actual_qty,
    ROUND(SUM(actual_qty) / SUM(planned_qty) * 100, 1) AS pct_complete,
    SUM(CASE WHEN status = 'Complete'    THEN 1 ELSE 0 END) AS complete,
    SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) AS in_progress,
    SUM(CASE WHEN status = 'Not Started' THEN 1 ELSE 0 END) AS not_started,
    CASE
        WHEN SUM(actual_qty) / SUM(planned_qty) >= 0.8 THEN 'Green'
        WHEN SUM(actual_qty) / SUM(planned_qty) >= 0.5 THEN 'Amber'
        ELSE 'Red'
    END AS rag_status
FROM work_packages
GROUP BY discipline
ORDER BY pct_complete DESC;