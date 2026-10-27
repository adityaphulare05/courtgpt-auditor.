import re
from typing import List, Dict, Any
from backend.app.rag.retriever import global_retriever

class HallucinationGroundingAgent:
    """
    Identifies claims and provisions that cannot be grounded in trusted legal sources:
    - Flags non-existent sections (e.g. Section 999 IPC)
    - Verifies quotation groundedness
    """

    def run(self, paragraphs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        findings = []
        finding_counter = 1

        for p in paragraphs:
            text = p["text"]
            para_num = p.get("paragraph_number")
            page_num = p.get("page_number", 1)

            # Check 1: Non-existent section in IPC (> 511)
            fake_sec_match = re.search(r'Section\s*(5[1-9][2-9]|[6-9][0-9]{2,})\s*(?:of\s*(?:the)?\s*)?IPC', text, re.IGNORECASE)
            if fake_sec_match:
                flagged_sec = fake_sec_match.group(0)
                findings.append({
                    "finding_code": f"HALL-{finding_counter:03d}",
                    "agent_name": "Hallucination / Grounding Agent",
                    "issue_type": "Hallucinated Statutory Provision",
                    "severity": "CRITICAL",
                    "status": "CONTRADICTED",
                    "paragraph_index": para_num,
                    "page_number": page_num,
                    "quoted_text": flagged_sec,
                    "claim": f"Reliance on statutory provision '{flagged_sec}'",
                    "reasoning_explanation": "The Indian Penal Code, 1860 ends at Section 511. Any section number above 511 is non-existent.",
                    "evidence_text": "Indian Penal Code, 1860 ends at Section 511 (Punishment for attempting to commit offences).",
                    "source_reference": "India Code (Ministry of Law and Justice)",
                    "confidence": 0.99,
                    "counter_evidence": "Check if an erroneous abbreviation was used for another state act.",
                    "human_action_required": True
                })
                finding_counter += 1

            # Check 2: Verbatim quotation grounding
            quotes = re.findall(r'"([^"]{40,})"', text)
            for q in quotes:
                search_res = global_retriever.search(q, top_k=1)
                if not search_res or search_res[0]["score"] < 1.0:
                    findings.append({
                        "finding_code": f"HALL-{finding_counter:03d}",
                        "agent_name": "Hallucination / Grounding Agent",
                        "issue_type": "Ungrounded / Potential Hallucinated Quotation",
                        "severity": "MEDIUM",
                        "status": "UNVERIFIED",
                        "paragraph_index": para_num,
                        "page_number": page_num,
                        "quoted_text": f'"{q[:100]}..."',
                        "claim": "Attributed quotation within text.",
                        "reasoning_explanation": "The exact quotation could not be verified verbatim in primary indexed Supreme Court repositories.",
                        "evidence_text": "Zero exact phrase matches in primary corpus.",
                        "source_reference": "Corpus Grounding Verifier",
                        "confidence": 0.65,
                        "counter_evidence": "Quotation may be from unindexed witness deposition or trial court record.",
                        "human_action_required": True
                    })
                    finding_counter += 1

        return findings
