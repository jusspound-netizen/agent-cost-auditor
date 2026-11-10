#!/usr/bin/env python3
r"""Agent Cost Auditor - find wasted tokens in an AI agent's tool-call log.

Reads a ghost-tracer / ghost-reason SQLite database and prints a
quantified report of the patterns that waste context.

Usage:
    python run.py --db path\to\ghost_tracer.db
    python run.py --db path\to\ghost_tracer.db --json
"""
import argparse
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path


def detect_schema(conn):
    """Return 'tracer' or 'reason' based on which table exists."""
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}
    if "tool_calls" in tables:
        return "tracer"
    if "reasoning" in tables:
        return "reason"
    raise SystemExit(
        "ERROR: no known schema found. Expected table 'tool_calls' "
        "(ghost-tracer) or 'reasoning' (ghost-reason)."
    )


def load_tracer_rows(conn):
    """Yield (timestamp, tool_name, args, result, error) tuples."""
    cur = conn.execute(
        "SELECT timestamp, tool_name, arguments, result, error "
        "FROM tool_calls ORDER BY id ASC"
    )
    for row in cur:
        yield row


def load_reason_rows(conn):
    """Yield reasoning rows as (timestamp, step_type, content, metadata)."""
    cur = conn.execute(
        "SELECT timestamp, step_type, content, metadata "
        "FROM reasoning ORDER BY id ASC"
    )
    for row in cur:
        yield row


def analyze_tracer(rows):
    total = 0
    per_tool = Counter()
    errors_per_tool = Counter()
    retry_loops = 0
    seen_seq = []
    repeated_args = defaultdict(Counter)

    for ts, tool, args, result, error in rows:
        total += 1
        per_tool[tool] += 1
        if error:
            errors_per_tool[tool] += 1
        # crude retry-loop detector: same tool called again immediately
        if seen_seq and seen_seq[-1] == tool and error:
            retry_loops += 1
        seen_seq.append(tool)
        # repeated-arg detector: same tool, same args
        repeated_args[tool][args] += 1

    redundant_calls = sum(
        c - 1 for counter in repeated_args.values() for c in counter.values() if c > 1
    )
    return {
        "total_calls": total,
        "per_tool": dict(per_tool.most_common()),
        "errors_per_tool": dict(errors_per_tool),
        "retry_loops": retry_loops,
        "redundant_calls": redundant_calls,
    }


def analyze_reason(rows):
    steps = list(rows)
    total = len(steps)
    per_type = Counter(r[1] for r in steps)
    # consecutive duplicate thoughts
    dup_thoughts = 0
    last = None
    for _, step_type, content, _ in steps:
        if step_type == "thought" and content == last:
            dup_thoughts += 1
        last = content if step_type == "thought" else None
    return {
        "total_steps": total,
        "per_type": dict(per_type.most_common()),
        "duplicate_thoughts": dup_thoughts,
    }


def estimate_savings(report, kind):
    """Return token savings estimate. Rough: 1 redundant call ~ 300 tokens,
    1 retry loop ~ 800 tokens, 1 duplicate thought ~ 150 tokens."""
    if kind == "tracer":
        tokens = report["redundant_calls"] * 300 + report["retry_loops"] * 800
    else:
        tokens = report["duplicate_thoughts"] * 150
    # $0.000003 per token (typical mid-tier model input price)
    dollars = tokens * 0.000003
    return {"tokens_saved_estimate": tokens, "dollars_saved_estimate": round(dollars, 4)}


def render_text(report, kind, savings):
    lines = []
    lines.append("=" * 60)
    lines.append(f"AGENT COST AUDITOR  ({kind} log)")
    lines.append("=" * 60)
    if kind == "tracer":
        lines.append(f"Total tool calls     : {report['total_calls']}")
        lines.append(f"Redundant calls      : {report['redundant_calls']}")
        lines.append(f"Retry loops detected : {report['retry_loops']}")
        lines.append("")
        lines.append("Calls per tool:")
        for tool, n in report["per_tool"].items():
            errs = report["errors_per_tool"].get(tool, 0)
            lines.append(f"  {tool:<24} {n:>4} calls, {errs:>3} errors")
    else:
        lines.append(f"Total reasoning steps: {report['total_steps']}")
        lines.append(f"Duplicate thoughts   : {report['duplicate_thoughts']}")
        lines.append("")
        lines.append("Steps per type:")
        for step, n in report["per_type"].items():
            lines.append(f"  {step:<12} {n}")
    lines.append("")
    lines.append("-" * 60)
    lines.append(f"Estimated tokens saved : ~{savings['tokens_saved_estimate']:,}")
    lines.append(f"Estimated dollars saved: ~${savings['dollars_saved_estimate']:.4f} per run")
    lines.append("-" * 60)
    lines.append("Recommendation: eliminate redundant calls first - they are the")
    lines.append("largest single source of wasted context in most agent logs.")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="Audit an AI agent's log for wasted tokens.")
    p.add_argument("--db", required=True, help="Path to ghost_tracer.db or ghost_reason.db")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = p.parse_args(argv)

    db = Path(args.db)
    if not db.exists():
        raise SystemExit(f"ERROR: database not found: {db}")

    with sqlite3.connect(db) as conn:
        kind = detect_schema(conn)
        if kind == "tracer":
            report = analyze_tracer(load_tracer_rows(conn))
        else:
            report = analyze_reason(load_reason_rows(conn))

    savings = estimate_savings(report, kind)
    if args.json:
        print(json.dumps({"schema": kind, "report": report, "savings": savings}, indent=2))
    else:
        print(render_text(report, kind, savings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
