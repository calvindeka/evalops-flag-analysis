-- LEGACY 9-RECORD LOG ONLY.
-- Q3: How many reasons does each record carry, and which ones?
-- LEFT JOIN keeps records with zero reasons (none here, but the query would show them).
-- group_concat glues the reasons into one text cell per record.
SELECT substr(r.id, 1, 8)                       AS id,
       r.source,
       r.severity,
       COUNT(fr.reason)                         AS n_reasons,
       group_concat(fr.reason, ', ')            AS reasons
FROM records r
LEFT JOIN flag_reasons fr ON fr.record_id = r.id
WHERE r.source IN ('seeded_fixture', 'dev_mock')
GROUP BY r.id
ORDER BY n_reasons DESC, r.logged_at;
