"""Run sql/0N_*.sql against data/flags.db, save CSVs, and draw one chart."""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DB, OUT = "data/flags.db", Path("outputs")


def main():
    OUT.mkdir(exist_ok=True)
    with sqlite3.connect(DB) as conn:
        for f in sorted(Path("sql").glob("[0-9][0-9]_*.sql")):
            if f.name.startswith("00"):
                continue  # schema, not a query
            pd.read_sql_query(f.read_text(), conn).to_csv(OUT / f"{f.stem}.csv", index=False)
        d = pd.read_sql_query(
            "SELECT fr.reason, r.source, COUNT(*) n FROM flag_reasons fr "
            "JOIN records r ON r.id = fr.record_id GROUP BY fr.reason, r.source", conn)
    live = pd.read_sql_query(
        "SELECT category, 100.0 * SUM(flagged) / COUNT(*) AS pct_flagged FROM records "
        "WHERE source = 'real_claude' GROUP BY category ORDER BY pct_flagged", sqlite3.connect(DB))
    ax = live.plot.barh(x="category", y="pct_flagged", legend=False, figsize=(8, 4))
    ax.set(title="Live Claude run: % of phrases flagged, by phrase category (n = 71)",
           xlabel="% flagged for review", ylabel="", xlim=(0, 100))
    plt.tight_layout(); plt.savefig(OUT / "live_flag_rate_by_category.png", dpi=130); plt.close()

    p = d.pivot(index="reason", columns="source", values="n").fillna(0)
    p = p.loc[p.sum(axis=1).sort_values().index]
    ax = p.plot.barh(stacked=True, figsize=(9, 4))
    ax.set(title="Legacy 9-record log: flag reasons by source (seeded / mock, not real Claude)",
           xlabel="Records", ylabel="")
    plt.tight_layout(); plt.savefig(OUT / "legacy_reasons_by_source.png", dpi=130); plt.close()
    print("wrote outputs/")


if __name__ == "__main__":
    main()
