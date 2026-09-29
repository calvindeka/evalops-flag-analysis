-- LIVE RUN. Q10: Which taxonomy labels does Claude pick most, and how often are those
-- records flagged? Window function ranks labels within task / problem.
WITH label_counts AS (
    SELECT rl.kind, rl.label, COUNT(*) AS n, SUM(r.flagged) AS flagged
    FROM record_labels rl
    JOIN records r ON r.id = rl.record_id
    WHERE r.source = 'real_claude'
    GROUP BY rl.kind, rl.label
)
SELECT kind, label, n, flagged,
       RANK() OVER (PARTITION BY kind ORDER BY n DESC) AS rank_in_kind
FROM label_counts
ORDER BY kind, rank_in_kind, label;
