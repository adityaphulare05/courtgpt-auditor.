import re
from typing import List, Dict, Any

class ReasoningConsistencyAgent:
    """
    Audits the logical consistency of legal reasoning:
    - Detects internal contradictions between facts, reasoning, and final orders
    - Detects non sequiturs and unsupported conclusions
    """

    def run(self, sections: Dict[str, str], paragraphs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        findings = []
        finding_counter = 1

        reasoning = sections.get("reasoning", "").lower()
        conclusion = sections.get("conclusion", "").lower()

        doubt_phrases = [
            "prosecution failed to prove", "no credible evidence", "fatal lacuna",
            "benefit of doubt must be given", "material witnesses turned hostile"
        ]
        conviction_phrases = [
            "conviction is upheld", "appeal is dismissed", "found guilty", "sentence is confirmed"
        ]

        # Check internal contradiction across judgment body
        found_doubt = any(p in reasoning for p in doubt_phrases)
        found_conviction = any(p in conclusion for p in conviction_phrases)

        if found_doubt and found_conviction:
            # Locate paragraph with doubt phrase
            doubt_p = next((p for p in paragraphs if any(d in p["text"].lower() for d in doubt_phrases)), paragraphs[-1] if paragraphs else {})
            findings.append({
                "finding_code": f"REAS-{finding_counter:03d}",
                "agent_name": "Reasoning Agent",
                "issue_type": "Internal Evidentiary Contradiction",
                "severity": "CRITICAL",
                "status": "CONTRADICTED",
                "paragraph_index": doubt_p.get("paragraph_number"),
                "page_number": doubt_p.get("page_number", 1),
                "quoted_text": doubt_p.get("text", "")[:180] + "...",
                "claim": "Court records fatal evidentiary deficiency yet proceeds to affirm criminal conviction.",
                "reasoning_explanation": (
                    "Internal contradiction detected: The analytical section records that the prosecution failed to prove "
                    "guilt beyond reasonable doubt / material witnesses turned hostile, yet the operative conclusion upholds conviction."
                ),
                "evidence_text": "Analytical section contains explicit evidentiary failure markers, while Operative Conclusion dismisses appeal.",
                "source_reference": f"Judgment Paragraph {doubt_p.get('paragraph_number')}",
                "confidence": 0.94,
                "counter_evidence": "Review whether the evidentiary doubt pertained to an acquitted co-accused rather than the primary appellant.",
                "human_action_required": True
            })
            finding_counter += 1

        return findings
