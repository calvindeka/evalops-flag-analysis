-- LIVE RUN. Q8: How does the model's self-reported confidence relate to being flagged?
-- Note: confidence = 'low' is itself one of the flag reasons, so 100% of low-confidence
-- records are flagged by construction. The interesting rows are medium and high.
SELECT confidence,
       COUNT(*)                                     AS phrases,
       SUM(flagged)                                 AS flagged,
       ROUND(100.0 * SUM(flagged) / COUNT(*), 1)    AS pct_flagged
FROM records
WHERE source = 'real_claude'
GROUP BY confidence
ORDER BY CASE confidence WHEN 'low' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END;
