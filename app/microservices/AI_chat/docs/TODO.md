# AI Chat Module Execution TODO

This checklist operationalizes the implementation plan. Tackle in order unless a dependency notes otherwise. Update state (☐ ➜ ☑) as we proceed.

## Legend

- P#: Phase alignment (from implementation plan)
- Effort: S (≤2h), M (≤1d), L (>1d)
- Dep: Key prerequisite(s)

---

## 1. Scaffolding & Structure

☑ 1.1 Create package layout:

```filetree
ai_chat/
  __init__.py
  router.py
  config.py
  graph/
    __init__.py
    state.py
    nodes/
      __init__.py
      ingest.py
      intent_classifier.py
      param_collector.py
      context_builder.py
      safety_pre.py
      action_planner.py
      confirmation_gate.py
      action_executor.py
      summarizer.py
      response_composer.py
      safety_post.py
  tools/
    __init__.py
    base.py
    invite_teammate.py
    invite_client.py
    modify_staff_permission.py
    send_reminder_email.py
  services/
    __init__.py
    context_service.py
    summarization_service.py
    safety_service.py
    rate_limiter.py
    audit_service.py
    cache_service.py
  models/
    __init__.py
    db.py (SQLAlchemy table definitions for conversations/messages/summaries/audits)
    schemas.py (Pydantic request/response/action proposal schemas)
  persistence/
    __init__.py
    repository.py (Conversation + Message repo abstraction)
  tests/
    __init__.py
    test_intent_classifier.py
    test_permission_enforcement.py
    test_action_confirmation_flow.py
```
Effort: M

☑ 1.2 Add environment config entries (ENV parsing in `config.py`). Effort: S
☑ 1.3 Wire router into FastAPI application root (non-invasive import & include). Effort: S
☑ 1.4 Add feature flag (ENABLE_AI_CHAT) to allow safe deployment toggle. Effort: S

## 2. Database Layer (Schema + Migration)
☑ 2.1 Define SQLAlchemy models: Conversation, Message, Summary, Audit, RateLimitCounter. Effort: M
☑ 2.2 Write lightweight migration script (manual) or integrate Alembic (decision). Effort: M
☑ 2.3 Add repository functions (create_conversation, append_message, list_recent_messages, store_summary, write_audit). Effort: M
☑ 2.4 Add idempotency helper store (in-memory + optional table/TTL). Effort: S

## 3. Model & Orchestration Abstraction
☑ 3.1 Create model provider interface (generate(messages, mode, json_schema?)). Effort: S
☑ 3.2 Implement Gemini free-tier adapter (stub). Effort: S
☑ 3.3 Place adapter behind factory (env-driven). Effort: S
☑ 3.4 Add tracing IDs to each call. Effort: S

## 4. Graph State & Nodes
☐ 4.1 Define `ChatState` dataclass / Pydantic model. Effort: S
☐ 4.2 Implement IngestNode (input normalization). Effort: S
☐ 4.3 Implement IntentClassifierNode (rule-based initial). Effort: S
☐ 4.4 Implement ParamCollectorNode (missing param detection strategy). Effort: M
☐ 4.5 Implement ContextBuilderNode (hybrid: live queries + cached snapshots). Effort: M
☐ 4.6 Implement SafetyPreCheckNode (basic injection patterns). Effort: S
☐ 4.7 Implement ActionPlannerNode (maps recognized intent → tool proposal JSON). Effort: M
☐ 4.8 Implement ConfirmationGateNode (pending vs confirmed). Effort: S
☐ 4.9 Implement ActionExecutorNode (calls tool + audit). Effort: M
☐ 4.10 Implement SummarizerNode (threshold based). Effort: M
☐ 4.11 Implement ResponseComposerNode (assemble narrative + optional JSON). Effort: S
☐ 4.12 Implement SafetyPostCheckNode (schema + field redaction). Effort: S
☐ 4.13 LangGraph wiring of nodes with transitions. Effort: M

## 5. Tools Layer
☐ 5.1 BaseTool class (name, permission check, validate inputs, execute). Effort: S
☐ 5.2 InviteTeammateTool (simulation mode flag). Effort: M
☐ 5.3 InviteClientTool. Effort: S
☐ 5.4 ModifyStaffPermissionTool (permission bound check). Effort: M
☐ 5.5 SendReminderEmailTool (integrate existing email service). Effort: S
☐ 5.6 Registry + dynamic lookup by action name. Effort: S
☐ 5.7 Idempotency enforcement within applicable tools. Effort: S

## 6. Safety & Compliance
☐ 6.1 Injection pattern list + regex tests. Effort: S
☐ 6.2 Permission boundary validator separate from model output. Effort: S
☐ 6.3 Output JSON schema & validator (Pydantic). Effort: S
☐ 6.4 Redaction utility (emails/PII when not required). Effort: S
☐ 6.5 Action cooldown implementation (per IP + per action). Effort: S

## 7. Conversation Memory & Summarization
☐ 7.1 Token estimator utility (rough heuristics). Effort: S
☐ 7.2 Summarization prompt template + adapter. Effort: S
☐ 7.3 Persistence of summary + pruning logic. Effort: M
☐ 7.4 Tests verifying key fact retention. Effort: S

## 8. Rate Limiting
☐ 8.1 In-memory token bucket implementation. Effort: S
☐ 8.2 Hook into router dependency. Effort: S
☐ 8.3 Action vs general counters separation. Effort: S
☐ 8.4 Basic tests (edge: boundary overrun). Effort: S

## 9. Auditing & Metrics
☐ 9.1 Audit write function (structured). Effort: S
☐ 9.2 Metrics setup (counters/histograms; stub if Prometheus not yet). Effort: S
☐ 9.3 Trace id propagation through nodes. Effort: S
☐ 9.4 Tests ensuring audit on action execution & not on mere proposal. Effort: S

## 10. Testing Suite
☐ 10.1 Unit tests: tools validation & permission edges. Effort: M
☐ 10.2 Integration test: full invite flow (missing param → confirm → execute). Effort: M
☐ 10.3 Integration test: permission denial on excessive elevation. Effort: S
☐ 10.4 Adversarial test: injection attempt. Effort: S
☐ 10.5 Load test harness (lightweight async loop). Effort: M
☐ 10.6 Regression guard: ensure confirmed flag required. Effort: S

## 11. Configuration & Feature Flagging
☐ 11.1 Add ENABLE_AI_CHAT env parsing with default false. Effort: S
☐ 11.2 Conditional router registration. Effort: S
☐ 11.3 Document all config keys in README section. Effort: S

## 12. Documentation
☐ 12.1 Update IMPLEMENTATION.md with real schema examples post-Phase 2. Effort: S
☐ 12.2 Add developer README for chat module (setup & usage). Effort: S
☐ 12.3 Add quickstart snippet for invoking chat endpoint. Effort: S

## 13. Deployment Readiness
☐ 13.1 Health check extension (/chat/health). Effort: S
☐ 13.2 Fallback static FAQ JSON file. Effort: S
☐ 13.3 Latency logging toggle (debug mode). Effort: S

## 14. Post-Phase Enhancements (Backlog)
☐ B1 Vector store evaluation (enterprise docs) – research
☐ B2 Multilingual enablement scaffolding (language detection node)
☐ B3 Voice interface exploration (streaming input adapter)
☐ B4 Advanced analytics dashboard
☐ B5 Policy-based dynamic tool enable/disable

---
## Dependencies Overview
- Tools depend on repository + permission enforcement.
- ActionPlanner depends on IntentClassifier + ParamCollector.
- Summarizer depends on persistence layer & model adapter.
- Safety layers wrap planner + executor.

## Recommended Execution Order (Condensed)
1. Scaffolding (Section 1)
2. DB schema + repos (Section 2)
3. Model abstraction (Section 3)
4. Graph core (Section 4) – start with Ingest → Intent → ResponseComposer (stub)
5. Tools (Section 5) – implement invite teammate first
6. Safety + rate limiting (Sections 6 & 8)
7. Auditing + metrics (Section 9)
8. Summarization (Section 7)
9. Full test matrix (Section 10)
10. Docs + feature flag (Sections 11–12)

---
## Immediate Next Candidate Task
Proceed directly to Section 4 - start with Ingest → Intent → ResponseComposer (stub)
