# Reflection Hardening Validation

## Narrative Accuracy

- Promptfoo evals pass: generated STAR narratives contain the correct hours saved, latency reduction percentage, and project/task counts from the input metrics snapshot
- No generated narrative introduces a value that is absent from the input metrics snapshot
- Evals run locally without a live Gemini key (fixture-based inputs)

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
