-- LEGACY 9-RECORD LOG ONLY.
-- Q5: Of the flagged records, how many had NO task label, NO problem label, or NO metrics?
-- CTE computes per-record booleans; the outer query totals them by source.
WITH gaps AS (
    SELECT source,
           (n_task_labels = 0)    AS no_task,
           (n_problem_labels = 0) AS no_problem,
           (n_metrics <= 1)       AS small_bundle
    FROM records
    WHERE flagged = 1 AND source IN ('seeded_fixture', 'dev_mock')
)
SELECT source,
       COUNT(*)           AS flagged_records,
       SUM(no_task)       AS no_task_label,
       SUM(no_problem)    AS no_problem_label,
       SUM(small_bundle)  AS one_or_zero_metrics
FROM gaps
GROUP BY source;
