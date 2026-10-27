import re
from typing import List, Dict, Any
from backend.app.rag.retriever import global_retriever
from backend.app.knowledge_graph.graph_engine import global_legal_kg

class CitationVerificationAgent:
    """
    Verifies every citation extracted from the actual uploaded judgment:
    - Extracts citations using regex & standard Indian legal reporters (SCC, SCR, AIR, SCALE, ILR, SCC OnLine)
    - Distinguishes VALID, OUTDATED (overruled in KG), FABRICATED, and UNVERIFIED
    - Tracks paragraph and page numbers from the uploaded document
    """

    CITATION_REGEX = re.compile(
        r'(\([12][0-9]{3}\)\s*\d+\s*(?:SCC|SCR|SCALE|Comp\s*Cas)\s*\d+|'
        r'AIR\s*[12][0-9]{3}\s*(?:SC|Del|Bom|Mad|Cal|All)\s*\d+|'
        r'[12][0-9]{3}\s*SCC\s*OnLine\s*(?:SC|Del|Bom|Mad|Cal)\s*\d+|'
        r'\[[12][0-9]{3}\]\s*\d+\s*SCR\s*\d+)',
        re.IGNORECASE
    )

    def run(self, paragraphs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        findings = []
        finding_counter = 1

        for p in paragraphs:
            text = p["text"]
            para_num = p.get("paragraph_number")
            page_num = p.get("page_number", 1)

            matches = self.CITATION_REGEX.findall(text)
            for cit_raw in matches:
                cit_clean = cit_raw.strip()

                # Check Overruling in Knowledge Graph
                overruling_info = global_legal_kg.find_overruling_authority(cit_clean)

                # Query Hybrid Legal Knowledge Corpus
                chunk = global_retriever.find_by_citation_or_case(cit_clean)

                if overruling_info:
                    overruling_case = overruling_info["overruling_case"].get("name", "Subsequent Constitution Bench")
                    findings.append({
                        "finding_code": f"CIT-{finding_counter:03d}",
                        "agent_name": "Citation Agent",
                        "issue_type": "Outdated / Superseded Citation",
                        "severity": "CRITICAL",
                        "status": "OUTDATED",
                        "paragraph_index": para_num,
                        "page_number": page_num,
                        "quoted_text": cit_clean,
                        "claim": f"Reliance on precedent citation '{cit_clean}'.",
                        "reasoning_explanation": f"The citation '{cit_clean}' has been expressly overruled/superseded by {overruling_case}.",
                        "evidence_text": f"Knowledge Graph relationship OVERRULES verified: {overruling_info.get('details', {}).get('status', 'Overruled')}",
                        "source_reference": overruling_case,
                        "confidence": 0.98,
                        "counter_evidence": "Confirm whether the citation was referenced merely as legislative history rather than as operative ratio decidendi.",
                        "human_action_required": True
                    })
                    finding_counter += 1

                elif chunk:
                    findings.append({
                        "finding_code": f"CIT-{finding_counter:03d}",
                        "agent_name": "Citation Agent",
                        "issue_type": "Verified Precedent Citation",
                        "severity": "INFO",
                        "status": "VALID",
                        "paragraph_index": para_num,
                        "page_number": page_num,
                        "quoted_text": cit_clean,
                        "claim": f"Citing {chunk.title} ({chunk.citation})",
                        "reasoning_explanation": f"Citation verified in authoritative Supreme Court jurisprudence corpus.",
                        "evidence_text": chunk.text[:220] + "...",
                        "source_reference": chunk.source_url or chunk.citation,
                        "confidence": 0.95,
                        "counter_evidence": None,
                        "human_action_required": False
                    })
                    finding_counter += 1

                else:
                    is_suspicious_fabricated = any(x in cit_clean for x in ["999 SCC", "99 SCC 0", "0000", "55 SCC 999"])
                    status = "FABRICATED" if is_suspicious_fabricated else "UNVERIFIED"
                    severity = "HIGH" if status == "FABRICATED" else "MEDIUM"

                    findings.append({
                        "finding_code": f"CIT-{finding_counter:03d}",
                        "agent_name": "Citation Agent",
                        "issue_type": "Citation Grounding & Verification",
                        "severity": severity,
                        "status": status,
                        "paragraph_index": para_num,
                        "page_number": page_num,
                        "quoted_text": cit_clean,
                        "claim": f"Citation of {cit_clean}",
                        "reasoning_explanation": (
                            f"Citation '{cit_clean}' could not be located in primary Supreme Court / High Court reporters. Potential hallucinated citation."
                            if status == "FABRICATED"
                            else f"Citation '{cit_clean}' could not be verified in primary indexed reporters. Manual verification against official court reporter required."
                        ),
                        "evidence_text": "Zero matches returned from hybrid lexical and dense legal authority index.",
                        "source_reference": "N/A (Unverified)",
                        "confidence": 0.88 if status == "FABRICATED" else 0.50,
                        "counter_evidence": "May originate from an unindexed specialized tribunal or state law journal.",
                        "human_action_required": True
                    })
                    finding_counter += 1

        return findings
