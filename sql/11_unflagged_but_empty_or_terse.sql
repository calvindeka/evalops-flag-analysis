-- LIVE RUN. Q11: Vague / non-actionable / terse phrases that were NOT flagged.
-- These are the flag rules' possible blind spots: the pipeline was satisfied by an output
-- that arguably should not be trusted.
SELECT r.id, r.category, r.feedback, r.confidence, r.n_task_labels, r.n_problem_labels, r.n_metrics
FROM records r
WHERE r.source = 'real_claude'
  AND r.flagged = 0
  AND r.category IN ('vague', 'non_actionable', 'terse')
ORDER BY r.category, r.id;
