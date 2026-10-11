import json
import os
import re
from engine.rules_engine import SalesforceRulesEngine

class SalesforceAgentService:
    def __init__(self):
        self.rules_engine = SalesforceRulesEngine()
        self.scenarios = self._init_scenarios()

    def _init_scenarios(self):
        return [
            {
                "id": "scenario-1",
                "title": "VIP Case Routing & SLA Milestone Automation",
                "type": "planning",
                "userStory": "As a Customer Support Lead, when a Case is created for a VIP or Platinum Account, I want the system to automatically flag the Case as Escalated, link the active Service Contract, and initialize a 1-hour First Response Case Milestone.",
                "acceptanceCriteria": "1. If Account Tier is 'Platinum' or 'VIP', Case Priority becomes 'Critical' and IsEscalated = TRUE.\n2. Query the active Service Contract for the Account and populate Service_Contract__c.\n3. Create a Case_Milestone__c record with Milestone_Type__c = 'First Response' and Target_Date = NOW() + Response_SLA_Hours.\n4. Bulk-safe when multiple cases are inserted via API/data loader (up to 200 cases).\n5. Declarative Flow vs Apex trade-off evaluated with governor safety.",
                "clarifications": [
                    "What should happen if an Account has multiple active contracts? (Answer: Pick the most recently created active contract).",
                    "Should milestone creation trigger email alerts? (Answer: Handled by existing Case_Auto_Notification_Flow).",
                    "Do support agents have Edit permissions on Service_Contract__c? (Answer: Read-only on Contract, Edit on Case)."
                ],
                "recommendation": {
                    "architecture": "Hybrid: Record-Triggered Flow (After Save) + Invocable Apex Action for SLA Milestone Calculation",
                    "justification": "Flow handles simple field updates and orchestrates after-save triggers declaratively. Invocable Apex handles business-hours date/time calculation and bulkified milestone record generation without exhausting SOQL queries.",
                    "impactedComponents": [
                        {"type": "Flow", "name": "Case_VIP_SLA_Orchestrator_Flow", "action": "Create"},
                        {"type": "Apex Class", "name": "CaseMilestoneService.cls", "action": "Create"},
                        {"type": "Apex Class", "name": "CaseMilestoneInvocable.cls", "action": "Create"},
                        {"type": "Test Class", "name": "CaseMilestoneServiceTest.cls", "action": "Create (>=85% coverage)"},
                        {"type": "Permission Set", "name": "Support_Agent_Case_SLA_Access", "action": "Update"}
                    ],
                    "implementationSteps": [
                        "1. Create Invocable Apex method `createFirstResponseMilestones(List<CaseMilestoneRequest> requests)` in `CaseMilestoneInvocable.cls`.",
                        "2. Enforce `with sharing` and `WITH USER_MODE` query on `Service_Contract__c`.",
                        "3. Configure Record-Triggered Flow on `Case` (After Create) filtered where `Account.Tier__c IN ('VIP', 'Platinum')`.",
                        "4. Flow executes Update Records on trigger Case (`Priority = Critical`, `IsEscalated = true`).",
                        "5. Flow calls Invocable Apex passing `CaseId`, `AccountId`, and `CreatedDate`.",
                        "6. Deploy companion unit test `CaseMilestoneServiceTest` testing bulk 200 case insertion."
                    ],
                    "riskReview": [
                        "Governor Limit Risk: Ensure SOQL on Service_Contract__c is bulkified across all 200 cases in trigger batch.",
                        "OWASP LLM09 Guard: Verified fields `Tier__c`, `Service_Contract__c`, `Case_Milestone__c.Milestone_Type__c` exist in metadata schema.",
                        "Recursion Risk: After-save flow updates same record fields — use Fast Field Updates (Before Save) for Case field modifications to avoid re-triggering recursive flow loops."
                    ]
                }
            },
            {
                "id": "scenario-2",
                "title": "Legacy Trigger Refactoring & Bulkification",
                "type": "coding",
                "developerTask": "Refactor non-bulkified legacy Case trigger logic into enterprise Service-Selector pattern with zero SOQL inside loops and full CRUD/FLS compliance.",
                "legacyCode": "trigger LegacyCaseTrigger on Case (after insert, after update) {\n    for (Case c : Trigger.new) {\n        // Unsafe: SOQL inside loop\n        Account acc = [SELECT Id, Tier__c FROM Account WHERE Id = :c.AccountId];\n        if (acc.Tier__c == 'VIP') {\n            // Unsafe: DML inside loop\n            Case_Milestone__c milestone = new Case_Milestone__c();\n            milestone.CaseId__c = c.Id;\n            milestone.Milestone_Type__c = 'First Response';\n            insert milestone;\n        }\n    }\n}",
                "refactoredCode": "public with sharing class CaseTriggerHandler {\n    public static void handleAfterInsert(List<Case> newCases) {\n        Set<Id> accountIds = new Set<Id>();\n        List<Case> vipCases = new List<Case>();\n        \n        for (Case c : newCases) {\n            if (c.AccountId != null) {\n                accountIds.add(c.AccountId);\n            }\n        }\n        \n        if (accountIds.isEmpty()) {\n            return;\n        }\n        \n        // Bulkified SOQL with explicit FLS check and index filter\n        Map<Id, Account> accountMap = new Map<Id, Account>([\n            SELECT Id, Tier__c \n            FROM Account \n            WHERE Id IN :accountIds \n            WITH USER_MODE\n        ]);\n        \n        List<Case_Milestone__c> milestonesToInsert = new List<Case_Milestone__c>();\n        for (Case c : newCases) {\n            if (c.AccountId != null && accountMap.containsKey(c.AccountId)) {\n                if (accountMap.get(c.AccountId).Tier__c == 'VIP') {\n                    milestonesToInsert.add(new Case_Milestone__c(\n                        CaseId__c = c.Id,\n                        Milestone_Type__c = 'First Response',\n                        Target_Date__c = System.now().addHours(1)\n                    ));\n                }\n            }\n        }\n        \n        // Bulk DML outside loop with exception handling\n        if (!milestonesToInsert.isEmpty()) {\n            Database.insert(milestonesToInsert, true, AccessLevel.USER_MODE);\n        }\n    }\n}",
                "testClassCode": "@isTest\nprivate class CaseTriggerHandlerTest {\n    @TestSetup\n    static void setupTestData() {\n        Account vipAccount = new Account(\n            Name = 'Acme Corp VIP',\n            Tier__c = 'VIP'\n        );\n        insert vipAccount;\n    }\n    \n    @isTest\n    static void testBulkMilestoneCreationForVIP() {\n        Account acc = [SELECT Id FROM Account WHERE Name = 'Acme Corp VIP' LIMIT 1];\n        \n        List<Case> bulkCases = new List<Case>();\n        for (Integer i = 0; i < 200; i++) {\n            bulkCases.add(new Case(\n                Subject = 'Bulk VIP Test Case ' + i,\n                AccountId = acc.Id,\n                Priority = 'High',\n                Origin = 'Email'\n            ));\n        }\n        \n        Test.startTest();\n        insert bulkCases;\n        Test.stopTest();\n        \n        List<Case_Milestone__c> createdMilestones = [\n            SELECT Id, CaseId__c, Milestone_Type__c \n            FROM Case_Milestone__c \n            WHERE Milestone_Type__c = 'First Response'\n            WITH USER_MODE\n        ];\n        \n        System.Assert.areEqual(200, createdMilestones.size(), 'Expected 200 bulk milestone records to be created.');\n    }\n}"
            },
            {
                "id": "scenario-3",
                "title": "Selective SOQL Query & Relationship Optimizer",
                "type": "coding",
                "developerTask": "Write a selective SOQL query on Case and Account to retrieve open cases with active SLA details without causing table scans.",
                "legacyCode": "// Bad practice: Negative condition, leading wildcard, no user mode\nList<Case> cases = [SELECT Id, Subject, Description, Account.Name, Account.Tier__c FROM Case WHERE Status != 'Closed' AND Subject LIKE '%Urgent%'];",
                "refactoredCode": "// Optimized Selective SOQL Query\nList<Case> selectiveCases = [\n    SELECT Id, CaseNumber, Subject, Status, Priority, \n           AccountId, Account.Name, Account.Tier__c, \n           Service_Contract__r.Name, Service_Contract__r.Response_SLA_Hours__c\n    FROM Case\n    WHERE Status IN ('New', 'In Progress', 'Escalated')\n      AND Account.Tier__c = 'VIP'\n      AND CreatedDate = LAST_N_DAYS:30\n    WITH USER_MODE\n    LIMIT 500\n];",
                "testClassCode": "@isTest\nprivate class CaseSelectorTest {\n    @isTest\n    static void testSelectiveQueryReturnsVIPCases() {\n        Account acc = new Account(Name = 'Selective Test Acc', Tier__c = 'VIP');\n        insert acc;\n        \n        Case c = new Case(Subject = 'Urgent Issue', AccountId = acc.Id, Status = 'New');\n        insert c;\n        \n        Test.startTest();\n        List<Case> results = [SELECT Id, CaseNumber, Account.Name FROM Case WHERE Status IN ('New', 'Escalated') AND Account.Tier__c = 'VIP' WITH USER_MODE];\n        Test.stopTest();\n        \n        System.Assert.isFalse(results.isEmpty(), 'Query should selectively return the VIP test case.');\n    }\n}"
            }
        ]

    def get_all_scenarios(self):
        return self.scenarios

    def get_scenario_by_id(self, scenario_id: str):
        for s in self.scenarios:
            if s["id"] == scenario_id:
                return s
        return None

    def audit_code(self, code_text: str):
        return self.rules_engine.analyze_apex(code_text)

    def audit_plan(self, plan_text: str):
        return self.rules_engine.validate_solution_plan(plan_text)

if __name__ == "__main__":
    service = SalesforceAgentService()
    print("Scenarios loaded:", len(service.get_all_scenarios()))
