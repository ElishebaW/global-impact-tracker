# Repo Split Requirements

## Context

HMAC licensing is complete. The next phase is repo separation so paid MCP functionality and signing-sensitive code are not shipped in the public customer-facing codebase.

This phase should reduce product risk before broader paid distribution while preserving the shared tracker model between free and paid experiences.

## Goal

Separate the project into:

- a public GitHub repo for shared tracking logic, packaging, documentation, and a CLI entrypoint
- a private GitHub repo named `global-impact-tracker-mcp` for MCP functionality, internal key issuance tooling, real signing-backed entitlements, and paid-only tests

The split must preserve local development usability and keep both repos runnable.

## In Scope

- Move the public product shape to shared `core/` logic plus packaging, docs, and a CLI entrypoint
- Move non-public functionality into the private repo, including:
  - the MCP server
  - internal key issuance tooling such as `tools/generate_key.py`
  - signing-secret-backed entitlement logic
  - paid-only tests
- Keep the private repo dependent on the public repo as an installed dependency
- Keep `core/entitlements.py` in the public repo with the same interface but only a placeholder `_SIGNING_KEY`
- Preserve compatibility of the shared tracker model across CLI and MCP flows
- Keep both repos runnable in local development after the split
- Add automated validation that the public repo cannot unlock paid MCP behavior

## Out of Scope

- Hosted backend work
- Gemini proxy work
- New product capabilities beyond the repo split and CLI packaging surface needed for it
- Storage changes away from CSV

## Constraints

- Preserve the local-first product model described in [mission.md](../mission.md)
- Stay consistent with the Python, CSV, and pip-packaging direction in [tech-stack.md](../tech-stack.md)
- Avoid introducing hosted dependencies for core functionality
- Keep shared code organized so the free CLI and paid MCP continue to use the same tracker model

## Decisions

- The public repo includes a CLI entrypoint in this phase
- The private repo includes MCP, internal key issuance tooling, signing-secret-backed entitlements, and paid-only tests
- The private repo consumes the public repo as an installed dependency
- The public repo keeps a placeholder `_SIGNING_KEY` under the same entitlement module path
- Both repos must remain runnable locally after the split
- Automated tests must prove the public repo cannot activate paid MCP behavior
- Internal key issuance remains developer/operator tooling and is not part of either customer-facing free or paid tier

## Implementation Considerations

- Define the CLI entrypoint name and packaging location
- Define public and private package names
- Decide how the private repo pins or references the public package during active development
- Partition tests so public and private concerns can run independently
- Preserve stable import surfaces where practical to minimize downstream churn

## Success Criteria

- Public users can install and run the CLI without shipping paid MCP code
- Private development can install the public package and run MCP behavior against shared core logic
- No real signing secret, internal key issuance tooling, or paid-only implementation detail is present in the public repo
- The separation is validated by automated tests and clear setup documentation
