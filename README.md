# Agent Cost Auditor

A SKILL.md package for AI agents that audits an agent's tool-call or reasoning
log for wasted tokens and prints a quantified savings estimate.

## What it does

Reads a local SQLite log from `ghost-tracer` or `ghost-reason` and reports:
- Redundant tool calls (same tool + same args repeated)
- Retry loops (same tool called again immediately after an error)
- Duplicate reasoning steps

Prints an estimated token and dollar savings per run.

## Install

This is an Agensi skill package. Upload the zip to Agensi, or copy the folder
into your agent's skills directory.

## Usage

    python scripts/run.py --db path/to/ghost_tracer.db
    python scripts/run.py --db path/to/ghost_tracer.db --json

## License

MIT
