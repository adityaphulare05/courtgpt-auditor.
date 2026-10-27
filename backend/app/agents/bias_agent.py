import re
from typing import List, Dict, Any

class BiasDetectionAgent:
    """
    FLAGGING SYSTEM ONLY: Analyzes linguistic patterns and demographic references.
    Never declares a judge biased; flags potential linguistic indicators against
    the Supreme Court of India's Handbook on Combating Gender Stereotypes (2023).
    """

    GENDER_STEREOTYPE_PATTERNS = [
        (r'\b(chaste woman|ravished woman|loose morals|easy virtue|fallen woman)\b', 
         "Non-objective gendered moral characterization (deprecated by Supreme Court Gender Stereotypes Handbook 2023)"),
        (r'\b(women are naturally emotional|hysterical female|feminine intuition)\b',
         "Stereotypical generalized gender trait assumption"),
        (r'\b(obedient wife|dutiful wife must|conciliatory attitude)\b',
         "Normative role-based expectation in judicial prose")
    ]

    def run(self, paragraphs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        findings = []
        finding_counter = 1

        for p in paragraphs:
            text = p["text"]
            para_num = p.get("paragraph_number")
            page_num = p.get("page_number", 1)

            for pattern, explanation in self.GENDER_STEREOTYPE_PATTERNS:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for m in matches:
                    matched_str = m.group(0)
                    findings.append({
                        "finding_code": f"BIAS-{finding_counter:03d}",
                        "agent_name": "Bias Detection Agent",
                        "issue_type": "Potential Linguistic / Demographic Bias Indicator",
                        "severity": "MEDIUM",
                        "status": "PARTIALLY_SUPPORTED",
                        "paragraph_index": para_num,
                        "page_number": page_num,
                        "quoted_text": matched_str,
                        "claim": f"Judicial text contains phrase: '{matched_str}'",
                        "reasoning_explanation": (
                            f"Linguistic indicator flagged: {explanation}. "
                            "NOTE: This is a statistical/linguistic indicator only and DOES NOT establish subjective judicial bias or legal invalidity."
                        ),
                        "evidence_text": "Supreme Court of India 'Handbook on Combating Gender Stereotypes' (August 2023), Pages 12-18.",
                        "source_reference": "Supreme Court of India (Administrative / Research Guidelines)",
                        "confidence": 0.88,
                        "counter_evidence": "The phrase may be a direct quotation from a lower court deposition or witness testimony rather than the court's own voice.",
                        "human_action_required": True
                    })
                    finding_counter += 1

        return findings
