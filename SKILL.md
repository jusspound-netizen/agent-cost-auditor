---
name: agent-cost-auditor
description: Analyze an AI agent's tool-call or reasoning log to find wasted tokens and quantify potential savings. Reads local ghost-tracer / ghost-reason SQLite databases.
external_urls:
  - https://pypi.org/project/ghost-tracer/
  - https://pypi.org/project/ghost-reason/
permissions:
  network: false
  env_vars: false
  filesystem: read
---

# Agent Cost Auditor

## Description

Reads an AI agent's local log (from ghost-tracer or ghost-reason) and produces a
report of the patterns that waste tokens: redundant tool calls, retry loops, and
duplicated reasoning steps. Prints a quantified savings estimate in tokens and dollars.

## When to use this skill

- The user asks "why is my agent so expensive?"
- The user says "my token bill is too high" or "find wasted context"
- The user wants to audit an agent's behavior before optimizing it
- The user has ghost_tracer.db or ghost_reason.db and wants insights

## Prerequisites

- A local SQLite log produced by ghost-tracer or ghost-reason
- Python 3.9+ (no external dependencies)

## Usage

Audit a tracer log (tool calls):

    python scripts/run.py --db path/to/ghost_tracer.db

Audit a reason log (reasoning steps):

    python scripts/run.py --db path/to/ghost_reason.db

Emit JSON:

    python scripts/run.py --db path/to/ghost_tracer.db --json

## Output

- Total calls / steps
- Redundant calls (same tool + same args repeated)
- Retry loops (same tool called again immediately after an error)
- Per-tool breakdown with error counts
- Estimated tokens saved and estimated dollars saved per run

## Notes

- All analysis is local. No data leaves the machine.
- Token savings are an estimate; treat them as a relative ranking.
