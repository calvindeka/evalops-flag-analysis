"""Load the flagged-feedback JSONL log into SQLite (records + flag_reasons)."""
import csv
import json
import sqlite3
import sys
from pathlib import Path

SCHEMA = Path(__file__).resolve().parent.parent / "sql" / "00_schema.sql"


def flatten(raw: dict, source: str):
    """One JSONL record -> (row for `records`, list of (record_id, reason))."""
    flag, cls = raw["flag"], raw["classification"]
    rec = {
        "id": raw["id"], "logged_at": raw["timestamp"], "feedback": raw["feedback"],
        "model_context": raw.get("model_context"), "stakeholder_ctx": raw.get("stakeholder_context"),
        "n_task_labels": len(cls["task_labels"]), "n_problem_labels": len(cls["problem_labels"]),
        "n_metrics": len(raw["metric_ids"]), "flagged": int(flag["flagged"]),
        "severity": flag["severity"], "source": source,
        "category": None, "confidence": cls.get("confidence"), "model": None,
    }
    return rec, [(raw["id"], r) for r in flag["reasons"]]


def flatten_run(raw: dict):
    """One line of run_real_claude.jsonl -> (records row, reasons, labels)."""
    cls = raw["classification"]
    rec, reasons = flatten({**raw, "id": raw["phrase_id"], "timestamp": raw["ran_at"]}, raw["run_mode"])
    rec["category"], rec["model"] = raw["category"], raw["model"]
    labels = [(raw["phrase_id"], "task", t) for t in cls["task_labels"]] + \
             [(raw["phrase_id"], "problem", p) for p in cls["problem_labels"]]
    return rec, reasons, labels


def load_run(run_path, db_path) -> int:
    """Add the live-API run to an existing database. Returns rows loaded (errors excluded)."""
    conn = sqlite3.connect(db_path)
    try:
        n = 0
        for line in open(run_path):
            raw = json.loads(line)
            if "error" in raw:
                conn.execute("INSERT INTO run_errors VALUES (?, ?, ?, ?)",
                             (raw["phrase_id"], raw["category"], raw["feedback"], raw["error"]))
                continue
            rec, reasons, labels = flatten_run(raw)
            conn.execute(f"INSERT INTO records ({', '.join(rec)}) VALUES ({', '.join('?' for _ in rec)})",
                         list(rec.values()))
            conn.executemany("INSERT INTO flag_reasons VALUES (?, ?)", reasons)
            conn.executemany("INSERT INTO record_labels VALUES (?, ?, ?)", labels)
            n += 1
        conn.commit()
        return n
    finally:
        conn.close()


def load(jsonl_path, provenance_path, db_path) -> int:
    with open(provenance_path, newline="") as f:
        source_of = {r["id"]: r["source"] for r in csv.DictReader(f)}
    Path(db_path).unlink(missing_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA.read_text())
        n = 0
        for line in open(jsonl_path):
            raw = json.loads(line)
            rec, reasons = flatten(raw, source_of[raw["id"]])  # KeyError = record without provenance
            cols = ", ".join(rec)
            conn.execute(f"INSERT INTO records ({cols}) VALUES ({', '.join('?' for _ in rec)})", list(rec.values()))
            conn.executemany("INSERT INTO flag_reasons VALUES (?, ?)", reasons)
            n += 1
        conn.commit()
        return n
    finally:
        conn.close()


if __name__ == "__main__":
    print("legacy log:", load("data/flagged_feedback.jsonl", "data/provenance.csv", "data/flags.db"), "records")
    print("live run:  ", load_run("data/run_real_claude.jsonl", "data/flags.db"), "records")
