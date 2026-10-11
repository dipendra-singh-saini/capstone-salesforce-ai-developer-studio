# Architecture & System Design: Salesforce AI Developer Studio

---

## 1. System Overview

The **Salesforce AI Developer Studio** is an AI enablement system composed of two specialized tracks:
1. **Salesforce Solution Planning Agent (Use Case 1)**: Analyzes requirements, checks metadata schemas, recommends declarative (Flow) vs programmatic (Apex) solutions, generates build checklists, test scenarios, and security/governor-limit risk reviews.
2. **Salesforce Apex, SOQL & Flow Coding Assistant (Use Case 2)**: Generates and refactors Apex classes, creates invocable actions for Flow, optimizes SOQL selectivity, produces robust unit tests ($\ge 85\%$ coverage), and performs real-time static security/governor-limit auditing.

---

## 2. End-to-End Architecture Diagram

```mermaid
flowchart TB
    subgraph Client_Layer ["1. Developer Workstation (UI / IDE)"]
        UI_Input["User Story / Requirement / Legacy Apex"]
        UI_Chat["Interactive Chat & Code Diff Viewer"]
        UI_Scorecard["Security & Governor Limit Scorecard"]
    end

    subgraph Orchestration_Layer ["2. Multi-Step AI Agent Orchestration"]
        Orchestrator["Agent Orchestrator & Workflow Controller"]
        AmbiguityDetector["Ambiguity & Clarification Engine"]
        TradeoffEngine["Declarative vs Programmatic Engine"]
        CodeGenerator["Apex & SOQL Generation Engine"]
    end

    subgraph Knowledge_Layer ["3. Grounding & Mock Schema Repository"]
        SchemaDB[("Mock Metadata Catalog\n(Case, Account, Contact, Service_Contract__c)")]
        StandardsDB[("Salesforce Standards\n(Governor Limits, Sharing, CRUD/FLS)")]
        OWASPRules[("OWASP LLM Security Rules\n(LLM01-LLM10)")]
    end

    subgraph Guardrail_Layer ["4. Static Linter & Guardrail Verifier"]
        Linter["AST & Regex Static Linter\n- SOQL/DML in Loops\n- Sharing Keyword Check\n- WITH USER_MODE Verification"]
        HallucinationChecker["Schema Verifier\n(Flags unverified fields & objects)"]
    end

    subgraph Delivery_Layer ["5. Developer Handoff Artifacts"]
        PlanDoc["Solution Implementation Plan & Checklist"]
        ApexArtifacts["Bulkified Apex, Handlers & Tests"]
        AuditReport["Audit Scorecard (Grade A-F)"]
    end

    %% Connections
    UI_Input --> Orchestrator
    Orchestrator --> AmbiguityDetector
    Orchestrator --> TradeoffEngine
    Orchestrator --> CodeGenerator
    
    SchemaDB -.-> AmbiguityDetector
    SchemaDB -.-> CodeGenerator
    StandardsDB -.-> CodeGenerator
    
    CodeGenerator --> Guardrail_Layer
    Linter --> UI_Scorecard
    HallucinationChecker --> UI_Scorecard
    
    Guardrail_Layer --> UI_Chat
    UI_Chat --> PlanDoc & ApexArtifacts & AuditReport
```

---

## 3. Sequence Diagram: Solution Planning Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Salesforce Developer
    participant Agent as Solution Planning Agent
    participant Schema as Mock Schema Store
    participant Guard as Safety & Rule Engine

    Dev->>Agent: Submit User Story & Acceptance Criteria
    Agent->>Schema: Inspect Object & Field Definitions
    Schema-->>Agent: Return Confirmed Metadata Snapshot
    
    alt Incomplete / Ambiguous Requirements
        Agent-->>Dev: Prompt Clarifying Questions (e.g. Volume, Security Profile)
        Dev->>Agent: Provide Requirement Clarifications
    end

    Agent->>Agent: Evaluate Declarative (Flow) vs Programmatic (Apex) Trade-offs
    Agent->>Guard: Verify Proposed Changes against OWASP LLM Guardrails
    Guard-->>Agent: Validation Passed (No Hallucinated Schema)
    
    Agent->>Dev: Output Structured Solution Plan:
    Note over Agent,Dev: 1. Architecture Classification<br/>2. Impacted Components Matrix<br/>3. Step-by-Step Build Checklist<br/>4. Test Scenarios (Bulk/Positive/Negative)<br/>5. Governor Limit & Risk Review
    Dev->>Dev: Human-in-the-Loop Review & Approval
```

---

## 4. Sequence Diagram: Code Refactoring & Security Audit Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Salesforce Developer
    participant Assistant as Coding Assistant
    participant Linter as Static Rules Engine
    participant LLM as Code Refactoring Engine

    Dev->>Assistant: Submit Legacy Trigger / Non-Bulkified Apex Snippet
    Assistant->>Linter: Run Pre-Audit on Input Code
    Linter-->>Assistant: Flags: SOQL in loop (SF-RULE-001), Missing Sharing (SF-RULE-003)
    
    Assistant->>LLM: Prompt Bulkified Refactoring with 'WITH USER_MODE' & Map Pattern
    LLM-->>Assistant: Returns Bulkified Handler + Companion Test Class
    
    Assistant->>Linter: Run Post-Audit on Generated Code
    Linter-->>Assistant: Score 100/100 (Grade A, Zero Violations)
    
    Assistant->>Dev: Present Side-by-Side Diff, Explanation, Test Class & Security Scorecard
    Dev->>Dev: Developer Review, Sandbox Test & Final Handoff Sign-off
```

---

## 5. Security Guardrails & Human-in-the-Loop Governance

1. **Zero Production Mutation**: The agent operates purely as an advisory planning and code generation workbench. It does not possess direct deployment privileges to production Salesforce environments.
2. **Context Grounding & Hallucination Defense**: Every object and field reference is validated against the static `mock_schema.json` catalog before generation to prevent nonexistent API calls.
3. **Data Privacy**: Input prompts must be sanitized with zero customer PII, secrets, or org tokens.
4. **Mandatory Human Sign-off**: Every AI-generated design and code artifact is stamped with an AI-assistance notice requiring explicit review and sandbox unit testing by a certified Salesforce developer.
