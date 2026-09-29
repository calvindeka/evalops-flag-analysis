import json
import sqlite3

from src.load import flatten, load

REC = {
    "id": "a", "timestamp": "2026-06-30T14:27:36+00:00", "feedback": "f",
    "model_context": None, "stakeholder_context": "Support",
    "classification": {"task_labels": ["x"], "problem_labels": [], "summary": "s"},
    "metric_ids": ["m1", "m2"],
    "flag": {"flagged": True, "reasons": ["no_problem_identified", "tiny_metric_bundle"], "severity": "low"},
}


def test_flatten_counts_labels_and_metrics():
    rec, reasons = flatten(REC, "seeded_fixture")
    assert rec["n_task_labels"] == 1
    assert rec["n_problem_labels"] == 0
    assert rec["n_metrics"] == 2
    assert rec["flagged"] == 1
    assert rec["source"] == "seeded_fixture"
    assert reasons == [("a", "no_problem_identified"), ("a", "tiny_metric_bundle")]


def test_flatten_unflagged_record_has_no_reasons():
    r = {**REC, "flag": {"flagged": False, "reasons": [], "severity": None}}
    rec, reasons = flatten(r, "dev_mock")
    assert rec["flagged"] == 0 and rec["severity"] is None and reasons == []


def test_load_builds_one_record_row_and_one_row_per_reason(tmp_path):
    jsonl = tmp_path / "f.jsonl"
    jsonl.write_text(json.dumps(REC) + "\n")
    prov = tmp_path / "p.csv"
    prov.write_text("id,source,evidence\na,seeded_fixture,test\n")
    db = tmp_path / "t.db"
    load(jsonl, prov, db)
    with sqlite3.connect(db) as c:
        assert c.execute("SELECT COUNT(*) FROM records").fetchone()[0] == 1
        assert c.execute("SELECT COUNT(*) FROM flag_reasons").fetchone()[0] == 2


def test_load_fails_if_a_record_has_no_provenance(tmp_path):
    import pytest
    jsonl = tmp_path / "f.jsonl"
    jsonl.write_text(json.dumps(REC) + "\n")
    prov = tmp_path / "p.csv"
    prov.write_text("id,source,evidence\n")
    with pytest.raises(KeyError):
        load(jsonl, prov, tmp_path / "t.db")


RUN = {
    "phrase_id": "p01", "category": "vague", "feedback": "meh", "run_mode": "real_claude",
    "model": "m", "ran_at": "2026-09-29T21:00:00+00:00",
    "classification": {"task_labels": ["factual_qa", "verification"], "problem_labels": ["low_trust"],
                       "summary": "s", "confidence": "low"},
    "metric_ids": ["a"], "flag": {"flagged": False, "reasons": [], "severity": None},
}


def test_flatten_run_maps_fields_and_labels():
    from src.load import flatten_run
    rec, reasons, labels = flatten_run(RUN)
    assert rec["id"] == "p01" and rec["source"] == "real_claude"
    assert rec["category"] == "vague" and rec["confidence"] == "low" and rec["model"] == "m"
    assert rec["flagged"] == 0 and reasons == []
    assert ("p01", "task", "verification") in labels and ("p01", "problem", "low_trust") in labels
    assert len(labels) == 3


def test_load_run_stores_errors_separately(tmp_path):
    from src.load import load_run
    run = tmp_path / "r.jsonl"
    err = {"phrase_id": "p02", "category": "vague", "feedback": "x", "run_mode": "real_claude",
           "model": "m", "ran_at": "t", "error": "AttributeError: boom"}
    run.write_text(json.dumps(RUN) + "\n" + json.dumps(err) + "\n")
    jsonl = tmp_path / "f.jsonl"; jsonl.write_text("")
    prov = tmp_path / "p.csv"; prov.write_text("id,source,evidence\n")
    db = tmp_path / "t.db"
    load(jsonl, prov, db)
    load_run(run, db)
    with sqlite3.connect(db) as c:
        assert c.execute("SELECT COUNT(*) FROM records WHERE source='real_claude'").fetchone()[0] == 1
        assert c.execute("SELECT COUNT(*) FROM run_errors").fetchone()[0] == 1
