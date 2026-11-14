# Agent Cost Auditor

[![Agensi](https://img.shields.io/badge/Agensi-Agent_Cost_Auditor-blue)](https://www.agensi.io/r/CONTEXTBRIDGE?to=/skills/agent-cost-auditor)

A SKILL.md package for AI agents that audits an agent's tool-call or reasoning log for wasted tokens and prints a quantified savings estimate.

## What it does

Reads a local SQLite log from `ghost-tracer` or `ghost-reason` and reports:
- **Redundant tool calls:** same tool + same args repeated
- **Retry loops:** same tool called again immediately after an error
- **Duplicate reasoning steps**

Prints an estimated token and dollar savings per run.

## Usage

Requires Python 3.9+. No external packages needed.

```bash
python scripts/run.py --db path/to/ghost_tracer.db
python scripts/run.py --db path/to/ghost_tracer.db --json
```

## License

MIT

---

### Ready-to-use Agent Skills
Want your AI agent to use this tool automatically? Install the **Agent Cost Auditor** skill on Agensi.
> **[Get Agent Cost Auditor on Agensi](https://www.agensi.io/r/CONTEXTBRIDGE?to=/skills/agent-cost-auditor)**
