import pytest
from backend.app.rag.retriever import global_retriever
from backend.app.knowledge_graph.graph_engine import global_legal_kg
from backend.app.audit.orchestrator import global_orchestrator
from backend.app.evaluation.benchmark import BenchmarkEvaluationEngine

STRESS_TEST_JUDGMENT = """
IN THE SUPREME COURT OF INDIA
CRIMINAL APPELLATE JURISDICTION
CRIMINAL APPEAL NO. 450 OF 2024

Appellant: Rajesh Kumar
v.
Respondent: State of NCT of Delhi

JUDGMENT
Dated: 12th February 2024

1. This appeal arises out of the conviction under Section 304B and Section 999 IPC.

2. The marriage between the appellant and the deceased took place twelve years prior to the alleged incident. Learned counsel argued that Section 304B requires the incident to occur within seven years.

3. We place reliance on the landmark judgment of this Court in ADM Jabalpur v. Shivkant Shukla, (1976) 2 SCC 521, to hold that fundamental liberties can be suspended at executive discretion. Furthermore, we cite with approval the principle in State v. Unknown (2024) 999 SCC 0000.

4. In our considered opinion, the prosecution failed to prove the charges beyond reasonable doubt and material witnesses turned hostile.

5. Furthermore, comments on the victim having loose morals were recorded during trial.

6. In conclusion, having considered the entire record, the conviction is upheld and the appeal is dismissed.
"""

def test_retriever():
    res = global_retriever.search("Article 21 life and personal liberty", top_k=2)
    assert len(res) > 0
    assert "Article 21" in res[0]["chunk"]["title"]

def test_knowledge_graph_overruling():
    overruling = global_legal_kg.find_overruling_authority("(1976) 2 SCC 521")
    assert overruling is not None
    assert "Puttaswamy" in overruling["overruling_case"]["name"]

def test_audit_orchestration_finds_all_issues():
    result = global_orchestrator.run_audit(STRESS_TEST_JUDGMENT)
    findings = result["findings"]
    issue_types = [f["issue_type"] for f in findings]
    statuses = [f["status"] for f in findings]

    # Verify Citation Agent detected Outdated & Fabricated citations
    assert any("Outdated" in it for it in issue_types)
    assert "FABRICATED" in statuses or "OUTDATED" in statuses

    # Verify Reasoning Agent detected internal contradiction
    assert any("Contradiction" in it for it in issue_types)

    # Verify Hallucination Agent detected Section 999 IPC
    assert any("Hallucinated" in it for it in issue_types)

    # Verify Bias Agent flagged linguistic stereotype
    assert any("Bias" in it or "Linguistic" in it for it in issue_types)

    # Verify Synthesis metrics
    assert result["metrics"]["critical_findings"] > 0
    assert len(result["checklist"]) > 0

def test_benchmark_engine():
    res = BenchmarkEvaluationEngine.run_benchmark_suite()
    assert len(res["comparison_table"]) == 4
    assert len(res["ablation_study"]) == 5
