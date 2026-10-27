# CourtGPT Auditor: Research Methodology & Verification Protocol

## 1. Core Research Question
"Can multiple AI agents collaboratively audit the quality and legal consistency of judicial judgments while providing transparent, evidence-backed explanations?"

The framework demonstrates that dividing judicial audit into specialized functional roles (Citation Verification, Precedent Retrieval, Reasoning Entailment, Statutory Ingredient Verification, Linguistic Stereotype Auditing, and Groundedness) yields significantly higher precision and explainability than monolithic single-LLM legal analysis pipelines.

## 2. Research Integrity & Non-Adjudicative Guarantee
- **Tool Boundary**: CourtGPT Auditor is strictly a quality-assurance and legal-consistency research tool. It does NOT declare judgments legally invalid, find judicial misconduct, or replace judicial discretion.
- **Evidence-Backed**: Every flagged issue is paired with primary statutory text or reporter citation evidence, severity level, confidence score, and counter-evidence considerations.
- **Uncertainty Explicit**: Issues lacking definitive index coverage are classified as `UNVERIFIED` rather than hallucinating validation.

## 3. Indian Legal Jurisprudence Mapping
- **Constitutional Core**: Articles 14, 19, 21 (*Maneka Gandhi*, *Puttaswamy* doctrines).
- **Substantive Penal Law**: Indian Penal Code, 1860 (including statutory preconditions such as the 7-year limitation under Section 304B) and Bharatiya Nyaya Sanhita (BNS).
- **Criminal Procedure**: Sections 438 (Anticipatory Bail, *Gurbaksh Sibbia*, *Sushila Aggarwal*), 41/41A (*Arnesh Kumar*), CrPC / Bharatiya Nagarik Suraksha Sanhita (BNSS).
- **Linguistic Stereotype Checks**: Structured against the Supreme Court of India's *Handbook on Combating Gender Stereotypes* (2023).
