# ⚖️ CourtGPT Auditor
### An Explainable Multi-Agent AI Framework for Auditing Judicial Judgments and Legal Reasoning

**Target Jurisdiction:** India  
**Project Domain:** Artificial Intelligence, Natural Language Processing, Legal Technology, Explainable AI

CourtGPT Auditor is a research-oriented AI framework designed to support the systematic examination of judicial judgments for potential citation inconsistencies, overlooked precedents, reasoning gaps, statutory verification issues, linguistic stereotypes, and unsupported claims.

The project follows a multi-agent architecture in which specialized AI agents examine different dimensions of a judicial judgment. Its objective is to provide structured, transparent, and evidence-backed observations that help researchers and legal professionals review judgments more efficiently.

> **Important:** CourtGPT Auditor is a decision-support and research tool. It does not determine whether a judgment is legally invalid, establish judicial misconduct, or replace qualified legal professionals or judicial discretion.

---

## 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [Problem Statement](#-problem-statement)
3. [Project Objectives](#-project-objectives)
4. [Research Question](#-research-question)
5. [Key Features](#-key-features)
6. [Multi-Agent Architecture](#-multi-agent-architecture)
7. [Research Methodology](#-research-methodology)
8. [Technology Stack](#-technology-stack)
9. [Project Structure](#-project-structure)
10. [Prerequisites](#-prerequisites)
11. [Installation and Setup](#-installation-and-setup)
12. [Running the Application](#-running-the-application)
13. [API Documentation](#-api-documentation)
14. [Running Automated Tests](#-running-automated-tests)
15. [Docker Deployment](#-docker-deployment)
16. [Research Integrity and Verification](#-research-integrity-and-verification)
17. [Limitations](#-limitations)
18. [Future Scope](#-future-scope)
19. [Contributing](#-contributing)
20. [License](#-license)
21. [Disclaimer](#-disclaimer)

---

## 🔍 Project Overview

Judicial judgments contain complex legal arguments, references to statutes, precedents, factual findings, and judicial reasoning. Reviewing these elements can require considerable time and careful examination of legal sources.

CourtGPT Auditor explores how multiple specialized AI agents can assist in this review process.

Instead of relying on a single general-purpose AI response, the framework separates the auditing task into distinct responsibilities. Each agent focuses on a particular category of potential issue, helping organize the review into understandable and verifiable observations.

The framework is designed around six auditing areas:

- Citation verification
- Precedent retrieval and analysis
- Legal reasoning consistency
- Statutory ingredient verification
- Linguistic stereotype auditing
- Groundedness and hallucination checks

The system aims to make potential issues easier to investigate by associating observations with supporting evidence, severity, confidence, and uncertainty where applicable.

The target jurisdiction is India, with research mapping that includes constitutional principles, criminal law, criminal procedure, judicial precedents, and the Supreme Court of India's 2023 *Handbook on Combating Gender Stereotypes*.

## 🎯 Problem Statement

Manual examination of judicial judgments may require reviewers to cross-reference citations, identify relevant precedents, interpret statutory requirements, evaluate reasoning, and inspect the language used in the judgment.

A general-purpose AI system may produce plausible-sounding explanations without adequately establishing whether its claims are supported by reliable legal sources.

CourtGPT Auditor investigates a structured alternative: dividing the review into specialized agents and organizing their findings into an explainable audit process.

The central challenge is to help reviewers identify potential inconsistencies and areas requiring further investigation without presenting automated observations as definitive legal conclusions.

## 🎯 Project Objectives

1. **Citation verification:** Support the identification of references that may require additional verification.
2. **Precedent analysis:** Help identify potentially relevant or overlooked binding precedents.
3. **Reasoning analysis:** Examine relationships between legal claims, facts, and supporting explanations.
4. **Statutory verification:** Support the examination of statutory requirements relevant to a legal issue.
5. **Linguistic auditing:** Identify potentially stereotypical or problematic language for contextual review.
6. **Groundedness verification:** Distinguish evidence-supported observations from claims that cannot be adequately verified.
7. **Explainability:** Present findings with supporting evidence, severity, confidence, and counter-evidence considerations.
8. **Research evaluation:** Provide a framework for investigating whether specialized agents improve audit quality compared with a single-model approach.

## ❓ Research Question

Can multiple AI agents collaboratively audit the quality and legal consistency of judicial judgments while providing transparent, evidence-backed explanations?

The research methodology proposes comparing specialized functional roles with monolithic, single-LLM legal analysis pipelines in terms of precision and explainability. Any claim of improved performance must be established through actual experiments and reported evaluation results.

## ✨ Key Features

### 1. Multi-agent auditing

The framework separates judicial review into specialized functional responsibilities instead of treating the entire task as one undifferentiated AI query.

### 2. Evidence-backed observations

The research protocol specifies that flagged issues should be associated with relevant statutory text or reporter citations, severity levels, confidence scores, and counter-evidence considerations.

### 3. Explicit uncertainty

When sufficient evidence or index coverage is unavailable, an issue can be classified as `UNVERIFIED` rather than incorrectly presented as verified.

### 4. Indian legal context

The research methodology maps the auditing framework to selected areas of Indian jurisprudence, including constitutional rights, criminal law, criminal procedure, and gender-stereotype guidance.

### 5. API-based backend

The project uses FastAPI and provides a documented local API interface through which supported backend operations can be explored.

### 6. Web frontend

The repository includes a frontend application built with TypeScript and Vite. The frontend can be started independently during development.

### 7. Testing support

The project includes a documented pytest command for running the audit-suite tests.

### 8. Containerized deployment

Docker Compose configuration defines backend and frontend services to support a containerized deployment workflow.

---

## 🧠 Multi-Agent Architecture

CourtGPT Auditor organizes its proposed auditing responsibilities into six specialized agents.

### 1. Citation Agent

**Purpose:** Examine citation-related information and identify references that may require verification.

Potential review areas include the existence of a cited source, reference consistency, and whether the cited material supports the associated claim.

### 2. Precedent Agent

**Purpose:** Support the identification and examination of relevant judicial precedents.

The research methodology highlights the importance of binding precedents and identifies decisions such as *Gurbaksh Singh Sibbia* and *Sushila Aggarwal* as relevant examples within the Indian criminal-procedure context.

### 3. Reasoning Agent

**Purpose:** Examine the logical relationship between legal claims, factual statements, and the explanations offered in a judgment.

Potential observations may include reasoning gaps, unsupported inferences, or inconsistencies that require closer legal examination.

### 4. Statute Agent

**Purpose:** Support verification of statutory requirements relevant to the legal issues under examination.

The research methodology maps the framework to selected provisions of the Indian Penal Code, Bharatiya Nyaya Sanhita, Code of Criminal Procedure, and Bharatiya Nagarik Suraksha Sanhita.

### 5. Bias Agent

**Purpose:** Identify language that may warrant examination for gender stereotypes or other linguistic concerns within the framework's defined scope.

The research protocol references the Supreme Court of India's *Handbook on Combating Gender Stereotypes* (2023).

A flagged expression is an observation for contextual review, not proof of bias or misconduct.

### 6. Hallucination and Groundedness Agent

**Purpose:** Support the identification of statements that lack adequate evidentiary grounding.

The research methodology requires uncertainty to remain explicit. Findings without sufficient verification should not be presented as established facts.

### How the agents fit together

At a conceptual level, the auditing process can be represented as follows:

1. A judicial judgment is selected for examination.
2. Relevant text, claims, references, and legal provisions are identified through the supported processing pipeline.
3. Specialized agents examine their respective auditing dimensions.
4. Potential issues are organized into structured observations.
5. Evidence, severity, confidence, and uncertainty are considered when presenting findings.
6. A reviewer examines the observations and independently evaluates their legal significance.

This describes the intended research workflow. The precise orchestration, evidence-retrieval sequence, and output aggregation should be understood from the implementation in the repository.

---

## 🔬 Research Methodology

The project adopts a research-oriented approach to explainable, multi-agent legal auditing.

### Stage 1: Define the audit dimensions

The overall judicial review problem is divided into citation verification, precedent retrieval, reasoning entailment, statutory ingredient verification, linguistic stereotype auditing, and groundedness.

### Stage 2: Establish a jurisdictional context

The methodology identifies selected Indian constitutional, criminal-law, and criminal-procedure materials relevant to the intended research scope.

### Stage 3: Examine potential issues

Specialized agents examine their assigned dimensions and produce observations for further review.

### Stage 4: Associate evidence

Where possible, observations are linked to primary statutory text or relevant reporter citations.

### Stage 5: Represent uncertainty

The framework distinguishes verified information from findings that remain uncertain or unsupported by available evidence.

### Stage 6: Consider counter-evidence

The research protocol requires counter-evidence considerations so that potential concerns are not presented without acknowledging relevant opposing information.

### Stage 7: Evaluate the approach

The core research question proposes investigating the precision and explainability of specialized agents relative to a single-LLM pipeline.

A rigorous evaluation should use a defined dataset, documented evaluation criteria, a consistent comparison procedure, and reported results. No quantitative performance improvement is claimed here without corresponding experimental evidence.

For the detailed research protocol, see [`RESEARCH_METHODOLOGY.md`](RESEARCH_METHODOLOGY.md).

---

## 🛠️ Technology Stack

The following technologies are supported by the supplied dependency and configuration files.

| Technology | Purpose |
|---|---|
| Python | Backend development and agent implementation |
| FastAPI | Backend API framework |
| Uvicorn | ASGI application server |
| Pydantic | Data validation and settings support |
| SQLAlchemy | Database interaction |
| SQLite | Local relational database support |
| rank-bm25 | BM25 ranking functionality |
| pypdf | PDF processing support |
| PyJWT | JWT-related functionality |
| passlib and bcrypt | Password-related utilities |
| pytest | Automated testing |
| python-multipart | Multipart form-data handling |
| TypeScript | Frontend application development |
| Vite | Frontend development server and build tooling |
| Docker Compose | Multi-service container orchestration |

The precise use of each dependency should be confirmed against the corresponding source files. The presence of a package in `requirements.txt` does not, by itself, establish which application features use it.

---

## 📁 Project Structure

The repository contains backend agent modules, API components, a frontend application, Docker configuration, and supporting documentation.

The following is a representative view of the visible project organization; it is not an exhaustive inventory of every file.

```text
courtgpt-auditor/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── bias_agent.py
│   │   │   ├── citation_agent.py
│   │   │   ├── hallucination_agent.py
│   │   │   ├── precedent_agent.py
│   │   │   ├── reasoning_agent.py
│   │   │   └── statute_agent.py
│   │   │
│   │   └── api/
│   │       └── main.py
│   │
│   └── tests/
│       └── test_audit_suite.py
│
├── frontend/
│   └── src/
│
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
│
├── data/
│
├── RESEARCH_METHODOLOGY.md
├── README.md
├── requirements.txt
└── docker-compose.yml
```

Other directories and files may exist in the actual repository. Retain the existing application structure rather than creating placeholder files solely to match this example.

---

## 💻 Prerequisites

Install the following software before starting the project:

- Python with a version compatible with the backend dependencies.
- Node.js and npm compatible with the frontend configuration.
- Git for source-code version control.
- Docker Desktop if you want to use containerized deployment.

Verify the installations in PowerShell:

```powershell
python --version
python -m pip --version
node --version
npm --version
git --version
docker --version
docker compose version
```

Docker commands are required only if you plan to use the Docker deployment option.

---

## 🚀 Installation and Setup

### Step 1: Clone the repository

After the repository has been published on GitHub, run:

```powershell
git clone https://github.com/YOUR_USERNAME/courtgpt-auditor.git
cd courtgpt-auditor
```

Replace `YOUR_USERNAME` with the GitHub account that owns the repository.

If you have already opened the project locally, you can continue from its existing root directory.

### Step 2: Create a Python virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use an approved activation method for your system or invoke the environment's Python executable directly.

### Step 3: Install backend dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The commands above assume that `requirements.txt` is located in the repository root.

### Step 4: Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

The frontend must contain its own `package.json`. If that file is missing, inspect the repository before continuing.

### Step 5: Configure environment variables

If the application requires environment variables, create a local `.env` file using the supplied `.env.example` as a reference.

For example:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with the configuration required by your actual application.

Do not commit `.env` or publish API keys, passwords, signing secrets, or other credentials. The exact required environment variables depend on the backend settings implementation.

---

## ▶️ Running the Application

Run the backend and frontend in separate VS Code terminals.

### Terminal 1: Start the backend

From the repository root:

```powershell
$env:PYTHONPATH = (Get-Location).Path

python -m uvicorn backend.app.api.main:app --reload --port 8000
```

If startup succeeds, the backend API should be accessible at:

- API base: `http://localhost:8000`
- Interactive API documentation: `http://localhost:8000/docs`

The availability of particular API endpoints depends on the routes implemented in the application.

### Terminal 2: Start the frontend

From the repository root:

```powershell
cd frontend
npm run dev
```

Open the local URL printed by Vite in the terminal. The configured development URL in the project's Quickstart is:

`http://localhost:5173`

If the frontend cannot communicate with the backend, check the API base URL and cross-origin settings in the actual frontend and backend configuration.

---

## 🔌 API Documentation

CourtGPT Auditor uses FastAPI for its backend API.

Once the backend is running, visit:

**Swagger UI:** http://localhost:8000/docs

The interactive documentation allows developers to inspect the registered routes, view request and response schemas, and try supported endpoints.

The available endpoints and their request formats should be taken from the running application's API documentation rather than assumed from the project description.

---

## 🧪 Running Automated Tests

The supplied Quickstart specifies a pytest test suite for the audit functionality.

From the repository root, run:

```powershell
$env:PYTHONPATH = (Get-Location).Path

python -m pytest backend/tests/test_audit_suite.py -v
```

The `-v` flag displays individual test results.

Use the test output to determine which checks passed, failed, or were skipped. A successful test run supports the correctness of the tested behavior; it does not establish that every legal observation produced by the system is correct.

---

## 🐳 Docker Deployment

The supplied Docker Compose configuration defines two services:

- **Backend:** Built using `docker/Dockerfile.backend` and exposed on port `8000`.
- **Frontend:** Built using `docker/Dockerfile.frontend` and exposed on port `5173`.

The configuration specifies a SQLite database URL and enables the in-memory knowledge-graph setting through environment variables.

### Start the services

From the repository root:

```powershell
docker compose up --build
```

To run the services in the background:

```powershell
docker compose up --build -d
```

To inspect running services:

```powershell
docker compose ps
```

To view logs:

```powershell
docker compose logs -f
```

To stop the services:

```powershell
docker compose down
```

### Docker configuration notes

The Dockerfiles and application configuration must be present and consistent with the Compose file. Confirm that the backend binds to the appropriate interface within its container and that the frontend can reach the backend using the configured network address.

The Compose configuration mounts `./data` into `/app/data` for the backend. Verify the actual database path and persistence requirements before relying on that mount for durable storage.

---

## 🛡️ Research Integrity and Verification

Legal technology requires particular care because plausible but incorrect outputs can be misleading.

CourtGPT Auditor's research protocol establishes the following principles.

### Evidence-backed reporting

Potential issues should be accompanied by relevant statutory text or reporter citations wherever sufficient evidence is available.

### Explicit uncertainty

The system should distinguish an unverified observation from a confirmed finding. The `UNVERIFIED` status is intended to avoid presenting a lack of evidence as proof of correctness or error.

### Counter-evidence

Relevant counter-evidence should be considered when evaluating a flagged issue.

### Non-adjudicative operation

The framework is intended to support quality assurance and legal-consistency research. Its outputs are not final legal determinations.

### Jurisdictional awareness

Legal references must be interpreted in the context of the relevant jurisdiction, applicable legislation, procedural framework, and precedential authority.

The research methodology identifies the following areas for Indian legal mapping:

- Constitutional Articles 14, 19, and 21, including the *Maneka Gandhi* and *Puttaswamy* doctrines.
- The Indian Penal Code and Bharatiya Nyaya Sanhita.
- The Code of Criminal Procedure and Bharatiya Nagarik Suraksha Sanhita.
- Anticipatory bail under Section 438 CrPC, including *Gurbaksh Singh Sibbia* and *Sushila Aggarwal*.
- Arrest-related provisions under Sections 41 and 41A CrPC, including *Arnesh Kumar*.
- The Supreme Court of India's *Handbook on Combating Gender Stereotypes* (2023).

These references describe the research scope, not an assertion that every provision, judgment, or doctrine has already been comprehensively implemented or independently validated.

---

## ⚠️ Limitations

1. **Not a substitute for legal advice:** The system is intended to support research and review rather than provide definitive legal conclusions.
2. **Source coverage:** Verification depends on the availability, quality, and completeness of the underlying legal sources and indexes.
3. **Potential AI errors:** Automated agents may produce incorrect, incomplete, or misleading observations.
4. **Contextual interpretation:** Legal reasoning and linguistic analysis can depend on context that automated methods may not fully capture.
5. **Unverified information:** A missing citation or unavailable source does not, by itself, establish that a legal claim is incorrect.
6. **Evaluation requirements:** Claims about accuracy, precision, reliability, or superiority over alternative systems require empirical validation.
7. **Jurisdictional scope:** The research protocol targets Indian jurisprudence. Other jurisdictions require their own legal sources, rules, and evaluation procedures.

---

## 🔮 Future Scope

Potential research and development directions include:

- Expanding the coverage of authoritative legal sources and judgments.
- Improving retrieval and cross-referencing of precedents.
- Developing standardized evaluation datasets for legal-auditing tasks.
- Comparing single-model and multi-agent approaches using consistent benchmarks.
- Measuring precision, recall, false-positive rates, and evidence-grounding quality.
- Improving explainability and traceability between claims and supporting sources.
- Evaluating disagreement resolution between specialized agents.
- Strengthening uncertainty estimation and counter-evidence handling.
- Improving usability for legal researchers and academic evaluators.
- Evaluating robustness across document formats and legal writing styles.

These are prospective directions and should not be interpreted as features already implemented.

---

## 🤝 Contributing

Contributions that improve code quality, reproducibility, testing, documentation, and research transparency are welcome.

A suggested contribution workflow is:

1. Fork the repository.
2. Create a separate branch for your changes.
3. Implement and test the change.
4. Document new dependencies, configuration, and behavior.
5. Submit a pull request describing the change and its validation.

Example:

```bash
git checkout -b feature/your-feature
git add .
git commit -m "Describe your changes"
git push origin feature/your-feature
```

Please avoid including confidential case material, private user information, credentials, or unlicensed datasets in contributions.

---

## 📄 License

Choose and add an appropriate open-source license before distributing the project publicly. Until a license is included, do not assume that other users have permission to reuse, modify, or redistribute the repository's contents.

---

## ⚖️ Disclaimer

CourtGPT Auditor is an experimental, research-oriented legal technology framework. Its outputs may be incomplete, inaccurate, or dependent on the sources available to it.

Any flagged issue should be independently reviewed against authoritative legal materials by a qualified person. The system does not determine the legal validity of judicial judgments, establish judicial misconduct, or replace professional legal judgment.

**The purpose of the project is to support transparent legal research and structured quality assurance, not to automate judicial decision-making.**
