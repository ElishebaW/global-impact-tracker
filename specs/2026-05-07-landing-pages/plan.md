# Phase 9: Landing Page — Plan

## Task group 1: Copy and content

1.1 Write hero headline and subheadline (lead with the interview/performance review angle from the README)
1.2 Write the free tier value prop (CLI, local CSV, pip install, open source)
1.3 Write the paid tier value prop (MCP server, STAR story generation, decisions capture, LLM evals)
1.4 Write the free vs. paid comparison table (3–5 rows, no more)
1.5 Finalize CTA copy for both tiers ("Install free CLI" → pip command, "Request MCP access" → form link)

## Task group 2: Page structure and markup

2.1 Scaffold `impact-tracker.html` (or equivalent route) in the massavelabs.com repo
2.2 Build hero section: headline, subheadline, two CTAs, GitHub badge
2.3 Build feature list section: 3–4 bullets per tier, icon or code-block treatment
2.4 Build free vs. paid comparison table
2.5 Build footer / closing CTA block

## Task group 3: Styling

3.1 Match base palette and typography to massavelabs.com
3.2 Apply codeguardian.studio layout pattern: full-width sections, tight spacing, monospace accents
3.3 Add code block for `pip install global-impact-tracker`
3.4 Ensure mobile responsiveness (single-column stack below ~768px)
3.5 Test in both light and dark system preferences if massavelabs.com supports it

## Task group 4: Integration and deploy

4.1 Add page to massavelabs.com navigation or add a direct-link entry point
4.2 Wire all external links: GitHub repo, PyPI, MCP request form
4.3 Confirm GitHub badge renders with correct repo path
4.4 Push to Cloudflare Pages and verify live URL
4.5 Smoke test all CTAs from the live URL
