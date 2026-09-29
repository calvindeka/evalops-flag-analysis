-- LIVE RUN. Q9: Do the flag signals agree? For each pair of (label gap) x (low confidence),
-- how many records? A CTE builds two yes/no columns; the outer query counts each combination.
WITH signals AS (
    SELECT id,
           (n_task_labels = 0 AND n_problem_labels = 0)   AS no_labels_at_all,
           (confidence = 'low')                           AS low_confidence
    FROM records
    WHERE source = 'real_claude'
)
SELECT no_labels_at_all, low_confidence, COUNT(*) AS phrases
FROM signals
GROUP BY no_labels_at_all, low_confidence
ORDER BY no_labels_at_all, low_confidence;
