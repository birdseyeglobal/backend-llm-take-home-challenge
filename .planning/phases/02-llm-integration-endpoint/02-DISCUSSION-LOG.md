# Phase 2: LLM Integration & Endpoint - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-04-04
**Phase:** 2 — LLM Integration & Endpoint

---

## LLM Library Choice

**Q:** Which LLM library for structured output?
**Selected:** Pydantic AI (user note: "use Pydantic AI")

**Q:** The request body has llm_model: str. How should the servicer handle different model names?
**Selected:** Route by provider prefix (gpt-* → OpenAI, claude-* → Anthropic, gemini-* → Gemini)

**Q:** For Pydantic AI structured output, how should the LLM output model be defined?
**Selected:** Reuse VoiceProfileResponse as result type (separate VoiceProfileLLMResult subset)

**Q:** (Follow-up) Pydantic AI implementation details?
**User note:** Use the Pydantic AI gateway (https://ai.pydantic.dev/gateway/) and store the key in ENV variable

**Q:** Which ENV variable holds the Pydantic AI gateway API key?
**Selected:** PYDANTIC_AI_GATEWAY_API_KEY (user note: "PYDANTIC_AI_GATEWAY_API_KEY")

---

## Version Increment Strategy

**Q:** How should version be computed?
**User note:** Track history — each generate creates a new VoiceProfile object, version = MAX(existing)+1

---

## LLM Error Handling

**Q:** If LLM call fails, what should the endpoint return?
**Selected:** 500 with error detail (Recommended)

---
*Log generated: 2026-04-04*
