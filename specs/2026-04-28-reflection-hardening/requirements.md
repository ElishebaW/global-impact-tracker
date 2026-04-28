# Reflection Hardening Requirements

## Context

Phase 2 (repo split) is complete. The MCP server lives in the private `global-impact-tracker-mcp` repo. Reflection features — Gemini-based effort estimation and STAR story generation — exist but have no validation or retry coverage.

This phase hardens those features so generated output is credible (grounded in actual CSV metrics), resilient (handles Gemini API failures), and testable (verified by automated evals).

## Goal

Harden the private MCP repo's reflection features so that:

- STAR narratives are provably grounded in live metrics from the CSV
- Gemini API failures surface as actionable errors rather than silent failures
- Automated evals gate merges on narrative accuracy

## In Scope

**All work is in the private `global-impact-tracker-mcp` repo. The public package is unchanged.**

- Retry logic with exponential backoff on all Gemini API calls
- Error handling that surfaces clear messages when Gemini is unavailable
- Promptfoo eval suite using deterministic assertions for STAR narrative accuracy
- Integration test coverage for the full reflection flow end to end

## Out of Scope

- Changes to the public `global_impact_tracker` package
- New product features beyond hardening existing reflection behavior
- Storage changes (CSV remains the source of truth)
- Phase 4 tool exposure
- LLM-as-judge evaluation (deferred to Phase 4 — see note below)

## Constraints

- Stay consistent with the Python and Gemini-first stack (tech-stack.md)
- All narrative output must be grounded in exact numbers from the CSV (mission.md: credibility matters, evidence over vibes)
- Local-first model preserved; no hosted dependencies added in this phase
- Evals must run locally without a live Gemini key (fixture-based inputs)

## Decisions

- Phase 3 is private repo only; public package is not modified
- Eval assertions are **deterministic** — promptfoo `contains` and regex checks verify that generated narratives reference the correct hours saved, latency reduction percentage, and project/task counts from the input metrics snapshot. No second LLM call is needed for Phase 3's accuracy bar.
- Gemini API failures must surface as clear errors — not silent empty or incorrect output
- Narrative accuracy and API reliability are co-equal merge gates

## Deferred: LLM-as-judge (Phase 4)

Phase 4 will introduce qualitative evaluation — assessing whether STAR narratives are coherent and compelling, not just numerically correct. That requires an independent critic model.

The planned approach uses graceful degradation:

1. **Primary: HuggingFace Inference API.** A capable hosted open model as the independent critic, no second paid cloud API key required.
2. **Fallback: locally-run open model via Ollama** (e.g., Llama 3 8B or Qwen 2.5 7B). If the HuggingFace Inference API returns a rate-limit error, the eval runner degrades gracefully to the local Ollama model and continues without failing the suite.

**This introduces Ollama as a paid-tier dependency.** Paid MCP users must install Ollama locally to use the fallback path. That installation requirement must be documented clearly in the Phase 4 spec and in paid-tier setup instructions.

A locally-run 7B–8B model is a weaker judge than a frontier model and will miss subtle qualitative issues. That tradeoff is acceptable for the fallback path given the local-first constraint.
