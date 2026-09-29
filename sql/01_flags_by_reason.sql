-- LEGACY 9-RECORD LOG ONLY (seeded + mock; see README).
-- Q1: How often does each flag reason fire, and in what share of records?
-- Joins flag_reasons back to records to get the total (9) for the percentage.
SELECT fr.reason,
       COUNT(*)                                                       AS records_with_reason,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM records WHERE source IN ('seeded_fixture', 'dev_mock')), 1)    AS pct_of_records
FROM flag_reasons fr
JOIN records r ON r.id = fr.record_id
WHERE r.source IN ('seeded_fixture', 'dev_mock')
GROUP BY fr.reason
ORDER BY records_with_reason DESC, fr.reason;
