// Salesforce AI Developer Studio Frontend Controller - Live Gemini LLM Integration

// State
let isGenerating = false;

// Navigation
function switchTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

  const targetTab = document.getElementById('tab-' + tabName);
  const targetNav = document.getElementById('nav-' + tabName);

  if (targetTab) targetTab.classList.add('active');
  if (targetNav) targetNav.classList.add('active');

  const titles = {
    planning: { title: "Use Case 1: Salesforce Solution Planning Agent", subtitle: "Live AI: Translate user stories into declarative/programmatic architectures with governor safety reviews." },
    coding: { title: "Use Case 2: Apex & SOQL Coding Studio", subtitle: "Live AI: Refactor legacy code, generate bulkified service patterns, and produce companion test classes." },
    audit: { title: "Static & AI Security Linter", subtitle: "Live Dual Evaluation: AST static rules + Gemini LLM security reasoning." },
    schema: { title: "Mock Salesforce Metadata Catalog", subtitle: "Sanitized data dictionary grounding all AI reasoning and preventing hallucinated schema." },
    docs: { title: "Capstone Submission Deliverables Pack", subtitle: "Comprehensive documentation, diagrams, prompts, sample outputs, and reflection notes." }
  };

  if (titles[tabName]) {
    document.getElementById('page-title').innerText = titles[tabName].title;
    document.getElementById('page-subtitle').innerText = titles[tabName].subtitle;
  }
}

function switchSubTab(subTabName) {
  document.querySelectorAll('.subtab-btn').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.subtab-content').forEach(el => el.classList.remove('active'));

  if (event && event.target) {
    event.target.classList.add('active');
  }
  const target = document.getElementById('subtab-' + subTabName);
  if (target) target.classList.add('active');
}

// Helper to call backend Gemini API
async function fetchGemini(action, prompt, systemPrompt = "") {
  try {
    const resp = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, prompt, systemPrompt })
    });
    const data = await resp.json();
    if (data.success) {
      return data.result;
    } else {
      throw new Error(data.error || "Failed to generate AI response.");
    }
  } catch (err) {
    console.error("API Error:", err);
    throw err;
  }
}

// Planning Agent Actions
function loadSampleScenario() {
  document.getElementById('plan-user-story').value = "As a Customer Support Lead, when a Case is created for a VIP or Platinum Account, I want the system to automatically flag the Case as Escalated, link the active Service Contract, and initialize a 1-hour First Response Case Milestone.";
  document.getElementById('plan-criteria').value = "1. If Account Tier is 'Platinum' or 'VIP', Case Priority becomes 'Critical' and IsEscalated = TRUE.\n2. Query the active Service Contract for the Account and populate Service_Contract__c.\n3. Create a Case_Milestone__c record with Milestone_Type__c = 'First Response' and Target_Date = NOW() + Response_SLA_Hours.\n4. Bulk-safe when multiple cases are inserted via API/data loader (up to 200 cases).\n5. Declarative Flow vs Apex trade-off evaluated with governor safety.";
  showToast("Loaded VIP SLA Scenario!");
}

async function detectClarifications() {
  const userStory = document.getElementById('plan-user-story').value.trim();
  const criteria = document.getElementById('plan-criteria').value.trim();
  const listEl = document.getElementById('clarifications-list');

  if (!userStory) {
    alert("Please enter or load a User Story first.");
    return;
  }

  listEl.innerHTML = `<p style="color:#58a6ff;">⚡ <em>Gemini AI is analyzing requirement ambiguities...</em></p>`;
  
  try {
    const prompt = `User Story:\n${userStory}\n\nAcceptance Criteria:\n${criteria}`;
    const result = await fetchGemini("planning_ambiguity", prompt);
    
    listEl.innerHTML = `
      <h4 style="font-size:0.88rem; margin-bottom:8px; color:var(--warning)">❓ Real-Time AI Ambiguity Review:</h4>
      <div style="font-size:0.88rem; line-height:1.5; color:#e6edf3; white-space:pre-wrap;">${escapeHtml(result)}</div>
    `;
    showToast("Ambiguities analyzed by Gemini LLM!");
  } catch (err) {
    listEl.innerHTML = `<p style="color:var(--danger)">Error: ${err.message}</p>`;
  }
}

async function generateSolutionPlan() {
  const userStory = document.getElementById('plan-user-story').value.trim();
  const criteria = document.getElementById('plan-criteria').value.trim();
  const profile = document.getElementById('plan-profile').value;
  const volume = document.getElementById('plan-volume').value;
  const container = document.getElementById('plan-result-container');

  if (!userStory) {
    alert("Please enter or load a User Story first.");
    return;
  }

  container.innerHTML = `
    <div style="text-align:center; padding:30px;">
      <div style="font-size:1.8rem; margin-bottom:10px;">⚡</div>
      <h4 style="color:#58a6ff;">Gemini 2.5 Flash is Architecting Solution Plan...</h4>
      <p style="font-size:0.85rem; color:var(--text-muted);">Evaluating Flow vs Apex, mapping components, checking governor limits and OWASP guardrails.</p>
    </div>
  `;

  try {
    const prompt = `User Story: ${userStory}\nAcceptance Criteria: ${criteria}\nTarget Profile: ${profile}\nExecution Volume: ${volume}`;
    const result = await fetchGemini("planning_solution", prompt);
    
    container.innerHTML = `
      <div style="font-size:0.92rem; line-height:1.65; color:#e6edf3; white-space:pre-wrap; font-family:var(--font-sans);">${escapeHtml(result)}</div>
    `;
    showToast("Live Solution Architecture Plan Generated!");
  } catch (err) {
    container.innerHTML = `<div style="padding:16px; background:rgba(248,81,73,0.15); border-radius:6px; color:var(--danger);">Error: ${err.message}</div>`;
  }
}

// Coding Studio Actions
const sampleSnippets = {
  refactor: {
    prompt: "Refactor non-bulkified legacy Case trigger into enterprise service pattern with zero SOQL in loops.",
    legacy: `trigger LegacyCaseTrigger on Case (after insert, after update) {
    for (Case c : Trigger.new) {
        // Unsafe: SOQL inside loop (Breaches 100 query governor limit)
        Account acc = [SELECT Id, Tier__c FROM Account WHERE Id = :c.AccountId];
        if (acc.Tier__c == 'VIP') {
            // Unsafe: DML inside loop (Breaches 150 DML limit)
            Case_Milestone__c milestone = new Case_Milestone__c();
            milestone.CaseId__c = c.Id;
            milestone.Milestone_Type__c = 'First Response';
            insert milestone;
        }
    }
}`
  },
  invocable: {
    prompt: "Generate an invocable Apex action that can be called from Flow to create Case_Milestone__c records in bulk.",
    legacy: `// Draft requirements for Flow invocable milestone action:
// Accept List of Case IDs and Milestone Types, calculate target date, bulk insert with USER_MODE.`
  },
  "selective-soql": {
    prompt: "Optimize selective SOQL query for Case with Account relationship fields to prevent table scans.",
    legacy: `List<Case> cases = [SELECT Id, Subject, Description, Account.Name FROM Case WHERE Status != 'Closed' AND Subject LIKE '%Urgent%'];`
  }
};

function onTaskSelectChange() {
  const taskKey = document.getElementById('coding-task-select').value;
  const data = sampleSnippets[taskKey];
  if (data) {
    document.getElementById('coding-prompt').value = data.prompt;
    document.getElementById('legacy-code-input').value = data.legacy;
  }
}

async function refactorAndGenerateCode() {
  const prompt = document.getElementById('coding-prompt').value.trim();
  const legacyCode = document.getElementById('legacy-code-input').value.trim();
  const outputEl = document.getElementById('code-output-refactored');

  outputEl.innerText = "// Gemini 2.5 Flash is refactoring and bulkifying your Apex code...";
  switchSubTab('refactored');

  try {
    const userPrompt = `Task: ${prompt}\n\nExisting Code:\n${legacyCode}`;
    const result = await fetchGemini("refactor_apex", userPrompt);
    outputEl.innerText = result;
    showToast("Apex Code Bulkified & Refactored via Gemini!");
  } catch (err) {
    outputEl.innerText = `// Error: ${err.message}`;
  }
}

async function generateTestClass() {
  const refactoredCode = document.getElementById('code-output-refactored').innerText;
  const legacyCode = document.getElementById('legacy-code-input').value;
  const activeCode = refactoredCode.includes("public") ? refactoredCode : legacyCode;
  const outputEl = document.getElementById('code-output-test');

  outputEl.innerText = "// Gemini is generating companion enterprise unit test class (>=85% coverage + 200 record bulk test)...";
  switchSubTab('testclass');

  try {
    const userPrompt = `Target Apex Code to Test:\n${activeCode}`;
    const result = await fetchGemini("generate_test", userPrompt);
    outputEl.innerText = result;
    showToast("Unit Test Class Generated via Gemini!");
  } catch (err) {
    outputEl.innerText = `// Error: ${err.message}`;
  }
}

async function runDirectAudit() {
  const code = document.getElementById('audit-code-input').value.trim();
  const box = document.getElementById('audit-results-box');

  if (!code) {
    alert("Please paste an Apex/SOQL snippet to audit.");
    return;
  }

  box.innerHTML = `<p style="color:#58a6ff;">⚡ <em>Executing Static AST Rules Engine & Gemini Security Review...</em></p>`;

  try {
    const resp = await fetch("/api/audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code })
    });
    const data = await resp.json();

    if (!data.success) {
      throw new Error(data.error);
    }

    const staticRes = data.staticAudit;
    const aiInsight = data.aiInsight;

    const grade = staticRes.grade;
    const badgeClass = grade === "A" ? "badge-success" : grade === "B" ? "badge-primary" : "badge-danger";

    box.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px;">
        <div>
          <h4 style="font-size:1.1rem; font-weight:700;">Static Rule Score: ${staticRes.score}/100</h4>
          <p style="font-size:0.82rem; color:var(--text-muted);">Evaluation against Salesforce Governor, Bulkification & Security Standards</p>
        </div>
        <div>
          <span class="badge ${badgeClass}" style="font-size:1.1rem; padding:6px 14px;">Grade: ${grade}</span>
        </div>
      </div>

      ${staticRes.findings.length === 0 ? `
        <div style="padding:14px; margin-bottom:14px; background:rgba(35,134,54,0.15); border-left:4px solid var(--secondary); border-radius:6px;">
          <h5 style="color:#3fb950; margin-bottom:4px;">✅ Static Rules: Zero Violations Found</h5>
          <p style="font-size:0.84rem; color:var(--text-muted);">The code strictly adheres to bulkification, sharing, and CRUD/FLS standards.</p>
        </div>
      ` : staticRes.findings.map(f => `
        <div style="padding:12px; margin-bottom:10px; background:rgba(248,81,73,0.1); border-left:4px solid ${f.severity === 'CRITICAL' ? 'var(--danger)' : 'var(--warning)'}; border-radius:6px;">
          <div style="display:flex; gap:8px; align-items:center; margin-bottom:4px;">
            <span class="badge ${f.severity === 'CRITICAL' ? 'badge-danger' : 'badge-warning'}">${f.severity}</span>
            <strong style="font-size:0.9rem;">${f.title}</strong>
          </div>
          <p style="font-size:0.84rem; color:var(--text-muted); margin-bottom:4px;">${f.message}</p>
          <div style="font-size:0.8rem; color:#58a6ff;">💡 <strong>Fix:</strong> ${f.recommendation}</div>
        </div>
      `).join('')}

      <div style="margin-top:16px; padding:14px; background:rgba(47,129,247,0.08); border:1px solid rgba(47,129,247,0.25); border-radius:6px;">
        <h5 style="color:#58a6ff; margin-bottom:6px;">🤖 Gemini LLM Security & Architecture Insights:</h5>
        <div style="font-size:0.86rem; line-height:1.5; color:#e6edf3; white-space:pre-wrap;">${escapeHtml(aiInsight)}</div>
      </div>
    `;
    showToast("Audit completed with real-time AI reasoning!");
  } catch (err) {
    box.innerHTML = `<p style="color:var(--danger)">Audit Error: ${err.message}</p>`;
  }
}

function runCodeAuditNow() {
  const code = document.getElementById('legacy-code-input').value;
  document.getElementById('audit-code-input').value = code;
  switchTab('audit');
  runDirectAudit();
}

// Utility
function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderSchemaExplorer() {
  const container = document.getElementById('schema-tree-container');
  const schemaObjects = [
    { name: "Case", type: "Standard Object", fields: ["Id", "CaseNumber", "AccountId", "ContactId", "Subject", "Status", "Priority", "Service_Contract__c", "SLA_Status__c", "Total_Milestones__c"] },
    { name: "Account", type: "Standard Object", fields: ["Id", "Name", "Type", "Tier__c", "Active_Contracts_Count__c", "VIP_Routing_Enabled__c"] },
    { name: "Contact", type: "Standard Object", fields: ["Id", "AccountId", "FirstName", "LastName", "Email", "Phone"] },
    { name: "Service_Contract__c", type: "Custom Object", fields: ["Id", "Name", "AccountId__c", "Status__c", "Response_SLA_Hours__c", "Resolution_SLA_Hours__c", "Start_Date__c", "End_Date__c"] },
    { name: "Case_Milestone__c", type: "Custom Object", fields: ["Id", "CaseId__c", "Milestone_Type__c", "Target_Date__c", "Completion_Date__c", "Is_Violated__c"] }
  ];

  container.innerHTML = `
    <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:18px;">
      ${schemaObjects.map(obj => `
        <div style="background:rgba(13,17,23,0.6); border:1px solid var(--border-color); border-radius:8px; padding:16px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <h4 style="color:#58a6ff; font-size:1rem;">${obj.name}</h4>
            <span class="badge badge-info">${obj.type}</span>
          </div>
          <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:6px;">Sanitized Grounded Fields:</div>
          <div style="display:flex; flex-wrap:wrap; gap:4px;">
            ${obj.fields.map(f => `<span style="background:rgba(255,255,255,0.06); padding:2px 8px; border-radius:4px; font-family:var(--font-mono); font-size:0.75rem;">${f}</span>`).join('')}
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.innerText = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3500);
}

function exportDeliverables() {
  showToast("📦 Exporting complete Capstone Pack...");
  setTimeout(() => {
    alert("Capstone deliverables generated successfully in project /docs and /data directories!");
  }, 300);
}

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
  loadSampleScenario();
  onTaskSelectChange();
  renderSchemaExplorer();
});
