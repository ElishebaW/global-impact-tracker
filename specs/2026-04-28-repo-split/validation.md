# Repo Split Validation

## Public Repo Validation

- A fresh install exposes the CLI entrypoint and core tracking works against CSV data
- Public tests pass
- The public entitlement module rejects malformed and expired keys and cannot enable paid MCP flows with placeholder signing configuration
- The public distribution contains no MCP server, internal key issuance tooling, or real signing secret

## Private Repo Validation

- A fresh install works with the public repo installed as a dependency
- The MCP server starts and imports shared tracking logic from the public package
- Paid-only tests pass
- Key generation and signed-key validation continue to work end to end
- Internal key issuance remains available only in the private/developer-controlled environment, not in customer-facing install paths

## Cross-Repo Validation

- The shared tracker model behaves consistently between CLI and MCP flows
- Versioning and install instructions are documented and reproducible
- Local development setup for both repos works on a clean machine

## Merge Gate

- Both repos are runnable
- Automated tests cover the separation boundary
- Documentation clearly explains free versus paid install and usage paths
