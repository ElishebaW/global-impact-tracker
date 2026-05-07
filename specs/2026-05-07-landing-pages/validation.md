# Phase 9: Landing Page — Validation

## Merge criteria

The branch is ready to merge when all of the following are true.

### Live deployment

- [ ] Page is publicly accessible at a real URL on massavelabs.com
- [ ] Page loads without errors in Chrome and Safari (latest)
- [ ] Page is mobile-responsive: no horizontal scroll, readable on 375px viewport

### Content

- [ ] Hero headline clearly communicates what the tool does and who it's for
- [ ] Free and paid tiers are visually distinct and easy to compare
- [ ] `pip install global-impact-tracker` is shown verbatim and copyable
- [ ] CTA for MCP access links to the correct Google Form URL
- [ ] GitHub badge links to the correct repo and renders a star count

### Links and CTAs

- [ ] All external links open correctly (GitHub, PyPI, request form)
- [ ] No broken links (run through a link checker or manual click-through)
- [ ] "Install free CLI" CTA renders the pip command — user can copy it directly

### Design

- [ ] Page palette and typography is consistent with massavelabs.com
- [ ] Code-adjacent aesthetic matches the CLI tool feel (no generic SaaS look)
- [ ] Page does not look broken with system dark mode enabled

## What success looks like

An engineer who discovers the repo or hears about the tool can land on the page, understand the free vs. paid split in under 30 seconds, copy the install command, and click through to request MCP access — without needing to read the README.

## Out of scope for this validation gate

- SEO, analytics, or tracking setup
- Lighthouse score targets
- A/B testing or copy experiments
- Standalone domain (globalimpacttracker.dev)
