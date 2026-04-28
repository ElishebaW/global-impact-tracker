# Reflection Hardening Plan

1. Gemini API resilience
   - Add retry logic with exponential backoff to all Gemini API calls
   - Define a consistent error type for Gemini unavailability
   - Return a clear error message to the MCP caller when retries are exhausted
   - Add unit tests for retry behavior and error surface

2. STAR narrative accuracy enforcement
   - Audit the existing STAR story generation prompt for grounding instructions
   - Tighten the prompt to explicitly require exact numbers from the metrics input
   - Add a verification step to confirm generated text references correct metric values before returning to the caller

3. Promptfoo eval suite
   - Define test cases using fixture metrics snapshots as input
   - Assert that generated STAR narratives reference correct hours saved, latency reduction percentage, and task/project counts
   - Assert that no value appears in the narrative that is absent from the input metrics
   - Integrate evals into the local dev workflow

4. Integration coverage
   - Add an end-to-end test for the full reflection flow: CSV → metrics → Gemini → STAR narrative
   - Cover the success path and the Gemini failure path using a stubbed client
