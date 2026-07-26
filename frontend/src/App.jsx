import { useCallback, useRef, useState } from 'react';
import { FIELD_LABELS } from './fieldLabels';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8010';
const POLICY_ID = 'hdfc_ergo_optima_secure';

function StampBadge() {
  return (
    <div className="stamp-badge" aria-hidden="true">
      <span>PRE-SUBMISSION</span>
      <span>AUDIT</span>
    </div>
  );
}

function Perforation() {
  return (
    <div className="perforation" aria-hidden="true">
      {Array.from({ length: 22 }).map((_, i) => (
        <span key={i} />
      ))}
    </div>
  );
}

function StagedFile({ file, onRemove, disabled }) {
  const isImage = file.type.startsWith('image/');
  const previewUrl = isImage ? URL.createObjectURL(file) : null;

  return (
    <li className="staged-file">
      {previewUrl ? (
        <img className="staged-file-thumb" src={previewUrl} alt={file.name} />
      ) : (
        <div className="staged-file-thumb staged-file-thumb-doc" aria-hidden="true">
          PDF
        </div>
      )}
      <span className="staged-file-name">{file.name}</span>
      <button
        type="button"
        className="staged-file-remove"
        onClick={() => onRemove(file)}
        disabled={disabled}
        aria-label={`Remove ${file.name}`}
      >
        ×
      </button>
    </li>
  );
}

function UploadCard({ files, onAddFiles, onRemoveFile, disabled }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFiles = useCallback(
    (fileList) => {
      const incoming = Array.from(fileList || []);
      if (incoming.length) onAddFiles(incoming);
    },
    [onAddFiles],
  );

  return (
    <div
      className={`upload-card${dragOver ? ' drag-over' : ''}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        handleFiles(e.dataTransfer.files);
      }}
    >
      <Perforation />
      <div className="upload-body">
        {files.length > 0 ? (
          <ul className="staged-file-list">
            {files.map((f, i) => (
              <StagedFile key={`${f.name}-${i}`} file={f} onRemove={onRemoveFile} disabled={disabled} />
            ))}
          </ul>
        ) : (
          <svg className="upload-icon" viewBox="0 0 64 64" fill="none" aria-hidden="true">
            <rect x="10" y="6" width="44" height="52" rx="2" stroke="currentColor" strokeWidth="2" />
            <path d="M18 18h28M18 28h28M18 38h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <circle cx="46" cy="46" r="13" fill="var(--paper)" stroke="currentColor" strokeWidth="2" />
            <path d="M46 40v12M40 46h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
        )}
        <p className="upload-title">
          {files.length > 0 ? `${files.length} document${files.length > 1 ? 's' : ''} staged` : 'Photograph the discharge summary + bill'}
        </p>
        <p className="upload-hint">Handwritten or mixed-script is fine — illegible fields get flagged, not guessed.</p>
        <button
          type="button"
          className="btn btn-outline"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
        >
          {files.length > 0 ? 'Add another document' : 'Capture / choose files'}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept="image/*,.pdf"
          capture="environment"
          multiple
          hidden
          onChange={(e) => {
            handleFiles(e.target.files);
            e.target.value = '';
          }}
        />
      </div>
    </div>
  );
}

function ConfidenceTag({ confidence }) {
  if (confidence === null || confidence === undefined) return null;
  const pct = Math.round(confidence * 100);
  return <span className="confidence-tag">{pct}%</span>;
}

function LedgerRow({ field }) {
  const [open, setOpen] = useState(false);
  const label = FIELD_LABELS[field.field] || field.field;

  return (
    <li className={`ledger-row${field.refused ? ' refused' : ''}`}>
      <button
        type="button"
        className="ledger-row-main"
        onClick={() => setOpen((v) => !v)}
        disabled={!field.source_line}
      >
        <span className="ledger-label">{label}</span>
        <span className="ledger-leader" aria-hidden="true" />
        {field.refused ? (
          <span className="ledger-refused-value">— UNREADABLE —</span>
        ) : (
          <span className="ledger-value">{field.value}</span>
        )}
        <ConfidenceTag confidence={field.confidence} />
      </button>
      {open && field.source_line && (
        <div className="ledger-source">
          <span className="ledger-source-label">source</span>
          <q>{field.source_line}</q>
          {field.source_document && <span className="ledger-source-doc">{field.source_document}</span>}
        </div>
      )}
    </li>
  );
}

function LedgerResult({ result }) {
  const [showRaw, setShowRaw] = useState(false);
  const refusedCount = result.merged_fields.filter((f) => f.refused).length;

  return (
    <div className="ledger">
      <Perforation />
      <div className="ledger-head">
        <h2>Claim Ledger</h2>
        <p className="ledger-sub">
          {refusedCount > 0
            ? `${refusedCount} field${refusedCount > 1 ? 's' : ''} refused — cannot be read reliably`
            : 'All fields extracted with usable confidence'}
        </p>
      </div>
      <ul className="ledger-list">
        {result.merged_fields.map((f) => (
          <LedgerRow key={f.field} field={f} />
        ))}
      </ul>
      {refusedCount > 0 && (
        <div className="fix-checklist">
          <span className="stamp-mini">GET RE-CONFIRMED</span>
          <p>
            Ask the hospital / doctor to rewrite the flagged field(s) legibly before you submit —
            everything else is claim-ready.
          </p>
        </div>
      )}
      <div className="ledger-footer">
        <button type="button" className="raw-toggle" onClick={() => setShowRaw((v) => !v)}>
          {showRaw ? 'hide digitised source' : 'view digitised source'}
        </button>
        <span className="timing">
          {result.documents.length} doc{result.documents.length > 1 ? 's' : ''} ·{' '}
          {result.documents.reduce((a, d) => a + d.digitise_seconds, 0).toFixed(1)}s digitise ·{' '}
          {result.documents.reduce((a, d) => a + d.extract_seconds, 0).toFixed(1)}s extract
        </span>
      </div>
      {showRaw && (
        <div className="raw-markdown-group">
          {result.documents.map((d) => (
            <div key={d.filename}>
              <p className="raw-markdown-filename">{d.filename}</p>
              <pre className="raw-markdown">{d.raw_markdown}</pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const RISK_LABELS = {
  none: 'CLEAR',
  insufficient_data: 'VERIFY',
  likely_rejection: 'AT RISK',
};

function FindingRow({ finding }) {
  const [open, setOpen] = useState(false);
  return (
    <li className={`finding-row finding-risk-${finding.risk}`}>
      <button type="button" className="finding-row-main" onClick={() => setOpen((v) => !v)}>
        <span className="finding-risk-tag">{RISK_LABELS[finding.risk] || finding.risk}</span>
        <span className="finding-verdict">{finding.verdict}</span>
      </button>
      {open && (
        <div className="finding-detail">
          <blockquote className="finding-quote">{finding.quote}</blockquote>
          <p className="finding-clause">
            Clause {finding.clause_ref} · p.{finding.page}
          </p>
          {finding.source_line && (
            <p className="finding-source">
              <span className="ledger-source-label">document</span> <q>{finding.source_line}</q>
              {finding.source_document && <span className="ledger-source-doc">{finding.source_document}</span>}
            </p>
          )}
        </div>
      )}
    </li>
  );
}

function money(v) {
  if (v === null || v === undefined) return '—';
  return `₹${v.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function FindingsReport({ result }) {
  return (
    <div className="findings-report">
      <Perforation />
      <div className="findings-head">
        <h2>Rejection-Risk Report</h2>
        <span className="stamp-mini">{result.policy_display_name}</span>
      </div>
      <div className="totals-strip">
        <div className="totals-cell">
          <span>Bill total</span>
          <strong>{money(result.totals.bill_total)}</strong>
        </div>
        <div className="totals-cell claimable">
          <span>Claimable</span>
          <strong>{money(result.totals.claimable_amount)}</strong>
        </div>
        <div className="totals-cell deduct">
          <span>Deductible</span>
          <strong>{money(result.totals.deductible_amount)}</strong>
        </div>
      </div>
      <ul className="findings-list">
        {result.findings.map((f, i) => (
          <FindingRow key={i} finding={f} />
        ))}
      </ul>
    </div>
  );
}

function App() {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState('idle'); // idle | loading | done | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const addFiles = useCallback((newFiles) => {
    setFiles((prev) => [...prev, ...newFiles]);
    setResult(null);
    setStatus('idle');
    setError(null);
  }, []);

  const removeFile = useCallback((file) => {
    setFiles((prev) => prev.filter((f) => f !== file));
  }, []);

  const runAudit = useCallback(async () => {
    if (files.length === 0) return;
    setStatus('loading');
    setError(null);
    try {
      const form = new FormData();
      files.forEach((f) => form.append('files', f));
      form.append('policy_id', POLICY_ID);
      const res = await fetch(`${API_URL}/api/audit`, { method: 'POST', body: form });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }
      const data = await res.json();
      setResult(data);
      setStatus('done');
    } catch (err) {
      setError(err.message || 'Something went wrong');
      setStatus('error');
    }
  }, [files]);

  const reset = useCallback(() => {
    setFiles([]);
    setResult(null);
    setStatus('idle');
    setError(null);
  }, []);

  return (
    <div className="page">
      <header className="site-header">
        <div className="wordmark">
          <h1>Claim Shield</h1>
          <p className="tagline">It won&rsquo;t invent your diagnosis. It will tell you what the insurer won&rsquo;t.</p>
        </div>
        <StampBadge />
      </header>

      <main className="stage">
        <UploadCard
          files={files}
          onAddFiles={addFiles}
          onRemoveFile={removeFile}
          disabled={status === 'loading'}
        />

        <div className="stage-actions">
          {status !== 'done' && (
            <button
              type="button"
              className="btn btn-primary"
              disabled={files.length === 0 || status === 'loading'}
              onClick={runAudit}
            >
              {status === 'loading' ? (
                <span className="scanning-label">
                  <span className="scan-bar" />
                  Reading documents…
                </span>
              ) : (
                'Run pre-submission audit'
              )}
            </button>
          )}
          {(status === 'done' || status === 'error') && (
            <button type="button" className="btn btn-outline" onClick={reset}>
              Start a new claim
            </button>
          )}
        </div>

        {status === 'error' && (
          <div className="error-banner">
            <strong>Audit failed.</strong> {error}
          </div>
        )}

        {status === 'done' && result && (
          <>
            <LedgerResult result={result} />
            <FindingsReport result={result} />
          </>
        )}
      </main>

      <footer className="site-footer">
        <span>Sarvam Document Intelligence · Digitise → structured audit</span>
      </footer>
    </div>
  );
}

export default App;
