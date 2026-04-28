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

3. Integration coverage
   - Add an end-to-end test for the full reflection flow: CSV → metrics → Gemini → STAR narrative
   - Cover the success path and the Gemini failure path using a stubbed client
