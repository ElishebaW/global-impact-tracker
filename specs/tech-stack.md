# Tech Stack

## v1 stack decisions

- Language/runtime: Python for the public package and the private MCP companion
- Product split: public CLI/package for free users, private MCP server for paid users
- Storage: CSV as the system of record
- AI provider: Gemini-first in the private paid MCP layer
- Distribution: pip-installable package

## Why this stack

Python fits both the local public package and the private MCP companion, keeps implementation surface area small, and matches the current codebase.

CSV is the right storage format for v1 because it is local, transparent, easy to debug, and already aligned with the current tracker model. It keeps the product simple while the shape of the data and workflows is still settling.

Gemini-first is the right default for now in the paid MCP layer because it keeps the current reflection and reporting path simple. Provider abstraction can wait until there is real pressure to support more than one LLM backend.

Pip installation is the right packaging target because it supports straightforward local setup for both free and paid users without introducing a separate installer path.

## CSV vs SQLite

CSV remains the default for v1.

SQLite would likely make some reads cleaner for:

- aggregate metrics
- dashboard queries
- STAR story input assembly

But those gains are not yet worth the additional complexity, migration work, and schema decisions. The current stance is:

- keep writes and source-of-truth storage in CSV
- design read paths so they can be swapped to SQLite later if query complexity becomes a real bottleneck

Triggers for adopting SQLite later:

- metrics queries become slow or fragile
- multiple derived reports require repeated CSV parsing logic
- story generation needs more structured filtering and joins
- the product adds enough metadata that flat-file handling becomes error-prone

## Architectural direction

- Keep `src/global_impact_tracker/` as the shared public package boundary
- Keep MCP-specific paid features isolated in the private `global-impact-tracker-mcp` repo
- Keep the free CLI and paid MCP companion aligned through the same underlying tracker model
- Treat Gemini-backed reflection, STAR story generation, and decisions capture as private paid-tier concerns unless intentionally promoted into the public package
- Avoid premature infrastructure or hosted dependencies for core functionality
