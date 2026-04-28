# Reflection Hardening Validation

## Narrative Accuracy

- Pytest assertions confirm `_missing_metrics` correctly identifies narratives that omit hours saved, latency reduction percentage, project count, or task count
- Pytest confirms `generate_star_story` retries with a stronger prompt when metrics are missing from the first response
- Pytest confirms a warning is prepended when metrics are still missing after retry
- All tests run without a live Gemini key (Gemini calls are stubbed)

## API Resilience

- Gemini call failures retry with exponential backoff before surfacing an error
- Exhausted retries return a clear, user-facing error message — no silent empty output
- Unit tests cover the retry behavior and the error path

## Integration

- End-to-end test passes: CSV → metrics → Gemini → STAR narrative returns correctly structured output
- Gemini failure path test passes using a stubbed client

## Merge Gate

- All promptfoo evals pass
- All pytest tests pass
- No public package changes are present on the branch
