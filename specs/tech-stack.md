# Tech Stack

## v1 stack decisions

- Language/runtime: Python for both the CLI and the MCP server
- Product split: CLI for free users, MCP server for paid users
- Storage: CSV as the system of record
- AI provider: Gemini-first
- Distribution: pip-installable package

## Why this stack

Python fits both the local CLI and MCP server use cases, keeps implementation surface area small, and matches the current codebase.

CSV is the right storage format for v1 because it is local, transparent, easy to debug, and already aligned with the current tracker model. It keeps the product simple while the shape of the data and workflows is still settling.

Gemini-first is the right default for now because the current product is using the free tier. Provider abstraction can wait until there is real pressure to support more than one LLM backend.

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

- Keep `core/` as the shared tracking logic
- Keep MCP-specific paid features isolated in `mcp/`
- Separate repos as described in `PLAN.md` when licensing work lands
- Avoid premature infrastructure or hosted dependencies for core functionality
