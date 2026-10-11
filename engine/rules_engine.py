import re
import json
import os

class SalesforceRulesEngine:
    def __init__(self, schema_path=None, standards_path=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.schema_path = schema_path or os.path.join(base_dir, "data", "mock_schema.json")
        self.standards_path = standards_path or os.path.join(base_dir, "data", "coding_standards.json")
        
        self.schema = self._load_json(self.schema_path)
        self.standards = self._load_json(self.standards_path)

    def _load_json(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def analyze_apex(self, code_content: str):
        findings = []
        score = 100

        # Check 1: Sharing model
        if not re.search(r'\b(with\s+sharing|without\s+sharing|inherited\s+sharing)\b', code_content, re.IGNORECASE):
            findings.append({
                "ruleId": "SF-RULE-003",
                "severity": "HIGH",
                "title": "Missing Explicit Class Sharing Declaration",
                "message": "Class does not declare 'with sharing', 'without sharing', or 'inherited sharing'.",
                "recommendation": "Add 'with sharing' or 'inherited sharing' to enforce org security policies."
            })
            score -= 15

        # Check 2: SOQL in loops
        # Look for loops containing [SELECT ...]
        loop_pattern = r'for\s*\([^)]*\)\s*\{([^}]*)\}|while\s*\([^)]*\)\s*\{([^}]*)\}'
        matches = re.finditer(loop_pattern, code_content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            loop_body = match.group(0)
            if re.search(r'\[\s*SELECT\b', loop_body, re.IGNORECASE) or re.search(r'Database\.query\(', loop_body, re.IGNORECASE):
                findings.append({
                    "ruleId": "SF-RULE-001",
                    "severity": "CRITICAL",
                    "title": "SOQL Query Inside Loop (Governor Limit Breach Risk)",
                    "message": "A SOQL query is executed inside a loop. This breaches the 100 SOQL query governor limit in bulk execution.",
                    "recommendation": "Query records outside the loop and store them in a List or Map<Id, SObject>."
                })
                score -= 30
                break

        # Check 3: DML in loops
        for match in re.finditer(loop_pattern, code_content, re.DOTALL | re.IGNORECASE):
            loop_body = match.group(0)
            if re.search(r'\b(insert|update|delete|upsert|Database\.insert|Database\.update|Database\.delete)\s+', loop_body, re.IGNORECASE):
                findings.append({
                    "ruleId": "SF-RULE-001",
                    "severity": "CRITICAL",
                    "title": "DML Operation Inside Loop",
                    "message": "A DML statement is executed inside a loop. This breaches the 150 DML statement governor limit.",
                    "recommendation": "Collect records in a List<SObject> and perform a single bulk DML operation outside the loop."
                })
                score -= 30
                break

        # Check 4: CRUD / FLS Enforcement
        has_soql = bool(re.search(r'\[\s*SELECT\b', code_content, re.IGNORECASE))
        has_security = bool(re.search(r'\b(WITH\s+USER_MODE|WITH\s+SECURITY_ENFORCED|Security\.stripInaccessible|isAccessible\(\)|isCreateable\(\)|isUpdateable\(\))\b', code_content, re.IGNORECASE))
        if has_soql and not has_security:
            findings.append({
                "ruleId": "SF-RULE-002",
                "severity": "HIGH",
                "title": "Missing CRUD/FLS Security Enforcement",
                "message": "SOQL query does not specify 'WITH USER_MODE' or 'WITH SECURITY_ENFORCED' or perform stripInaccessible.",
                "recommendation": "Append 'WITH USER_MODE' to SOQL queries or sanitize inputs with Security.stripInaccessible()."
            })
            score -= 20

        # Check 5: Hardcoded IDs
        if re.search(r"'(?:00[1356789a-zA-Z0-9]{12,15})'", code_content):
            findings.append({
                "ruleId": "SF-RULE-007",
                "severity": "MEDIUM",
                "title": "Hardcoded Salesforce Record ID Detected",
                "message": "Found hardcoded 15/18-character Salesforce record ID in code.",
                "recommendation": "Retrieve IDs dynamically via Custom Metadata Types, Hierarchy Custom Settings, or SOQL."
            })
            score -= 10

        # Check 6: Schema Hallucination Check
        hallucinated_fields = self._check_hallucinated_fields(code_content)
        if hallucinated_fields:
            findings.append({
                "ruleId": "OWASP-LLM09",
                "severity": "HIGH",
                "title": "Potential Schema / Field Hallucination",
                "message": f"References fields or objects not present in validated mock schema: {', '.join(hallucinated_fields)}",
                "recommendation": "Verify field API names against org metadata dictionary."
            })
            score -= 15

        score = max(0, min(100, score))
        grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 50 else "F"

        return {
            "score": score,
            "grade": grade,
            "passed": score >= 75,
            "findingsCount": len(findings),
            "findings": findings
        }

    def _check_hallucinated_fields(self, code: str):
        hallucinations = []
        # Look for custom fields __c
        custom_fields_found = set(re.findall(r'\b([A-Za-z0-9_]+__c)\b', code))
        
        known_custom_fields = set()
        objects = self.schema.get("objects", {})
        for obj_name, obj_data in objects.items():
            if obj_name.endswith("__c"):
                known_custom_fields.add(obj_name)
            for f_name in obj_data.get("fields", {}).keys():
                if f_name.endswith("__c"):
                    known_custom_fields.add(f_name)

        for cf in custom_fields_found:
            if cf not in known_custom_fields:
                hallucinations.append(cf)
        return list(hallucinations)

    def validate_solution_plan(self, plan_text: str):
        # Validate planning checklist
        checks = {
            "hasDeclarativeTradeoff": bool(re.search(r'\b(Flow|Declarative|Apex|Programmatic|Trade-off)\b', plan_text, re.IGNORECASE)),
            "hasGovernorCheck": bool(re.search(r'\b(governor|limit|bulk|bulkification|batch)\b', plan_text, re.IGNORECASE)),
            "hasTestStrategy": bool(re.search(r'\b(test|scenario|coverage|assertion|startTest)\b', plan_text, re.IGNORECASE)),
            "hasSecurityAndRisk": bool(re.search(r'\b(OWASP|CRUD|FLS|sharing|risk|permission)\b', plan_text, re.IGNORECASE)),
            "hasHumanInTheLoop": bool(re.search(r'\b(human|approval|review|developer sign-off|handoff)\b', plan_text, re.IGNORECASE))
        }
        passed_checks = sum(1 for v in checks.values() if v)
        readiness_score = int((passed_checks / len(checks)) * 100)
        return {
            "readinessScore": readiness_score,
            "isReadyForHandoff": readiness_score >= 80,
            "checklist": checks
        }

if __name__ == "__main__":
    engine = SalesforceRulesEngine()
    test_bad_apex = """
    public class BadCaseService {
        public void updateCases(List<Id> caseIds) {
            for(Id cId : caseIds) {
                Case c = [SELECT Id, Priority, Unknown_Custom_Field__c FROM Case WHERE Id = :cId];
                c.Priority = 'High';
                update c;
            }
        }
    }
    """
    results = engine.analyze_apex(test_bad_apex)
    print("Apex Analysis Result:", json.dumps(results, indent=2))
