import os
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.app.config.settings import settings
from backend.app.database.session import init_db, get_db
from backend.app.database.models import User, Judgment, AuditRun, Finding, AgentExecutionLog, UserRole, FindingSeverity, FindingStatus, AuditStatus
from backend.app.security.auth import verify_password, get_password_hash, create_access_token
from backend.app.audit.orchestrator import global_orchestrator
from backend.app.ingestion.document_parser import DocumentIngestionService, LegalSegmenter
from backend.app.rag.retriever import global_retriever
from backend.app.knowledge_graph.graph_engine import global_legal_kg
from backend.app.evaluation.benchmark import BenchmarkEvaluationEngine, TrainableClassifierManager

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Explainable Multi-Agent AI Framework for Auditing Judicial Judgments (India Jurisdiction)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    db = next(get_db())
    admin_user = db.query(User).filter(User.email == "auditor@courtgpt.org").first()
    if not admin_user:
        admin_user = User(
            email="auditor@courtgpt.org",
            hashed_password=get_password_hash("courtgpt2026!"),
            full_name="Lead Legal Research Auditor",
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        db.commit()
    db.close()

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "agents_ready": 7,
        "knowledge_corpus_chunks": len(global_retriever.corpus),
        "knowledge_graph_nodes": len(global_legal_kg.nodes)
    }

@app.post("/api/judgments/upload")
async def upload_judgment(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    is_demo: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Real file ingestion endpoint supporting PDF, DOCX, TXT with validation,
    encryption check, OCR fallback, and automatic case entity extraction.
    """
    extracted_text = ""
    filename = "document.txt"
    file_size = 0
    file_hash = None
    page_count = 1
    is_scanned = False

    if file:
        filename = file.filename
        try:
            content = await file.read()
            validated = DocumentIngestionService.validate_and_extract(content, filename)
            extracted_text = validated["extracted_text"]
            file_size = validated["file_size"]
            file_hash = validated["file_hash"]
            page_count = validated["page_count"]
            is_scanned = validated["is_scanned"]
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected document extraction failure: {str(e)}")
    elif raw_text:
        extracted_text = raw_text.strip()
        file_size = len(extracted_text.encode('utf-8'))
        filename = "pasted_judgment.txt"
    else:
        raise HTTPException(status_code=400, detail="No judgment file or text provided for upload.")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Document contains no readable text.")

    # Structure & Extract Case Information
    segmented = LegalSegmenter.segment_judgment(extracted_text)
    case_info = segmented.get("case_info", {})
    judgment_title = title or case_info.get("case_title") or filename

    user = db.query(User).first()
    judgment = Judgment(
        title=judgment_title,
        filename=filename,
        file_hash=file_hash,
        file_size=file_size,
        page_count=page_count,
        is_scanned=is_scanned,
        court_name=case_info.get("court", "Supreme Court of India"),
        judgment_date=case_info.get("judgment_date", "Unspecified"),
        case_number=case_info.get("case_number", "Unspecified"),
        bench=case_info.get("bench", "Division Bench"),
        raw_text=extracted_text,
        case_info=case_info,
        parsed_structure=segmented,
        owner_id=user.id if user else 1,
        is_demo=is_demo
    )
    db.add(judgment)
    db.commit()
    db.refresh(judgment)

    return {
        "judgment_id": judgment.id,
        "title": judgment.title,
        "filename": judgment.filename,
        "file_size": judgment.file_size,
        "page_count": judgment.page_count,
        "is_scanned": judgment.is_scanned,
        "court_name": judgment.court_name,
        "case_number": judgment.case_number,
        "case_info": judgment.case_info,
        "extracted_preview": extracted_text[:400] + "..."
    }

@app.get("/api/judgments/{id}")
def get_judgment(id: int, db: Session = Depends(get_db)):
    j = db.query(Judgment).filter(Judgment.id == id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Judgment not found")
    return {
        "id": j.id,
        "title": j.title,
        "filename": j.filename,
        "court_name": j.court_name,
        "case_number": j.case_number,
        "judgment_date": j.judgment_date,
        "bench": j.bench,
        "page_count": j.page_count,
        "is_scanned": j.is_scanned,
        "case_info": j.case_info,
        "parsed_structure": j.parsed_structure,
        "raw_text": j.raw_text,
        "created_at": j.created_at
    }

@app.post("/api/audits")
def trigger_audit(judgment_id: int, db: Session = Depends(get_db)):
    judgment = db.query(Judgment).filter(Judgment.id == judgment_id).first()
    if not judgment:
        raise HTTPException(status_code=404, detail="Judgment not found")

    audit_run = AuditRun(
        judgment_id=judgment.id,
        owner_id=judgment.owner_id,
        status=AuditStatus.RUNNING_AGENTS,
        current_step="Executing 7 Specialized Legal Agents..."
    )
    db.add(audit_run)
    db.commit()
    db.refresh(audit_run)

    # Run Multi-Agent Swarm Orchestrator on actual judgment text
    audit_result = global_orchestrator.run_audit(judgment.raw_text)

    # Save Results
    judgment.parsed_structure = audit_result["parsed_structure"]
    if audit_result.get("case_info"):
        judgment.case_info = audit_result["case_info"]

    audit_run.status = AuditStatus.COMPLETED
    audit_run.progress_percentage = 100
    audit_run.current_step = "Completed"
    audit_run.citation_accuracy = audit_result["metrics"]["citation_accuracy"]
    audit_run.reasoning_consistency = audit_result["metrics"]["reasoning_consistency"]
    audit_run.grounding_score = audit_result["metrics"]["grounding_score"]
    audit_run.precedent_coverage = audit_result["metrics"]["precedent_coverage"]
    audit_run.bias_indicator_count = audit_result["metrics"]["bias_indicator_count"]
    audit_run.summary_metrics = audit_result["metrics"]
    audit_run.executive_summary = audit_result["executive_summary"]
    audit_run.limitations = audit_result["limitations"]
    audit_run.human_verification_checklist = audit_result["checklist"]
    audit_run.completed_at = datetime.utcnow()

    # Save Individual Findings
    for f in audit_result["findings"]:
        finding_obj = Finding(
            audit_run_id=audit_run.id,
            finding_code=f["finding_code"],
            agent_name=f["agent_name"],
            issue_type=f["issue_type"],
            severity=FindingSeverity(f["severity"]),
            status=FindingStatus(f["status"]),
            paragraph_index=f.get("paragraph_index"),
            page_number=f.get("page_number", 1),
            quoted_text=f.get("quoted_text"),
            claim=f["claim"],
            reasoning_explanation=f["reasoning_explanation"],
            evidence_text=f.get("evidence_text"),
            source_reference=f.get("source_reference"),
            confidence=f.get("confidence", 0.5),
            counter_evidence=f.get("counter_evidence"),
            human_action_required=f.get("human_action_required", True)
        )
        db.add(finding_obj)

    # Save Agent Execution Logs
    for l in audit_result["logs"]:
        log_obj = AgentExecutionLog(
            audit_run_id=audit_run.id,
            agent_name=l["agent_name"],
            status=l["status"],
            duration_ms=l["duration_ms"],
            findings_generated=l["findings_generated"]
        )
        db.add(log_obj)

    db.commit()
    db.refresh(audit_run)

    return {
        "audit_run_id": audit_run.id,
        "status": audit_run.status,
        "total_findings": len(audit_result["findings"]),
        "metrics": audit_result["metrics"]
    }

@app.get("/api/audits/{id}")
def get_audit(id: int, db: Session = Depends(get_db)):
    audit = db.query(AuditRun).filter(AuditRun.id == id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    findings = db.query(Finding).filter(Finding.audit_run_id == id).all()
    logs = db.query(AgentExecutionLog).filter(AgentExecutionLog.audit_run_id == id).all()
    judgment = db.query(Judgment).filter(Judgment.id == audit.judgment_id).first()

    return {
        "id": audit.id,
        "judgment_id": audit.judgment_id,
        "judgment": {
            "title": judgment.title if judgment else "",
            "court_name": judgment.court_name if judgment else "",
            "case_number": judgment.case_number if judgment else "",
            "case_info": judgment.case_info if judgment else {},
            "page_count": judgment.page_count if judgment else 1,
            "filename": judgment.filename if judgment else ""
        },
        "status": audit.status,
        "metrics": audit.summary_metrics,
        "executive_summary": audit.executive_summary,
        "limitations": audit.limitations,
        "human_verification_checklist": audit.human_verification_checklist,
        "findings": [
            {
                "id": f.id,
                "finding_code": f.finding_code,
                "agent_name": f.agent_name,
                "issue_type": f.issue_type,
                "severity": f.severity,
                "status": f.status,
                "paragraph_index": f.paragraph_index,
                "page_number": f.page_number,
                "quoted_text": f.quoted_text,
                "claim": f.claim,
                "reasoning_explanation": f.reasoning_explanation,
                "evidence_text": f.evidence_text,
                "source_reference": f.source_reference,
                "confidence": f.confidence,
                "counter_evidence": f.counter_evidence,
                "human_action_required": f.human_action_required
            }
            for f in findings
        ],
        "logs": [
            {
                "agent_name": l.agent_name,
                "duration_ms": l.duration_ms,
                "findings_generated": l.findings_generated,
                "status": l.status
            }
            for l in logs
        ]
    }

@app.get("/api/audits/{id}/report")
def generate_audit_report(id: int, format: str = "html", db: Session = Depends(get_db)):
    """Generates downloadable, fully traceable HTML/PDF audit report."""
    audit = db.query(AuditRun).filter(AuditRun.id == id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    judgment = db.query(Judgment).filter(Judgment.id == audit.judgment_id).first()
    findings = db.query(Finding).filter(Finding.audit_run_id == id).all()

    findings_html = "".join([
        f"""
        <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 12px; background: #fafafa;">
            <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:bold; color:#475569;">
                <span>{f.finding_code} · {f.issue_type}</span>
                <span style="color: {'#e11d48' if f.severity.value == 'CRITICAL' else '#d97706'};">{f.severity.value}</span>
            </div>
            <div style="margin-top:6px; font-size:14px; font-weight:600; color:#0f172a;">{f.claim}</div>
            <div style="font-size:12px; color:#64748b; margin-top:4px;">Location: Page {f.page_number}, Paragraph {f.paragraph_index or 'N/A'}</div>
            {f'<div style="background:#f1f5f9; padding:8px; border-radius:4px; font-family:monospace; font-size:12px; margin-top:6px;">Quoted: {f.quoted_text}</div>' if f.quoted_text else ''}
            <div style="margin-top:8px; font-size:13px; color:#334155;"><strong>Reasoning:</strong> {f.reasoning_explanation}</div>
            {f'<div style="margin-top:6px; font-size:12px; color:#2563eb;"><strong>Authoritative Evidence:</strong> {f.evidence_text} ({f.source_reference})</div>' if f.evidence_text else ''}
        </div>
        """
        for f in findings
    ])

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>CourtGPT Auditor Report - {judgment.title if judgment else 'Audit'}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #0f172a; margin: 40px auto; max-width: 850px; }}
            h1 {{ font-size: 24px; border-bottom: 2px solid #0f172a; padding-bottom: 8px; }}
            .notice {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 12px; border-radius: 6px; font-size: 12px; color: #92400e; margin-bottom: 24px; }}
            .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }}
            .card {{ border: 1px solid #e2e8f0; padding: 12px; border-radius: 6px; text-align: center; }}
            .card .val {{ font-size: 20px; font-weight: bold; color: #0f172a; }}
            .card .lbl {{ font-size: 11px; color: #64748b; text-transform: uppercase; }}
        </style>
    </head>
    <body>
        <div class="notice">
            <strong>RESEARCH & QUALITY ASSURANCE DISCLAIMER:</strong> CourtGPT Auditor is an AI-assisted legal research and quality-assurance tool. It does NOT provide legal advice, determine legal correctness, establish judicial misconduct or bias, or replace qualified legal professionals. Findings must be independently verified against authoritative legal sources.
        </div>
        <h1>COURTGPT AUDITOR — JUDICIAL JUDGMENT AUDIT REPORT</h1>
        <p><strong>Case:</strong> {judgment.title if judgment else 'N/A'}<br>
        <strong>Court:</strong> {judgment.court_name if judgment else 'Supreme Court of India'}<br>
        <strong>Case Number:</strong> {judgment.case_number if judgment else 'N/A'}<br>
        <strong>Date Audited:</strong> {datetime.utcnow().strftime('%d %B %Y')}</p>

        <div class="grid">
            <div class="card"><div class="val">{len(findings)}</div><div class="lbl">Total Findings</div></div>
            <div class="card"><div class="val">{audit.summary_metrics.get('critical_findings', 0) if audit.summary_metrics else 0}</div><div class="lbl">Critical Findings</div></div>
            <div class="card"><div class="val">{int((audit.citation_accuracy or 1.0)*100)}%</div><div class="lbl">Citation Accuracy</div></div>
            <div class="card"><div class="val">{int((audit.reasoning_consistency or 1.0)*100)}%</div><div class="lbl">Reasoning Consistency</div></div>
        </div>

        <h2>Executive Summary</h2>
        <p>{audit.executive_summary or 'No executive summary generated.'}</p>

        <h2>Detailed Issue-by-Issue Audit Findings</h2>
        {findings_html}

        <h2>Limitations</h2>
        <p>{audit.limitations or 'None noted.'}</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/audits/recent")
def get_recent_audits(db: Session = Depends(get_db)):
    audits = db.query(AuditRun).order_by(AuditRun.started_at.desc()).limit(10).all()
    results = []
    for a in audits:
        j = db.query(Judgment).filter(Judgment.id == a.judgment_id).first()
        results.append({
            "audit_id": a.id,
            "judgment_id": a.judgment_id,
            "title": j.title if j else f"Audit #{a.id}",
            "court": j.court_name if j else "Supreme Court of India",
            "date": a.started_at.strftime("%d %b %Y"),
            "critical_findings": a.summary_metrics.get("critical_findings", 0) if a.summary_metrics else 0,
            "status": a.status
        })
    return results

@app.get("/api/evaluation/benchmark")
def get_benchmark_results():
    return BenchmarkEvaluationEngine.run_benchmark_suite()

@app.get("/api/evaluation/models")
def get_models():
    return TrainableClassifierManager.get_model_registry()

@app.post("/api/search")
def search_knowledge_base(query: str, top_k: int = 5):
    results = global_retriever.search(query=query, top_k=top_k)
    return {"query": query, "results": results}
