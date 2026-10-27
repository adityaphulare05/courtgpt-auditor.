import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldCheck, AlertTriangle, FileText, CheckCircle2, Search, 
  BarChart3, RefreshCw, Download, Scale, FileUp, Info
} from 'lucide-react';

interface Finding {
  id: number;
  finding_code: string;
  agent_name: string;
  issue_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  status: string;
  paragraph_index: number | null;
  page_number: number;
  quoted_text: string | null;
  claim: string;
  reasoning_explanation: string;
  evidence_text: string | null;
  source_reference: string | null;
  confidence: number;
  counter_evidence: string | null;
  human_action_required: boolean;
}

interface CaseInfo {
  court?: string;
  case_title?: string;
  case_number?: string;
  judgment_date?: string;
  bench?: string;
  statutes_mentioned?: string[];
}

interface BenchmarkItem {
  system: string;
  citation_accuracy: number;
  hallucination_f1: number;
  reasoning_consistency_acc: number;
  precedent_mrr: number;
  explainability_grounded_rate: number;
  latency_sec: number;
}

const DEMO_JUDGMENT = `IN THE SUPREME COURT OF INDIA
CRIMINAL APPELLATE JURISDICTION
CRIMINAL APPEAL NO. 450 OF 2024

Rajesh Kumar  ... Appellant
v.
State of NCT of Delhi ... Respondent

JUDGMENT
Decided on: 12th February 2024

1. This appeal arises out of the conviction under Section 304B and Section 999 IPC by the trial court.

2. The marriage between the appellant and the deceased took place twelve years prior to the alleged incident. Learned counsel argued that Section 304B strictly requires the incident to occur within seven years.

3. We place reliance on the landmark judgment of this Court in ADM Jabalpur v. Shivkant Shukla, (1976) 2 SCC 521, to hold that fundamental liberties can be suspended at executive discretion. Furthermore, we cite with approval the principle in State v. Unknown (2024) 999 SCC 0000.

4. In our considered opinion, the prosecution failed to prove the charges beyond reasonable doubt and material witnesses turned hostile.

5. Furthermore, comments on the victim having loose morals were recorded during trial.

6. In conclusion, having considered the entire record, the conviction is upheld and the appeal is dismissed.`;

const AGENT_LIST = [
  { id: 'DOC', name: 'Document Analysis Agent', desc: 'Parses structure, IRAC & metadata' },
  { id: 'CIT', name: 'Citation Agent', desc: 'Verifies reporters & overruling' },
  { id: 'PREC', name: 'Precedent Agent', desc: 'Identifies binding SC precedents' },
  { id: 'REAS', name: 'Reasoning Agent', desc: 'Checks logical contradictions' },
  { id: 'STAT', name: 'Statute Agent', desc: 'Audits statutory ingredients' },
  { id: 'BIAS', name: 'Bias Detection Agent', desc: 'SC Gender Handbook linguistic audit' },
  { id: 'HALL', name: 'Hallucination Agent', desc: 'Detects fabricated law & quotes' },
  { id: 'EXP', name: 'Explainability & QC', desc: 'Cross-agent synthesis & provenance' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<'audit' | 'benchmarks'>('audit');
  const [isDemoMode, setIsDemoMode] = useState(false);
  
  const [uploadProgress, setUploadProgress] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  
  const [judgmentId, setJudgmentId] = useState<number | null>(null);
  const [judgmentText, setJudgmentText] = useState<string>('');
  const [caseInfo, setCaseInfo] = useState<CaseInfo | null>(null);
  const [fileDetails, setFileDetails] = useState<{ name: string; size: number; pages: number } | null>(null);

  const [isAuditing, setIsAuditing] = useState(false);
  const [activeAgentIndex, setActiveAgentIndex] = useState<number>(-1);
  const [auditRunId, setAuditRunId] = useState<number | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [recentAudits, setRecentAudits] = useState<any[]>([]);

  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [filterAgent, setFilterAgent] = useState<string>('ALL');
  const [benchmarks, setBenchmarks] = useState<BenchmarkItem[]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetch('/api/evaluation/benchmark')
      .then(r => r.json())
      .then(d => { if (d?.comparison_table) setBenchmarks(d.comparison_table); })
      .catch(() => {});
    fetchRecentAudits();
  }, []);

  const fetchRecentAudits = () => {
    fetch('/api/audits/recent')
      .then(r => r.json())
      .then(d => { if (Array.isArray(d)) setRecentAudits(d); })
      .catch(() => {});
  };

  const handleFileUpload = async (uploadedFile: File) => {
    setUploadError(null);
    setIsUploading(true);
    setUploadProgress('Extracting & validating legal document...');
    setIsDemoMode(false);

    try {
      const form = new FormData();
      form.append('file', uploadedFile);

      const res = await fetch('/api/judgments/upload', { method: 'POST', body: form });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Upload failed');
      }

      const data = await res.json();
      setJudgmentId(data.judgment_id);
      setCaseInfo(data.case_info || {});
      setFileDetails({
        name: data.filename,
        size: data.file_size,
        pages: data.page_count
      });

      const jRes = await fetch(`/api/judgments/${data.judgment_id}`);
      const jData = await jRes.json();
      setJudgmentText(jData.raw_text);

      setFindings([]);
      setMetrics(null);
      setSelectedFinding(null);
      setAuditRunId(null);
      setUploadProgress('Document ready for multi-agent audit.');
    } catch (err: any) {
      setUploadError(err.message || 'File upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleLoadDemo = async () => {
    setIsDemoMode(true);
    setUploadError(null);
    setIsUploading(true);
    setUploadProgress('Loading Supreme Court demo judgment...');

    try {
      const form = new FormData();
      form.append('title', 'Rajesh Kumar v. State of NCT of Delhi');
      form.append('raw_text', DEMO_JUDGMENT);
      form.append('court_name', 'Supreme Court of India');
      form.append('is_demo', 'true');

      const res = await fetch('/api/judgments/upload', { method: 'POST', body: form });
      const data = await res.json();
      setJudgmentId(data.judgment_id);
      setJudgmentText(DEMO_JUDGMENT);
      setCaseInfo(data.case_info || {
        court: 'Supreme Court of India',
        case_title: 'Rajesh Kumar v. State of NCT of Delhi',
        case_number: 'Criminal Appeal No. 450 of 2024',
        judgment_date: '12th February 2024'
      });
      setFileDetails({
        name: 'Demo_Adversarial_Judgment_2024.txt',
        size: DEMO_JUDGMENT.length,
        pages: 1
      });
      setFindings([]);
      setMetrics(null);
      setSelectedFinding(null);
    } catch (e: any) {
      setUploadError(e.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRunAudit = async () => {
    if (!judgmentId) {
      alert('Please upload a judgment file or load the demo first.');
      return;
    }

    setIsAuditing(true);
    setActiveAgentIndex(0);

    const interval = setInterval(() => {
      setActiveAgentIndex(prev => (prev < AGENT_LIST.length - 1 ? prev + 1 : prev));
    }, 450);

    try {
      const res = await fetch(`/api/audits?judgment_id=${judgmentId}`, { method: 'POST' });
      if (!res.ok) throw new Error('Audit execution encountered an error.');

      const audData = await res.json();
      setAuditRunId(audData.audit_run_id);

      const fullRes = await fetch(`/api/audits/${audData.audit_run_id}`);
      const fullAudit = await fullRes.json();

      setFindings(fullAudit.findings || []);
      setMetrics(fullAudit.metrics);
      if (fullAudit.findings?.length > 0) {
        setSelectedFinding(fullAudit.findings[0]);
      }
      fetchRecentAudits();
    } catch (err: any) {
      alert('Audit error: ' + err.message);
    } finally {
      clearInterval(interval);
      setActiveAgentIndex(AGENT_LIST.length);
      setIsAuditing(false);
    }
  };

  const filteredFindings = findings.filter(f => {
    const matchesSev = filterSeverity === 'ALL' || f.severity === filterSeverity;
    const matchesAg = filterAgent === 'ALL' || f.agent_name.toLowerCase().includes(filterAgent.toLowerCase());
    return matchesSev && matchesAg;
  });

  return (
    <div className="min-h-screen bg-white text-slate-900 flex font-sans antialiased selection:bg-slate-200">
      
      {/* Clean Left Sidebar */}
      <aside className="w-64 border-r border-slate-200 bg-slate-50 flex flex-col justify-between shrink-0">
        <div className="p-4 space-y-4">
          <div className="flex items-center space-x-2.5 px-2">
            <div className="w-7 h-7 bg-black text-white rounded-md flex items-center justify-center font-bold text-xs tracking-wider">
              CG
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-900 leading-tight">CourtGPT Auditor</div>
              <div className="text-[11px] text-slate-500">Legal Consistency Swarm</div>
            </div>
          </div>

          <button
            onClick={() => {
              setJudgmentId(null);
              setJudgmentText('');
              setFindings([]);
              setMetrics(null);
              setSelectedFinding(null);
              setCaseInfo(null);
              setFileDetails(null);
            }}
            className="w-full flex items-center justify-center space-x-2 py-2 px-3 border border-slate-300 rounded-lg bg-white hover:bg-slate-100 text-xs font-semibold text-slate-800 shadow-sm transition"
          >
            <span>+ New Audit</span>
          </button>

          <nav className="space-y-1 text-xs font-medium text-slate-600">
            <button
              onClick={() => setActiveTab('audit')}
              className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg transition ${activeTab === 'audit' ? 'bg-slate-200/80 text-black font-semibold' : 'hover:bg-slate-100'}`}
            >
              <Scale className="w-4 h-4 text-slate-700" />
              <span>Audit Workspace</span>
            </button>
            <button
              onClick={() => setActiveTab('benchmarks')}
              className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg transition ${activeTab === 'benchmarks' ? 'bg-slate-200/80 text-black font-semibold' : 'hover:bg-slate-100'}`}
            >
              <BarChart3 className="w-4 h-4 text-slate-700" />
              <span>Empirical Benchmarks</span>
            </button>
          </nav>

          <div className="pt-3 border-t border-slate-200">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3 mb-2">Recent Audits</div>
            <div className="space-y-1 max-h-56 overflow-y-auto">
              {recentAudits.length === 0 ? (
                <div className="text-[11px] text-slate-400 px-3">No recent audits yet</div>
              ) : (
                recentAudits.map((a, i) => (
                  <button
                    key={i}
                    onClick={async () => {
                      const res = await fetch(`/api/audits/${a.audit_id}`);
                      const d = await res.json();
                      setAuditRunId(d.id);
                      setFindings(d.findings || []);
                      setMetrics(d.metrics);
                      setJudgmentId(d.judgment_id);
                      const jres = await fetch(`/api/judgments/${d.judgment_id}`);
                      const jd = await jres.json();
                      setJudgmentText(jd.raw_text);
                      setCaseInfo(jd.case_info || {});
                      setFileDetails({
                        name: jd.filename || 'Judgment.txt',
                        size: jd.raw_text.length,
                        pages: jd.page_count
                      });
                      if (d.findings?.length > 0) setSelectedFinding(d.findings[0]);
                      setActiveTab('audit');
                    }}
                    className="w-full text-left px-3 py-1.5 rounded text-xs text-slate-700 hover:bg-slate-200/60 truncate flex items-center justify-between"
                  >
                    <span className="truncate">{a.title}</span>
                    {a.critical_findings > 0 && <span className="w-2 h-2 rounded-full bg-rose-500 shrink-0 ml-1"></span>}
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-slate-200 bg-white space-y-2">
          <div className="text-[10px] text-slate-500 leading-tight">
            Target Jurisdiction: <strong>India</strong><br/>
            SC, High Courts, IPC, CrPC, BNS, BNSS
          </div>
          <button
            onClick={handleLoadDemo}
            className="w-full py-1.5 px-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded text-[11px] font-medium border border-slate-300 transition"
          >
            ⚡ Try Demo Mode (Stress Test)
          </button>
        </div>
      </aside>

      {/* Main Panel */}
      <div className="flex-1 flex flex-col overflow-hidden bg-white">
        
        {/* Research Disclaimer */}
        <div className="bg-amber-50 border-b border-amber-200 px-6 py-2 text-xs text-amber-900 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Info className="w-4 h-4 text-amber-700 shrink-0" />
            <span>
              <strong>RESEARCH & QUALITY-ASSURANCE DISCLAIMER:</strong> CourtGPT Auditor is an AI-assisted legal research tool. It does NOT provide legal advice, determine legal correctness, establish judicial misconduct or bias, or replace qualified advocates.
            </span>
          </div>
          <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-amber-200/70 text-amber-950">
            India Jurisdiction
          </span>
        </div>

        {activeTab === 'audit' ? (
          <div className="flex-1 flex flex-col overflow-hidden">
            
            {/* Header / Case Info */}
            <header className="border-b border-slate-200 px-6 py-3 flex items-center justify-between bg-white shrink-0">
              <div>
                <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  {caseInfo?.case_title || (fileDetails ? fileDetails.name : 'Upload Judgment to Begin')}
                  {isDemoMode && (
                    <span className="text-[10px] font-medium bg-amber-100 text-amber-800 border border-amber-300 rounded px-1.5 py-0.5">
                      DEMO MODE
                    </span>
                  )}
                </h2>
                <div className="text-xs text-slate-500 flex items-center space-x-3 mt-0.5">
                  <span>Court: <strong>{caseInfo?.court || 'Supreme Court of India'}</strong></span>
                  {caseInfo?.case_number && <span>• No: {caseInfo.case_number}</span>}
                  {caseInfo?.judgment_date && <span>• Date: {caseInfo.judgment_date}</span>}
                  {fileDetails && <span>• {fileDetails.pages} {fileDetails.pages === 1 ? 'Page' : 'Pages'}</span>}
                </div>
              </div>

              <div className="flex items-center space-x-3">
                {auditRunId && (
                  <a
                    href={`/api/audits/${auditRunId}/report`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center space-x-1.5 py-1.5 px-3 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg text-xs font-semibold text-slate-800 shadow-sm transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download Report</span>
                  </a>
                )}

                <button
                  onClick={handleRunAudit}
                  disabled={!judgmentId || isAuditing}
                  className={`flex items-center space-x-2 py-2 px-4 rounded-lg text-xs font-semibold shadow-sm transition ${
                    !judgmentId 
                      ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                      : isAuditing
                      ? 'bg-black text-white opacity-80 cursor-wait'
                      : 'bg-black text-white hover:bg-slate-800'
                  }`}
                >
                  {isAuditing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
                  <span>{isAuditing ? 'Running 7 Agents...' : 'Run Audit'}</span>
                </button>
              </div>
            </header>

            {/* Upload Zone when no judgment loaded */}
            {!judgmentId && (
              <div className="flex-1 flex flex-col items-center justify-center p-8 bg-slate-50">
                <div 
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    if (e.dataTransfer.files && e.dataTransfer.files[0]) handleFileUpload(e.dataTransfer.files[0]);
                  }}
                  className="w-full max-w-xl bg-white border-2 border-dashed border-slate-300 hover:border-slate-400 rounded-2xl p-10 flex flex-col items-center justify-center text-center shadow-sm transition"
                >
                  <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mb-4 text-slate-700">
                    <FileUp className="w-6 h-6" />
                  </div>
                  <h3 className="text-base font-bold text-slate-900">Upload Judicial Judgment</h3>
                  <p className="text-xs text-slate-500 mt-1 max-w-sm">
                    Drag and drop your judgment document directly here, or browse files from your computer.
                  </p>

                  <div className="mt-5">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.docx,.txt"
                      className="hidden"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) handleFileUpload(e.target.files[0]);
                      }}
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isUploading}
                      className="py-2 px-5 bg-black hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow transition"
                    >
                      {isUploading ? 'Validating...' : 'Browse Files'}
                    </button>
                  </div>

                  <div className="mt-4 text-[11px] text-slate-400">
                    Supported Formats: <strong>PDF</strong> (with OCR fallback), <strong>DOCX</strong>, <strong>TXT</strong> (up to 50MB)
                  </div>

                  {uploadProgress && (
                    <div className="mt-4 text-xs font-medium text-slate-700 flex items-center gap-1.5">
                      <RefreshCw className="w-3.5 h-3.5 animate-spin text-slate-900" />
                      <span>{uploadProgress}</span>
                    </div>
                  )}

                  {uploadError && (
                    <div className="mt-4 p-2.5 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 max-w-md">
                      <strong>Upload Error:</strong> {uploadError}
                    </div>
                  )}
                </div>

                <div className="mt-6 flex items-center space-x-3 text-xs text-slate-500">
                  <span>Want to test without a file?</span>
                  <button
                    onClick={handleLoadDemo}
                    className="text-black font-semibold underline hover:text-slate-700"
                  >
                    Load Synthetic Indian Supreme Court Stress-Test Case
                  </button>
                </div>
              </div>
            )}

            {/* When document is loaded */}
            {judgmentId && (
              <div className="flex-1 flex flex-col overflow-hidden">
                
                {/* Agent Execution Flow */}
                {isAuditing && (
                  <div className="bg-slate-900 text-white px-6 py-4 border-b border-slate-800">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                        Multi-Agent Audit in Progress
                      </span>
                      <span className="text-xs font-mono text-slate-300">
                        Step {Math.min(activeAgentIndex + 1, AGENT_LIST.length)} of {AGENT_LIST.length}
                      </span>
                    </div>

                    <div className="grid grid-cols-4 gap-3">
                      {AGENT_LIST.map((ag, idx) => {
                        const isDone = idx < activeAgentIndex;
                        const isCurrent = idx === activeAgentIndex;
                        return (
                          <div 
                            key={ag.id}
                            className={`p-2.5 rounded-lg border text-xs flex items-center space-x-2 ${
                              isDone ? 'bg-slate-800/80 border-slate-700 text-slate-200' :
                              isCurrent ? 'bg-black border-slate-500 text-white ring-1 ring-slate-400' :
                              'bg-slate-900 border-slate-800 text-slate-500'
                            }`}
                          >
                            {isDone ? (
                              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                            ) : isCurrent ? (
                              <RefreshCw className="w-4 h-4 animate-spin text-white shrink-0" />
                            ) : (
                              <span className="w-4 h-4 rounded-full border border-slate-700 shrink-0"></span>
                            )}
                            <div className="truncate">
                              <div className="font-semibold truncate">{ag.name}</div>
                              <div className="text-[10px] text-slate-400 truncate">{ag.desc}</div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Audit Findings Summary */}
                {metrics && (
                  <div className="bg-slate-50 border-b border-slate-200 px-6 py-3 flex items-center justify-between shrink-0">
                    <div className="flex items-center space-x-6 text-xs">
                      <div>
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Total Findings</span>
                        <span className="text-base font-bold text-slate-900">{metrics.total_findings}</span>
                      </div>
                      <div className="border-l border-slate-200 pl-4">
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Critical Issues</span>
                        <span className="text-base font-bold text-rose-600">{metrics.critical_findings}</span>
                      </div>
                      <div className="border-l border-slate-200 pl-4">
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Citation Accuracy</span>
                        <span className="text-base font-bold text-slate-900">{Math.round(metrics.citation_accuracy * 100)}%</span>
                      </div>
                      <div className="border-l border-slate-200 pl-4">
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Reasoning Consistency</span>
                        <span className="text-base font-bold text-slate-900">{Math.round(metrics.reasoning_consistency * 100)}%</span>
                      </div>
                      <div className="border-l border-slate-200 pl-4">
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Grounding Score</span>
                        <span className="text-base font-bold text-slate-900">{Math.round(metrics.grounding_score * 100)}%</span>
                      </div>
                      <div className="border-l border-slate-200 pl-4">
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Linguistic Bias Flags</span>
                        <span className="text-base font-bold text-amber-700">{metrics.bias_indicator_count}</span>
                      </div>
                    </div>

                    <button
                      onClick={() => setJudgmentId(null)}
                      className="text-xs text-slate-600 hover:text-black py-1 px-2.5 rounded border border-slate-200 bg-white"
                    >
                      Change Document
                    </button>
                  </div>
                )}

                {/* Two-Panel Split Workspace */}
                <div className="flex-1 grid grid-cols-12 overflow-hidden">
                  
                  {/* Left: Original Judgment Viewer */}
                  <div className="col-span-6 border-r border-slate-200 flex flex-col bg-white overflow-hidden">
                    <div className="px-5 py-2.5 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between text-xs text-slate-600 shrink-0">
                      <div className="flex items-center space-x-2">
                        <FileText className="w-3.5 h-3.5 text-slate-500" />
                        <span className="font-semibold text-slate-800">Original Judgment Text</span>
                      </div>
                      <span className="text-[11px] text-slate-400 font-mono">
                        {fileDetails ? `${fileDetails.name} • ${fileDetails.pages} Pages` : ''}
                      </span>
                    </div>

                    <div className="flex-1 p-6 overflow-y-auto font-serif text-[13px] leading-relaxed text-slate-800 whitespace-pre-wrap selection:bg-amber-100">
                      {judgmentText}
                    </div>
                  </div>

                  {/* Right: Audit Findings Panel */}
                  <div className="col-span-6 flex flex-col bg-slate-50/40 overflow-hidden">
                    
                    <div className="px-5 py-2.5 border-b border-slate-200 bg-white flex items-center justify-between shrink-0 text-xs">
                      <span className="font-semibold text-slate-800">
                        Audit Findings ({filteredFindings.length})
                      </span>

                      <div className="flex items-center space-x-2">
                        <select
                          value={filterSeverity}
                          onChange={e => setFilterSeverity(e.target.value)}
                          className="bg-white border border-slate-300 rounded px-2 py-1 text-slate-700 text-xs"
                        >
                          <option value="ALL">All Severities</option>
                          <option value="CRITICAL">Critical</option>
                          <option value="HIGH">High</option>
                          <option value="MEDIUM">Medium</option>
                          <option value="LOW">Low</option>
                          <option value="INFO">Info</option>
                        </select>

                        <select
                          value={filterAgent}
                          onChange={e => setFilterAgent(e.target.value)}
                          className="bg-white border border-slate-300 rounded px-2 py-1 text-slate-700 text-xs"
                        >
                          <option value="ALL">All Agents</option>
                          <option value="Citation">Citation Agent</option>
                          <option value="Precedent">Precedent Agent</option>
                          <option value="Reasoning">Reasoning Agent</option>
                          <option value="Statute">Statute Agent</option>
                          <option value="Bias">Bias Agent</option>
                          <option value="Hallucination">Hallucination Agent</option>
                        </select>
                      </div>
                    </div>

                    <div className="flex-1 grid grid-rows-2 overflow-hidden">
                      
                      {/* Findings Cards List */}
                      <div className="overflow-y-auto divide-y divide-slate-200 bg-white border-b border-slate-200">
                        {filteredFindings.length === 0 ? (
                          <div className="p-8 text-center text-slate-400 text-xs">
                            {findings.length === 0 
                              ? 'Click "Run Audit" above to analyze this judgment with all 7 specialized agents.'
                              : 'No findings matching current filter.'}
                          </div>
                        ) : (
                          filteredFindings.map((f) => (
                            <div
                              key={f.id || f.finding_code}
                              onClick={() => setSelectedFinding(f)}
                              className={`p-3.5 cursor-pointer transition flex items-start justify-between ${
                                selectedFinding?.finding_code === f.finding_code
                                  ? 'bg-slate-100 border-l-4 border-black'
                                  : 'hover:bg-slate-50'
                              }`}
                            >
                              <div className="space-y-1">
                                <div className="flex items-center space-x-2">
                                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider ${
                                    f.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-800 border border-rose-300' :
                                    f.severity === 'HIGH' ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                                    f.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800 border border-yellow-300' :
                                    'bg-slate-100 text-slate-700'
                                  }`}>
                                    {f.severity}
                                  </span>
                                  <span className="text-xs font-semibold text-slate-800">{f.issue_type}</span>
                                  <span className="text-[11px] text-slate-400 font-mono">[{f.finding_code}]</span>
                                </div>
                                <div className="text-xs text-slate-600 line-clamp-1">{f.claim}</div>
                              </div>

                              <div className="text-right shrink-0 ml-4">
                                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                                  f.status === 'OUTDATED' ? 'bg-rose-100 text-rose-800' :
                                  f.status === 'FABRICATED' ? 'bg-rose-200 text-rose-900 font-bold' :
                                  f.status === 'CONTRADICTED' ? 'bg-amber-100 text-amber-900' :
                                  f.status === 'VALID' ? 'bg-emerald-100 text-emerald-800' :
                                  'bg-slate-200 text-slate-700'
                                }`}>
                                  {f.status}
                                </span>
                                <div className="text-[10px] text-slate-400 mt-1">
                                  Page {f.page_number} · Conf: {Math.round(f.confidence * 100)}%
                                </div>
                              </div>
                            </div>
                          ))
                        )}
                      </div>

                      {/* Finding Evidence Details */}
                      <div className="overflow-y-auto p-5 bg-slate-50 space-y-3">
                        {selectedFinding ? (
                          <div className="space-y-3 text-xs">
                            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                              <div>
                                <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                                  Evidence Provenance · {selectedFinding.finding_code}
                                </div>
                                <h4 className="text-sm font-bold text-slate-900 mt-0.5">
                                  {selectedFinding.issue_type}
                                </h4>
                              </div>
                              <span className="text-xs text-slate-500">
                                Agent: <strong>{selectedFinding.agent_name}</strong>
                              </span>
                            </div>

                            {selectedFinding.quoted_text && (
                              <div className="p-3 bg-white border border-slate-200 rounded-lg">
                                <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                                  Flagged Judgment Text (Page {selectedFinding.page_number}, Para {selectedFinding.paragraph_index || 'N/A'})
                                </span>
                                <code className="text-slate-800 font-mono text-xs">
                                  \"{selectedFinding.quoted_text}\"
                                </code>
                              </div>
                            )}

                            <div>
                              <span className="font-semibold text-slate-700 block mb-1">Reasoning & Explanation</span>
                              <p className="text-slate-600 leading-relaxed bg-white p-3 rounded-lg border border-slate-200">
                                {selectedFinding.reasoning_explanation}
                              </p>
                            </div>

                            {selectedFinding.evidence_text && (
                              <div className="p-3 rounded-lg bg-emerald-50/60 border border-emerald-200">
                                <span className="font-semibold text-emerald-900 block mb-0.5">
                                  Authoritative Primary Law Evidence
                                </span>
                                <p className="text-emerald-800">
                                  {selectedFinding.evidence_text}
                                </p>
                                {selectedFinding.source_reference && (
                                  <div className="mt-1 text-[11px] text-emerald-700 font-mono">
                                    Source: {selectedFinding.source_reference}
                                  </div>
                                )}
                              </div>
                            )}

                            {selectedFinding.counter_evidence && (
                              <div className="p-2.5 rounded-lg bg-slate-100 border border-slate-200 text-slate-600 text-[11px]">
                                <span className="font-semibold text-slate-800">Counter-Evidence Context: </span>
                                {selectedFinding.counter_evidence}
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-center text-slate-400 text-xs py-10">
                            Select a finding card above to inspect evidence grounding and statutory provenance.
                          </div>
                        )}
                      </div>

                    </div>
                  </div>

                </div>

              </div>
            )}

          </div>
        ) : (
          /* Benchmarks Tab */
          <main className="flex-1 p-8 overflow-y-auto max-w-5xl mx-auto w-full space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Empirical Benchmarks & Baselines</h2>
              <p className="text-xs text-slate-500 mt-1">
                Evaluation across Indian Supreme Court test datasets comparing Multi-Agent Swarm against Single LLM pipelines.
              </p>
            </div>

            <div className="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-sm">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
                  <tr>
                    <th className="p-3.5">Architecture</th>
                    <th className="p-3.5">Citation Accuracy</th>
                    <th className="p-3.5">Hallucination F1</th>
                    <th className="p-3.5">Reasoning Consistency</th>
                    <th className="p-3.5">Precedent MRR</th>
                    <th className="p-3.5">Explainability Rate</th>
                    <th className="p-3.5">Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {benchmarks.map((b, idx) => {
                    const isProposed = b.system.includes('CourtGPT Auditor');
                    return (
                      <tr key={idx} className={isProposed ? 'bg-slate-50 font-semibold text-black' : ''}>
                        <td className="p-3.5">{b.system}</td>
                        <td className="p-3.5 font-mono text-emerald-600">{Math.round(b.citation_accuracy * 100)}%</td>
                        <td className="p-3.5 font-mono">{b.hallucination_f1.toFixed(2)}</td>
                        <td className="p-3.5 font-mono">{Math.round(b.reasoning_consistency_acc * 100)}%</td>
                        <td className="p-3.5 font-mono">{b.precedent_mrr.toFixed(2)}</td>
                        <td className="p-3.5 font-mono text-emerald-600">{Math.round(b.explainability_grounded_rate * 100)}%</td>
                        <td className="p-3.5 font-mono text-slate-500">{b.latency_sec}s</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </main>
        )}

      </div>
    </div>
  );
}
