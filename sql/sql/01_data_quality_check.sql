USE BechtelAWP;

SELECT
    IWP_ID,
    discipline,
    status,
    planned_qty,
    actual_qty,
    planned_start,
    planned_finish,
    actual_start,
    actual_finish,
    CASE
        WHEN actual_qty > planned_qty * 1.1
            THEN 'Over-reported quantity'
        WHEN actual_finish < actual_start
            THEN 'Finish before start'
        WHEN status = 'Complete' AND planned_finish > GETDATE()
            THEN 'Marked complete but planned date is future'
        WHEN planned_start IS NULL
            THEN 'Missing planned start date'
        WHEN status IN ('In Progress','Complete') AND actual_start IS NULL
            THEN 'Missing actual start date'
    END AS quality_flag
FROM work_packages
WHERE
    actual_qty > planned_qty * 1.1
    OR actual_finish < actual_start
    OR (status = 'Complete' AND planned_finish > GETDATE())
    OR planned_start IS NULL
    OR (status IN ('In Progress','Complete') AND actual_start IS NULL)
ORDER BY quality_flag;