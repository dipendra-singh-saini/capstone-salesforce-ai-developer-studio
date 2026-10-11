# Quality & Risk Review Checklist

---

## 1. Quality Checklist Matrix

| Rule ID | Domain | Requirement | Implementation Evidence | Status |
| :--- | :--- | :--- | :--- | :--- |
| **SF-RULE-001** | Bulkification | No SOQL or DML statements inside loops. | All queries execute outside `for` loops into Maps/Lists; DML is bulkified via `Database.insert(records, ...)`. | **PASSED** |
| **SF-RULE-002** | Security (FLS) | Queries and DML must enforce running user permissions. | Verified `WITH USER_MODE` in SOQL queries and `AccessLevel.USER_MODE` in Database methods. | **PASSED** |
| **SF-RULE-003** | Sharing Model | Explicit class sharing keyword. | All generated Apex classes declare `public with sharing class`. | **PASSED** |
| **SF-RULE-004** | Governor Limits | Selectivity and SOQL query caps. | Indexed fields (`Id`, `AccountId__c`, `Status`) filtered; query limits specified. | **PASSED** |
| **SF-RULE-005** | Test Safety | Unit tests with test isolation & bulk volume. | Contains `@TestSetup`, `SeeAllData=false`, `Test.startTest()`, and 200-record bulk tests with `System.Assert`. | **PASSED** |
| **SF-RULE-006** | Declarative First | Flow preferred over custom code where viable. | Recommends Record-Triggered Flow for notifications and field updates, reserving Apex for bulk milestone calculation. | **PASSED** |

---

## 2. OWASP Top 10 for LLMs Risk Analysis

| OWASP LLM Code | Threat Name | Risk Description | Applied Capstone Guardrail |
| :--- | :--- | :--- | :--- |
| **LLM01** | Prompt Injection | User tries to bypass safety filters via jailbreaking prompts. | Input prompts sanitized, strictly parsed against structured JSON schemas. |
| **LLM02** | Insecure Output Handling | AI generates code that executes unvetted operations. | AI cannot deploy directly to Salesforce orgs. Static rule audit + mandatory developer sign-off required. |
| **LLM06** | Sensitive Info Disclosure | Org secrets or customer PII leaked into prompt context. | Strict sanitized mock metadata policy; no real customer records or org access tokens accepted. |
| **LLM09** | Overreliance & Hallucination | LLM invents non-existent custom fields or APIs. | Integrated `SalesforceRulesEngine` cross-references all field names against `mock_schema.json`. |
