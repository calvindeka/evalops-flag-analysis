-- records: one row per logged feedback item. flag_reasons: one row per (record, reason),
-- because a record can carry several reasons (a "one-to-many" relationship).
CREATE TABLE records (
    id                TEXT PRIMARY KEY,
    logged_at         TEXT NOT NULL,
    feedback          TEXT NOT NULL,
    model_context     TEXT,
    stakeholder_ctx   TEXT,
    n_task_labels     INTEGER NOT NULL,
    n_problem_labels  INTEGER NOT NULL,
    n_metrics         INTEGER NOT NULL,
    flagged           INTEGER NOT NULL CHECK (flagged IN (0, 1)),
    severity          TEXT CHECK (severity IN ('high', 'medium', 'low')),
    category          TEXT,      -- author-assigned phrase category (real_claude rows only)
    confidence        TEXT,      -- model's self-reported confidence (real_claude rows only)
    model             TEXT,
    source            TEXT NOT NULL CHECK (source IN ('seeded_fixture', 'dev_mock', 'real_claude'))
);
CREATE TABLE flag_reasons (
    record_id TEXT NOT NULL REFERENCES records (id),
    reason    TEXT NOT NULL,
    PRIMARY KEY (record_id, reason)
);

-- Labels the classifier chose, one row per (record, kind, label); kind is 'task' or 'problem'.
CREATE TABLE record_labels (
    record_id TEXT NOT NULL REFERENCES records (id),
    kind      TEXT NOT NULL CHECK (kind IN ('task', 'problem')),
    label     TEXT NOT NULL,
    PRIMARY KEY (record_id, kind, label)
);

-- Phrases where the pipeline crashed instead of returning a result.
CREATE TABLE run_errors (
    phrase_id TEXT PRIMARY KEY,
    category  TEXT,
    feedback  TEXT NOT NULL,
    error     TEXT NOT NULL
);
