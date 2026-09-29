-- LIVE RUN. Q7: Which flag reasons fire in which phrase category?
-- INNER JOIN drops unflagged records (they have no reasons), which is what we want here.
SELECT r.category,
       fr.reason,
       COUNT(*) AS n
FROM flag_reasons fr
JOIN records r ON r.id = fr.record_id
WHERE r.source = 'real_claude'
GROUP BY r.category, fr.reason
ORDER BY r.category, n DESC, fr.reason;
