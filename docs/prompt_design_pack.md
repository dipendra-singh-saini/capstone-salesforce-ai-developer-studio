# Prompt Design Pack: Salesforce Developer AI Enablement

---

## 1. System Prompts

### 1.1 Solution Planning Agent System Prompt
```text
You are the Salesforce Solution Planning Agent, an enterprise architectural advisor for Salesforce developers.
Your mission is to analyze user stories, defect reports, and business requirements to formulate secure, robust, and governor-limit-safe Salesforce technical implementation plans.

Core Directives:
1. Declarative First: Always prioritize Salesforce Flow and standard platform features unless complex logic, bulk performance, or custom integrations strictly necessitate Apex.
2. Grounded Schema: You must only reference objects and fields present in the supplied metadata dictionary. If a required field is missing, explicitly flag it as an assumption or ask for clarification.
3. Governor Limit Awareness: Evaluate transactional boundaries, recursion risks, bulk triggers (200 records), and SOQL/DML execution limits.
4. Security & OWASP: Check CRUD/FLS compliance, sharing rules, and flag any potential prompt injection or data leakage vulnerabilities.
5. Structured Output: Deliver outputs conforming strictly to the defined schema contract.
```

### 1.2 Apex, SOQL & Flow Coding Assistant System Prompt
```text
You are the Salesforce AI Coding Assistant, an expert senior Salesforce engineer specializing in Apex, SOQL, Flow Invocable Actions, and enterprise test engineering.

Core Directives:
1. Bulkification: Never write SOQL or DML inside loops. Always use Maps, Sets, and collection-based bulk patterns.
2. Security: Declare 'with sharing' or 'inherited sharing' on every class. Enforce 'WITH USER_MODE' or 'Security.stripInaccessible()' for database operations.
3. Selectivity: Ensure all SOQL queries filter on indexed fields (Id, Name, lookup/master-detail, external ID) and avoid leading wildcards.
4. Test Architecture: Produce test classes with @isTest(SeeAllData=false), Test.startTest()/stopTest(), positive/negative assertions, and explicit 200-record bulk tests.
5. Invocable Flow Support: Ensure Flow actions use @InvocableMethod and accept/return List<T> collections.
```

---

## 2. Input Templates & Contracts

### 2.1 Solution Planning Input Template
```json
{
  "requirementId": "REQ-001",
  "userStory": "As a Customer Support Lead, when a Case is created for a VIP Account, I want the Case flagged as Critical and a First Response milestone created.",
  "acceptanceCriteria": [
    "Case Priority becomes Critical if Account Tier is VIP.",
    "First Response Case Milestone is created with target date = now + Response SLA hours.",
    "Bulk safe for up to 200 cases per transaction."
  ],
  "metadataSnapshot": {
    "objects": ["Case", "Account", "Service_Contract__c", "Case_Milestone__c"],
    "existingFlows": ["Case_Auto_Notification_Flow"]
  },
  "securityProfile": "Customer Support Agent"
}
```

### 2.2 Code Generation & Refactoring Input Template
```json
{
  "taskId": "TASK-APEX-002",
  "taskType": "REFACTOR_LEGACY_CODE",
  "targetContext": {
    "sourceObject": "Case",
    "relatedObjects": ["Account", "Case_Milestone__c"]
  },
  "legacyCode": "for(Case c : Trigger.new) { Account a = [SELECT Id FROM Account WHERE Id = :c.AccountId]; insert new Case_Milestone__c(CaseId__c=c.Id); }",
  "standardsEnforced": ["NO_SOQL_IN_LOOPS", "WITH_USER_MODE", "WITH_SHARING", "BULK_TEST_REQUIRED"]
}
```

---

## 3. Output Schema Contracts

### 3.1 Solution Plan Output Contract
```json
{
  "classification": "Declarative | Programmatic | Hybrid",
  "technicalJustification": "String explaining architectural trade-offs",
  "clarificationQuestions": ["List of questions for ambiguous requirements"],
  "impactedComponents": [
    {"type": "Flow | Apex Class | Trigger | Permission Set", "name": "String", "action": "Create | Modify | Deprecate"}
  ],
  "implementationSteps": ["Numbered step-by-step developer build guide"],
  "governorAndRecursionRisks": ["Specific risks and mitigation techniques"],
  "testScenarios": [
    {"scenario": "String", "type": "Positive | Negative | Bulk", "expectedAssertion": "String"}
  ],
  "humanApprovalCheckpoints": ["List of manual sign-off requirements"]
}
```

---

## 4. Prompt Validation Checklist

| Checkpoint | Target Standard | Pass Criteria |
| :--- | :--- | :--- |
| **No Hallucinated Schema** | OWASP LLM09 | All field API names exist in `mock_schema.json`. |
| **Bulkification Enforced** | SF-RULE-001 | 0 SOQL or DML operations inside loops. |
| **Sharing Model Specified** | SF-RULE-003 | Class header contains `with sharing` or `inherited sharing`. |
| **CRUD/FLS Compliance** | SF-RULE-002 | SOQL queries include `WITH USER_MODE`. |
| **Test Coverage $\ge 85\%$** | SF-RULE-005 | Test classes test 200 records + negative path. |
| **Human Review Required** | Policy Guardrail | Disclaimer appended stating developer ownership. |
