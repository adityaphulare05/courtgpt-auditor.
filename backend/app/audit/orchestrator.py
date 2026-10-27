import time
from typing import Dict, Any, List
from backend.app.ingestion.document_parser import LegalSegmenter
from backend.app.agents.citation_agent import CitationVerificationAgent
from backend.app.agents.precedent_agent import PrecedentAgent
from backend.app.agents.reasoning_agent import ReasoningConsistencyAgent
from backend.app.agents.statute_agent import StatuteInterpretationAgent
from backend.app.agents.bias_agent import BiasDetectionAgent
from backend.app.agents.hallucination_agent import HallucinationGroundingAgent
from backend.app.explainability.synthesis import ExplainabilityAgent, QualityControlAgent

class AuditOrchestrator:
    """
    Multi-Agent Orchestrator executing the 7 specialized agents on the actual uploaded document.
    Emits real step-by-step progress callbacks and logs execution durations.
    """

    def __init__(self):
        self.cit_agent = CitationVerificationAgent()
        self.prec_agent = PrecedentAgent()
        self.reas_agent = ReasoningConsistencyAgent()
        self.stat_agent = StatuteInterpretationAgent()
        self.bias_agent = BiasDetectionAgent()
        self.hall_agent = HallucinationGroundingAgent()
        self.qc_agent = QualityControlAgent()
        self.explain_agent = ExplainabilityAgent()

    def run_audit(self, raw_text: str, progress_callback=None) -> Dict[str, Any]:
        logs = []
        
        # 1. Document Structuring & Legal Segmentation
        if progress_callback: progress_callback("DOCUMENT_ANALYSIS", 15)
        parsed = LegalSegmenter.segment_judgment(raw_text)
        paragraphs = parsed["paragraphs"]
        sections = parsed["sections"]
        case_info = parsed.get("case_info", {})

        raw_findings: List[Dict[str, Any]] = []

        # 2. Citation Agent
        if progress_callback: progress_callback("CITATION_AGENT", 28)
        t0 = time.time()
        cit_findings = self.cit_agent.run(paragraphs)
        raw_findings.extend(cit_findings)
        logs.append({
            "agent_name": "Citation Agent",
            "duration_ms": int((time.time() - t0) * 1000),
            "findings_generated": len(cit_findings),
            "status": "COMPLETED"
        })

        # 3. Precedent Agent
        if progress_callback: progress_callback("PRECEDENT_AGENT", 42)
        t0 = time.time()
        prec_findings = self.prec_agent.run(sections, paragraphs)
        raw_findings.extend(prec_findings)
        logs.append({
            "agent_name": "Precedent Agent",
            "duration_ms": int((time.time() - t0) * 1000),
            "findings_generated": len(prec_findings),
            "status": "COMPLETED"
        })

        # 4. Reasoning Agent
        if progress_callback: progress_callback("REASONING_AGENT", 56)
        t0 = time.time()
        reas_findings = self.reas_agent.run(sections, paragraphs)
        raw_findings.extend(reas_findings)
        logs.append({
            "agent_name": "Reasoning Agent",
            "duration_ms": int((time.time() - t0) * 1000),
            "findings_generated": len(reas_findings),
            "status": "COMPLETED"
        })

        # 5. Statute Agent
        if progress_callback: progress_callback("STATUTE_AGENT", 70)
        t0 = time.time()
        stat_findings = self.stat_agent.run(paragraphs)
        raw_findings.extend(stat_findings)
        logs.append({
            "agent_name": "Statute Agent",
            "duration_ms": int((time.time() - t0) * 1000),
            "findings_generated": len(stat_findings),
            "status": "COMPLETED"
        })

        # 6. Bias Detection Agent
        if progress_callback: progress_callback("BIAS_AGENT", 80)
        t0 = time.time()
        bias_findings = self.bias_agent.run(paragraphs)
        raw_findings.extend(bias_findings)
        logs.append({
            "agent_name": "Bias Detection Agent",
            "duration_ms": int((time.time() - t0) * 1000),
            "findings_generated": len(bias_findings),
            "status": "COMPLETED"
        })

        # 7. Hallucination / Grounding Agent
        if progress_callback: progress_callback("HALLUCINATION_AGENT", 88)
        t0 = time.time()
        hall_findings = self.hall_agent.run(paragraphs)
        raw_findings.extend(hall_findings)
        logs.append({
            "agent_name": "Hallucination / Grounding Agent",
            "duration_ms": int((time.time() - t0) * 1000),
            "findings_generated": len(hall_findings),
            "status": "COMPLETED"
        })

        # Cross-Agent Validation & QC Gate
        if progress_callback: progress_callback("CROSS_VALIDATION", 92)
        clean_findings = self.qc_agent.audit_quality_gate(raw_findings)

        # 8. Explainability Synthesis Agent
        if progress_callback: progress_callback("EXPLAINABILITY_AGENT", 96)
        synthesis = self.explain_agent.synthesize(
            judgment_metadata={"court": case_info.get("court", "Supreme Court of India"), "date": case_info.get("judgment_date", "")},
            raw_findings=clean_findings
        )

        if progress_callback: progress_callback("COMPLETED", 100)

        return {
            "case_info": case_info,
            "parsed_structure": parsed,
            "findings": clean_findings,
            "logs": logs,
            "executive_summary": synthesis["executive_summary"],
            "limitations": synthesis["limitations"],
            "checklist": synthesis["checklist"],
            "metrics": synthesis["metrics"]
        }

global_orchestrator = AuditOrchestrator()
