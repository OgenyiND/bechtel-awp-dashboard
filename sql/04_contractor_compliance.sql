USE BechtelAWP;

SELECT
    c.contractor_id,
    c.name                                          AS contractor_name,
    c.discipline,
    c.compliance_status,
    COUNT(wp.IWP_ID)                                AS total_packages,
    SUM(CASE WHEN wp.status = 'Complete' THEN 1 ELSE 0 END)     AS completed,
    SUM(CASE WHEN wp.status = 'In Progress' THEN 1 ELSE 0 END)  AS in_progress,
    ROUND(
        100.0 * SUM(CASE WHEN wp.status = 'Complete' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(wp.IWP_ID), 0), 1
    )                                               AS completion_rate_pct,
    COUNT(dp.record_id)                             AS total_progress_reports,
    SUM(CASE WHEN dp.data_quality_flag IS NOT NULL THEN 1 ELSE 0 END) AS flagged_reports,
    ROUND(
        100.0 * SUM(CASE WHEN dp.data_quality_flag IS NULL THEN 1 ELSE 0 END)
        / NULLIF(COUNT(dp.record_id), 0), 1
    )                                               AS data_quality_rate_pct
FROM contractors c
LEFT JOIN work_packages wp ON wp.contractor_id = c.contractor_id
LEFT JOIN daily_progress dp ON dp.IWP_ID = wp.IWP_ID
GROUP BY c.contractor_id, c.name, c.discipline, c.compliance_status
ORDER BY completion_rate_pct DESC;