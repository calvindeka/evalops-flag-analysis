-- LEGACY 9-RECORD LOG ONLY.
-- Q4: Was the same feedback text logged more than once?
-- HAVING filters groups (WHERE can't, because COUNT(*) only exists after grouping).
SELECT feedback,
       COUNT(*)              AS times_logged,
       MIN(logged_at)        AS first_logged,
       MAX(logged_at)        AS last_logged
FROM records
WHERE source IN ('seeded_fixture', 'dev_mock')
GROUP BY feedback
HAVING COUNT(*) > 1
ORDER BY times_logged DESC;
