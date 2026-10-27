from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    RESEARCHER = "RESEARCHER"
    USER = "USER"

class FindingSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class FindingStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    FABRICATED = "FABRICATED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    OUTDATED = "OUTDATED"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"
    AGENT_DISAGREEMENT = "AGENT_DISAGREEMENT"

class AuditStatus(str, Enum):
    PENDING = "PENDING"
    PARSING = "PARSING"
    RUNNING_AGENTS = "RUNNING_AGENTS"
    CROSS_VALIDATING = "CROSS_VALIDATING"
    GENERATING_REPORT = "GENERATING_REPORT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    judgments = relationship("Judgment", back_populates="owner")
    audit_runs = relationship("AuditRun", back_populates="owner")

class Judgment(Base):
    __tablename__ = "judgments"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    filename = Column(String(500), nullable=True)
    file_path = Column(String(1000), nullable=True)
    file_hash = Column(String(64), nullable=True)
    file_size = Column(Integer, default=0)
    page_count = Column(Integer, default=1)
    is_scanned = Column(Boolean, default=False)
    
    court_name = Column(String(255), default="Supreme Court of India")
    judgment_date = Column(String(50), nullable=True)
    case_number = Column(String(255), nullable=True)
    bench = Column(String(500), nullable=True)
    case_type = Column(String(100), default="Judicial Judgment")
    
    raw_text = Column(Text, nullable=False)
    case_info = Column(JSON, nullable=True)
    parsed_structure = Column(JSON, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="judgments")
    audit_runs = relationship("AuditRun", back_populates="judgment", cascade="all, delete-orphan")

class AuditRun(Base):
    __tablename__ = "audit_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    judgment_id = Column(Integer, ForeignKey("judgments.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(AuditStatus), default=AuditStatus.PENDING, nullable=False)
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String(255), default="Initialized")
    
    citation_accuracy = Column(Float, default=1.0)
    reasoning_consistency = Column(Float, default=1.0)
    grounding_score = Column(Float, default=1.0)
    precedent_coverage = Column(Float, default=1.0)
    bias_indicator_count = Column(Integer, default=0)
    
    summary_metrics = Column(JSON, nullable=True)
    executive_summary = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    human_verification_checklist = Column(JSON, nullable=True)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    judgment = relationship("Judgment", back_populates="audit_runs")
    owner = relationship("User", back_populates="audit_runs")
    findings = relationship("Finding", back_populates="audit_run", cascade="all, delete-orphan")
    agent_logs = relationship("AgentExecutionLog", back_populates="audit_run", cascade="all, delete-orphan")

class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_run_id = Column(Integer, ForeignKey("audit_runs.id"), nullable=False)
    finding_code = Column(String(50), nullable=False)
    agent_name = Column(String(100), nullable=False)
    issue_type = Column(String(100), nullable=False)
    severity = Column(SQLEnum(FindingSeverity), nullable=False)
    status = Column(SQLEnum(FindingStatus), default=FindingStatus.UNVERIFIED, nullable=False)
    
    paragraph_index = Column(Integer, nullable=True)
    page_number = Column(Integer, default=1)
    quoted_text = Column(Text, nullable=True)
    claim = Column(Text, nullable=False)
    reasoning_explanation = Column(Text, nullable=False)
    evidence_text = Column(Text, nullable=True)
    source_reference = Column(String(500), nullable=True)
    confidence = Column(Float, default=0.5)
    counter_evidence = Column(Text, nullable=True)
    human_action_required = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    audit_run = relationship("AuditRun", back_populates="findings")

class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_run_id = Column(Integer, ForeignKey("audit_runs.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    duration_ms = Column(Integer, default=0)
    findings_generated = Column(Integer, default=0)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    audit_run = relationship("AuditRun", back_populates="agent_logs")

class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    configuration = Column(JSON, nullable=False)
    metrics = Column(JSON, nullable=False)
    ablation_flags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

