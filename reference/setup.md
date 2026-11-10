# Agent Cost Auditor - Setup

## 1. Install the log source

The auditor reads SQLite databases produced by either:

- ghost-tracer (tool calls): pip install ghost-tracer
- ghost-reason (reasoning steps): pip install ghost-reason

You only need one. If you already have a ghost_tracer.db or ghost_reason.db
from earlier use, skip this step.

## 2. Locate your database

By default:

- ghost-tracer writes to ghost_tracer.db in the current directory
- ghost-reason writes to ghost_reason.db in the current directory

Pass an explicit path with --db if yours is elsewhere.

## 3. Run the auditor

    python scripts/run.py --db ghost_tracer.db

## 4. What the numbers mean

- Redundant calls: same tool, identical arguments, repeated. Missing memoization.
- Retry loops: same tool called again immediately after an error. Retry policy
  with no backoff and no cap.
- Duplicate thoughts: the agent produced the same reasoning step twice in a
  row. Context window dropped the earlier thought.

## 5. Acting on the report

1. Fix redundant calls first - largest single source of waste.
2. Add a retry cap + backoff for any tool with retry loops.
3. For duplicate thoughts, raise the context retention window or add a
   "last N thoughts" summary before the model call.

## 6. Re-run after changes

Compare the token-saved estimate before and after. A successful optimization
should drop redundant calls to near-zero.
