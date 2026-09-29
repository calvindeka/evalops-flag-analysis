-- LEGACY 9-RECORD LOG ONLY.
-- Q2: Severity distribution, split by where the record came from.
-- Provenance matters: seeded fixtures and DEV-mock output are NOT real model behavior.
SELECT source, severity, COUNT(*) AS records
FROM records
WHERE source IN ('seeded_fixture', 'dev_mock')
GROUP BY source, severity
ORDER BY source, CASE severity WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END;
