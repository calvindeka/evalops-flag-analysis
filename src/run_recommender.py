"""Run every phrase in data/phrases.csv through the EvalOps recommender's real pipeline.

Uses the recommender's own functions (classify_feedback -> get_recommendations ->
apply_sanity_rules -> flagging.evaluate) with DEV=false, so each phrase makes ONE live
Claude API call. Results (flagged or not) go to data/run_real_claude.jsonl.
This script does not write to the recommender's own flag log.

Usage (needs the recommender's Python environment and its ANTHROPIC_API_KEY):
    EVALOPS_DIR=~/EvalOps/evalops-metric-assistant \
      $EVALOPS_DIR/.venv/bin/python src/run_recommender.py [--limit N]
"""
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

EVALOPS_DIR = Path(os.environ.get("EVALOPS_DIR", "~/EvalOps/evalops-metric-assistant")).expanduser()
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "run_real_claude.jsonl"

os.environ["DEV"] = "false"          # force the real API path (dotenv does not override this)
sys.path.insert(0, str(EVALOPS_DIR))
os.chdir(EVALOPS_DIR)

import flagging                       # noqa: E402
import llm_utils                      # noqa: E402
from prompts import apply_sanity_rules, get_recommendations, load_json  # noqa: E402

assert not llm_utils.DEV_MODE, "refusing to run: DEV mode is on, that would be mock output"
HARDCODED_MODEL = re.search(r'model="([^"]+)"', (EVALOPS_DIR / "llm_utils.py").read_text()).group(1)

# The recommender hardcodes a model that Anthropic has since retired (404). Swap in a current
# model at call time WITHOUT editing the recommender's source; the model actually used is
# recorded on every result row.
MODEL = os.environ.get("MODEL_OVERRIDE", "claude-sonnet-5-5")
_orig_create = llm_utils.client.messages.create


def _create_with_model(*args, **kwargs):
    kwargs["model"] = MODEL
    return _orig_create(*args, **kwargs)


llm_utils.client.messages.create = _create_with_model

tasks, problems = load_json("tasks.json"), load_json("problems.json")
metrics, mappings = load_json("metrics.json"), load_json("mappings.json")


def run_one(feedback: str) -> dict:
    cls = llm_utils.classify_feedback(feedback, tasks, problems)
    rec = get_recommendations(cls.get("task_labels", []), cls.get("problem_labels", []), metrics, mappings)
    rec = apply_sanity_rules(cls.get("task_labels", []), cls.get("problem_labels", []), rec, metrics)
    metric_ids = [m["id"] for m in rec]
    decision = flagging.evaluate(feedback, cls, metric_ids, claude_confidence=cls.get("confidence"))
    return {"classification": cls, "metric_ids": metric_ids, "flag": decision.to_dict()}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    done = set()
    if OUT.exists():
        done = {json.loads(l)["phrase_id"] for l in OUT.read_text().splitlines() if l}
    with open(ROOT / "data" / "phrases.csv", newline="") as f:
        phrases = [r for r in csv.DictReader(f) if r["phrase_id"] not in done]
    if limit:
        phrases = phrases[:limit]
    with OUT.open("a") as out:
        for p in phrases:
            rec = {"phrase_id": p["phrase_id"], "category": p["category"], "feedback": p["feedback"],
                   "run_mode": "real_claude", "model": MODEL, "recommender_hardcoded_model": HARDCODED_MODEL,
                   "ran_at": datetime.now(timezone.utc).isoformat()}
            try:
                rec.update(run_one(p["feedback"]))
            except Exception as e:  # keep failures visible instead of dropping the phrase
                rec["error"] = f"{type(e).__name__}: {e}"
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(p["phrase_id"], "error" if "error" in rec else rec["flag"]["severity"], flush=True)
            time.sleep(0.5)


if __name__ == "__main__":
    main()
