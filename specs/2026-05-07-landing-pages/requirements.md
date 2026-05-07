# Phase 9: Landing Page — Requirements

## Context

Global Impact Tracker is published on PyPI and has a working MCP server. There is no product page yet. Engineers discovering the repo have no clear entry point that explains the free vs. paid split or prompts them to request MCP access.

This phase builds a landing page hosted on massavelabs.com (Cloudflare Pages). It does not require a new domain — the page lives as a route within the existing massavelabs.com site.

## Scope

### In scope

- Hero section: headline, one-sentence description, primary CTA
- Free vs. paid tier comparison: what you get on the CLI vs. MCP server
- GitHub badge (repo link, star count)
- CTA wired to the existing MCP key request form (forms.gle/D3mVGqnsDdf18VaM8)
- `pip install global-impact-tracker` shown prominently for the free tier
- Deployed and live at a real URL on massavelabs.com

### Out of scope for Phase 9

- Standalone domain (globalimpacttracker.dev or similar) — deferred
- Animated or live metrics demo — deferred
- Blog, changelog, or docs pages
- Full design system or Figma file
- Team/about page

## Design direction

Match the aesthetic of codeguardian.studio: dark or neutral palette, minimal, developer-focused, CLI-native feel. GitHub badges and code-block-style elements are appropriate. The page should feel consistent with other CLI tools — not a SaaS marketing page.

The palette can run lighter than codeguardian.studio if it fits better alongside the rest of massavelabs.com, but the layout pattern (hero → features → tier split → CTA) should be the same.

## Decisions

### Host on massavelabs.com, not a standalone domain

**Why:** massavelabs.com is already deployed on Cloudflare Pages, so there is no new infrastructure to set up. A standalone domain adds DNS management and a separate deploy pipeline before Phase 9 even ships. Hosting under the existing site gets the page live faster with zero new ops burden.

**Tradeoff:** The URL will be something like `massavelabs.com/impact-tracker` rather than `globalimpacttracker.dev`. A standalone domain can be added in a later phase once there is evidence users want a dedicated presence.

### Static HTML/CSS/JS — no build step

**Why:** Cloudflare Pages supports static files natively. No Node toolchain, no bundler config, no CI changes needed. A self-contained page is the simplest artifact that satisfies the goal.

**Tradeoff:** If the page grows into multiple routes or needs dynamic data (live GitHub star count, live metrics), a static approach will need to be revisited. That is not a Phase 9 concern.

### Reuse existing CTA form

**Why:** The Google Form for MCP key requests is already live and operational. Wiring the CTA to it avoids building any new backend contact flow.

## Reference

- Aesthetic reference: codeguardian.studio
- MCP key request form: https://forms.gle/D3mVGqnsDdf18VaM8
- PyPI package: https://pypi.org/project/global-impact-tracker/
- GitHub repo: https://github.com/ElishebaW/global-impact-tracker
- Hosting: massavelabs.com on Cloudflare Pages
