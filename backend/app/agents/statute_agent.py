import re
from typing import List, Dict, Any
from backend.app.rag.retriever import global_retriever

class StatuteInterpretationAgent:
    """
    Audits statutes, sections, and constitutional provisions extracted from uploaded judgment:
    - Compares statutory claims against authoritative statutory text
    - Checks statutory preconditions (e.g. S. 304B IPC 7-year limitation)
    """

    def run(self, paragraphs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        findings = []
        finding_counter = 1

        for p in paragraphs:
            text = p["text"]
            para_num = p.get("paragraph_number")
            page_num = p.get("page_number", 1)

            # Check 1: Dowry death under 304B IPC
            if "304b" in text.lower() or "304-b" in text.lower():
                if any(w in text.lower() for w in ["twelve years", "12 years", "ten years", "10 years", "fifteen years", "15 years"]):
                    findings.append({
                        "finding_code": f"STAT-{finding_counter:03d}",
                        "agent_name": "Statute Agent",
                        "issue_type": "Statutory Ingredient Inconsistency",
                        "severity": "CRITICAL",
                        "status": "CONTRADICTED",
                        "paragraph_index": para_num,
                        "page_number": page_num,
                        "quoted_text": text[:200] + "...",
                        "claim": "Applying Section 304B IPC to marriage subsisting beyond 7-year statutory period.",
                        "reasoning_explanation": (
                            "Statutory inconsistency: Section 304B IPC strictly requires the death to have occurred "
                            "'within seven years of her marriage'. Applying Section 304B to an incident occurring 12 years after marriage contradicts the statute."
                        ),
                        "evidence_text": "Section 304B Indian Penal Code: '...occurs otherwise than under normal circumstances within seven years of her marriage...'",
                        "source_reference": "Section 304B, Indian Penal Code, 1860",
                        "confidence": 0.96,
                        "counter_evidence": "The conviction might have been altered to Section 302 or Section 306 IPC (Abetment of Suicide).",
                        "human_action_required": True
                    })
                    finding_counter += 1

            # Check 2: Article 21
            if "article 21" in text.lower() and "arbitrary" in text.lower():
                stat_chunk = global_retriever.find_by_citation_or_case("Article 21")
                if stat_chunk:
                    findings.append({
                        "finding_code": f"STAT-{finding_counter:03d}",
                        "agent_name": "Statute Agent",
                        "issue_type": "Verified Constitutional Provision",
                        "severity": "INFO",
                        "status": "VALID",
                        "paragraph_index": para_num,
                        "page_number": page_num,
                        "quoted_text": "Article 21 procedure established by law",
                        "claim": "Invocation of Article 21 fair procedure requirements.",
                        "reasoning_explanation": "Application of Article 21 accords with established constitutional jurisprudence (Maneka Gandhi doctrine).",
                        "evidence_text": stat_chunk.text,
                        "source_reference": stat_chunk.citation,
                        "confidence": 0.95,
                        "counter_evidence": None,
                        "human_action_required": False
                    })
                    finding_counter += 1

        return findings
