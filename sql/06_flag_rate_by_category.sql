-- LIVE RUN (source = 'real_claude'): 71 phrases that returned a result.
-- Q6: What share of each phrase category got flagged for review, and how severe?
-- SUM(flagged) works because flagged is 0/1. CASE WHEN turns severity into countable 0/1 columns.
SELECT category,
       COUNT(*)                                         AS phrases,
       SUM(flagged)                                     AS flagged,
       ROUND(100.0 * SUM(flagged) / COUNT(*), 1)        AS pct_flagged,
       SUM(CASE WHEN severity = 'high'   THEN 1 ELSE 0 END) AS high,
       SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) AS medium,
       SUM(CASE WHEN severity = 'low'    THEN 1 ELSE 0 END) AS low
FROM records
WHERE source = 'real_claude'
GROUP BY category
ORDER BY pct_flagged DESC, category;
