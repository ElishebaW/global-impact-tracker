# Task Groups

## 1. Audit and fix pyproject.toml

- Confirm package name, version, description, author, and license fields are correct
- Lock in the canonical CLI entry point name and wire it in `[project.scripts]`
- Verify all runtime dependencies are listed and pinned appropriately
- Ensure `pip install -e .` works in a clean virtualenv with no errors

## 2. Publish to PyPI

- Register the package on PyPI if not already claimed
- Build with `python -m build`
- Publish to TestPyPI first; confirm `pip install --index-url ... global-impact-tracker` installs and the CLI command resolves
- Publish to PyPI once TestPyPI passes
- Add a `__version__` export and confirm it matches the published version

## 3. Rewrite README for free CLI users

- Lead with a one-paragraph product description grounded in the mission
- Install section: `pip install global-impact-tracker` + first log command
- Show what a captured task and a generated STAR story look like (example output)
- Keep free CLI setup fully self-contained in the top section
- Remove any implementation detail that belongs in code comments, not docs

## 4. Add MCP access section (all four clients)

- Open with the limited-time free access offer and a clear CTA
- Link to the Google Form for requesting a license key; describe expected turnaround
- Provide per-client config snippets:
  - **Claude Code**: `claude_desktop_config.json` or `.claude/settings.json` MCP block
  - **Codex CLI**: `codex.json` or equivalent config with `mcpServers` block
  - **Gemini CLI**: Gemini CLI MCP config block and any auth steps
  - **Windsurf**: Windsurf MCP settings panel config
- Required env vars for each client: `IMPACT_TRACKER_LICENSE_KEY` and `GEMINI_API_KEY`
- Note the optional developer-side vars (`HUGGINGFACE_API_KEY`) that customers do not set
- **Sample prompts section**: include 4–6 ready-to-paste prompts users can send
  to their AI client right after setup to get started, for example:
  - "Log a task: I refactored the auth middleware, saving about 2 hours"
  - "Show me my impact dashboard"
  - "Generate a STAR story for my work on the payments project"
  - "What engineering decisions did I make this week?"
  - "Generate a cross-project STAR story for a senior engineer interview"

## 5. Naming cleanup

- Audit all references to the CLI command name across README, pyproject.toml,
  and any shell examples; make them consistent with the locked entry point name
- Audit module and package naming for consistency after the repo split
- Remove any stale references to old entry points or removed commands

## 6. Update private MCP repo docs

- Update `global-impact-tracker-mcp` README to reflect PyPI install path for the public package
- Ensure paid-tier setup guide links to the Google Form
- Confirm Ollama setup section still accurate after any public repo changes
