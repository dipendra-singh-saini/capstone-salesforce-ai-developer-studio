# Salesforce AI Developer Studio: Capstone PoC

An end-to-end AI Enablement suite designed for Salesforce Developers, satisfying all requirements of the AI Enablement Salesforce Developer PoC Use Cases.

---

## 🌟 Solution Highlights & Architecture

### 1. Track 1: Salesforce Solution Planning Agent (Use Case 1)
- **Requirement Ambiguity Detector**: Detects missing object/field specs, personas, and SLA thresholds before engineering begins.
- **Declarative vs Programmatic Decision Engine**: Evaluates trade-offs between Salesforce Flow and Apex to ensure a declarative-first posture.
- **Context Grounding**: Strictly grounds all proposed solutions in the sanitized metadata dictionary (`mock_schema.json`), eliminating field/API hallucinations (OWASP LLM09).
- **Handoff Checklist**: Produces developer build tasks, positive/negative/bulk test scenarios, and recursion guardrails.

### 2. Track 2: Apex, SOQL & Flow Coding Studio (Use Case 2)
- **Legacy Trigger Refactoring**: Transforms un-bulkified triggers into an enterprise Service-Selector pattern with zero SOQL/DML in loops.
- **Selective SOQL Optimizer**: Constructs selective relationship queries with standard indexed filters and `WITH USER_MODE`.
- **Invocable Action Generator**: Creates bulkified `@InvocableMethod` actions for Salesforce Flow.
- **Enterprise Unit Tests**: Generates `@isTest` classes containing `@TestSetup`, `Test.startTest()`, positive assertions, and 200-record bulk tests ($\ge 85\%$ coverage).

### 3. Static Security & Governor Limit Linter
- **Automated AST & Regex Rule Engine**: Inspects Apex snippets in real-time, enforcing governor limits (SOQL/DML in loops), explicit sharing models (`with sharing`), and Field-Level Security (`WITH USER_MODE`).

### 4. ⚡ Live Google AI Studio Integration (`Gemini 2.5 Flash`)
- **Real-Time LLM Reasoning**: Connected to Google AI Studio Gemini API (`gemini-2.5-flash`).
- **Token Optimization & Latency Control**:
  - `thinkingConfig: { thinkingBudget: 0 }` for near-instant inference and zero wasted thinking tokens.
  - Compressed schema context injection from `data/mock_schema.json`.
  - Tuned `maxOutputTokens` per action (e.g. 400 tokens for ambiguity detection, 1200 for unit tests).

---

## 📸 Visual Walkthrough

> **Note:** Screenshots are not included in this repository. Run the app locally (`python server.py`) and open `http://localhost:8000` to see the full interactive workbench.

| Screen | Description |
|--------|-------------|
| 1. Initial Workbench | Dual-track navigation, active governance status, and quick-action scenario loaders |
| 2. Planning Agent | Ambiguity detection, Hybrid Architecture Recommendation, Component Impact Matrix, Build Checklist |
| 3. Coding Studio | Legacy trigger refactoring, bulkified Apex, SOQL optimization, and 200-record bulk unit tests |
| 4. Security Linter | Real-time static code evaluation, compliance scores (Grade A–F), governor limit flags |
| 5. Schema Explorer | Sanitized metadata catalog (Case, Account, Contact, Service_Contract__c, Case_Milestone__c) |
| 6. Deliverables Pack | Architecture diagrams, prompt packs, sample outputs, quality matrices, reflection notes |

---

## 📁 Repository Structure

```
Capstone/
├── data/
│   ├── mock_schema.json            # Sanitized Salesforce metadata catalog (Case, Account, Contact, Service_Contract__c, etc.)
│   └── coding_standards.json       # Governor limit thresholds, CRUD/FLS rules, and OWASP LLM risks
├── docs/
│   ├── architecture_diagram.md     # Architecture spec, Mermaid diagrams & sequence flows
│   ├── prompt_design_pack.md       # Complete system prompts, input/output schemas & validation checklists
│   ├── sample_outputs.md           # 5 verified task outputs (Apex, SOQL, Tests, Refactored triggers, Audit)
│   ├── quality_checklist.md        # Detailed quality scorecard & OWASP LLM risk mitigations
│   └── reflection_and_limitations.md# Reflection note: AI strengths, limitations & developer ownership
├── engine/
│   ├── rules_engine.py             # Python AST/Regex static analysis linter & schema validator
│   └── agent_service.py            # Multi-step agent orchestrator & preloaded scenario runner
├── prompts/
│   ├── planning_agent_prompts.json # Solution planning prompts & contracts
│   └── coding_assistant_prompts.json# Coding assistant prompts & review checklists
├── screenshots/
│   ├── 01_initial_workbench.png
│   ├── 02_solution_planning_agent.png
│   ├── 03_coding_studio_and_tests.png
│   ├── 04_security_and_governor_linter.png
│   ├── 05_mock_schema_explorer.png
│   └── 06_capstone_deliverables.png
├── app/
│   ├── index.html                  # Interactive developer workbench UI
│   ├── styles.css                  # Modern dark-theme glassmorphism styling
│   └── app.js                      # Dynamic client controller & live diff/audit engine
├── server.py                       # Lightweight local HTTP server
└── README.md                       # Project overview & usage instructions
```

---

## 🚀 Running the Interactive Workbench

To run the interactive web application locally:

```bash
python server.py
```

Then open your browser to **`http://localhost:8000`**.

---

## 🛡️ Governance & Security Summary
- **Zero Org Mutations**: AI functions as an accelerator with strictly no direct deployment privileges.
- **Sanitized Data Only**: Zero production credentials, customer PII, or API keys are required or accepted.
- **Mandatory Human-in-the-Loop**: All AI-assisted designs must be tested and reviewed in a sandbox by a Salesforce developer before production handoff.
