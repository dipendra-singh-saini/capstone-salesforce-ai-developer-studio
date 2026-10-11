# Reflection & Limitations Note

---

## 1. Where AI Assisted Effectively
1. **Boilerplate & Pattern Acceleration**: The assistant reduced developer setup time by instantly structuring the Trigger-Handler-Service-Selector architectural separation and generating invocable wrappers.
2. **Bulkification Refactoring**: Legacy snippets with nested SOQL queries were transformed into `Map<Id, SObject>` lookups, immediately resolving governor limit vulnerabilities.
3. **Comprehensive Test Generation**: Automatically constructed `@TestSetup` methods, 200-record bulk tests, and modern `System.Assert` assertions.
4. **Architectural Trade-Off Analysis**: Structured clear arguments for Declarative (Flow) vs Programmatic (Apex), preventing over-engineering.

---

## 2. Model Limitations & Failure Modes Encountered
1. **Implicit Schema Assumptions**: In early iterations without grounding, general LLMs often invent custom fields (e.g. `Account.VIP_Level__c` instead of `Account.Tier__c`). **Mitigation**: Schema grounding against `mock_schema.json` and linter checks.
2. **Complex Governor Limit Nuance**: While simple loops are easily caught, complex multi-object recursion (e.g., Flow calling Invocable Apex that fires another Trigger) requires human developer foresight.
3. **Contextual Business Nuance**: Nuances such as timezone calculation across business hours vs standard calendar hours require developer clarification.

---

## 3. Developer-Owned Responsibilities (Human-in-the-Loop)
- **Deployment Sign-Off**: The AI must never directly deploy code to QA, UAT, or Production orgs.
- **Sandbox Regression Testing**: Developers must run test suites in a scratch org or sandbox.
- **Security & Data Classification**: Verifying that permissions and sharing models match company compliance policies.
- **Prompt Sanitization**: Ensuring no live org secrets or real customer PII are pasted into prompts.
