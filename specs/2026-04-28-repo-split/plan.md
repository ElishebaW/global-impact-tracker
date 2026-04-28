# Repo Split Plan

1. Define target repo boundaries and packaging surfaces
   - Map current files into public versus private ownership
   - Define package names, CLI entrypoints, and dependency lists
   - Define the import contract from the private repo into the installed public package

2. Prepare the public repo shape
   - Add or confirm the CLI entrypoint
   - Keep shared tracking logic in `core/`
   - Replace the public signing key with a placeholder while preserving the entitlement API
   - Update packaging and documentation for free CLI installation and usage

3. Prepare the private repo shape
   - Create the private `global-impact-tracker-mcp` repo
   - Move the MCP server, internal key issuance tooling, and paid-only tests into the private layout
   - Wire private code to consume the installed public package
   - Preserve paid entitlement checks and MCP behavior with private signing material
   - Keep operator key issuance separate from customer-facing free and paid product surfaces

4. Update testing and validation coverage
   - Split test suites between public and private concerns
   - Add automated checks proving paid MCP access cannot be activated from the public repo
   - Add validation for local development flows in both repos

5. Complete cutover and release-readiness checks
   - Verify both repos install and run cleanly from scratch
   - Verify versioning and dependency workflow between repos
   - Finalize migration notes, setup docs, and follow-up cleanup items
