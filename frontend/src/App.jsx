import { useCallback, useRef, useState } from 'react';
import { FIELD_LABELS } from './fieldLabels';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8010';

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

function UploadCard({ onFile, fileName, previewUrl, disabled }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFiles = useCallback(
    (fileList) => {
      const file = fileList?.[0];
      if (file) onFile(file);
    },
    [onFile],
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
        {previewUrl ? (
          <img className="doc-preview" src={previewUrl} alt="Uploaded document preview" />
        ) : (
          <svg className="upload-icon" viewBox="0 0 64 64" fill="none" aria-hidden="true">
            <rect x="10" y="6" width="44" height="52" rx="2" stroke="currentColor" strokeWidth="2" />
            <path d="M18 18h28M18 28h28M18 38h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <circle cx="46" cy="46" r="13" fill="var(--paper)" stroke="currentColor" strokeWidth="2" />
            <path d="M46 40v12M40 46h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
        )}
        <p className="upload-title">
          {fileName ? fileName : 'Photograph the discharge summary'}
        </p>
        <p className="upload-hint">Handwritten or mixed-script is fine — illegible fields get flagged, not guessed.</p>
        <button
          type="button"
          className="btn btn-outline"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
        >
          {fileName ? 'Choose a different file' : 'Capture / choose file'}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept="image/*,.pdf"
          capture="environment"
          hidden
          onChange={(e) => handleFiles(e.target.files)}
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
        </div>
      )}
    </li>
  );
}

function LedgerResult({ result }) {
  const [showRaw, setShowRaw] = useState(false);
  const refusedCount = result.fields.filter((f) => f.refused).length;

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
        {result.fields.map((f) => (
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
          digitise {result.digitise_seconds}s · extract {result.extract_seconds}s
        </span>
      </div>
      {showRaw && <pre className="raw-markdown">{result.raw_markdown}</pre>}
    </div>
  );
}

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [status, setStatus] = useState('idle'); // idle | loading | done | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFile = useCallback((f) => {
    setFile(f);
    setResult(null);
    setStatus('idle');
    setError(null);
    if (f.type.startsWith('image/')) {
      setPreviewUrl(URL.createObjectURL(f));
    } else {
      setPreviewUrl(null);
    }
  }, []);

  const runAudit = useCallback(async () => {
    if (!file) return;
    setStatus('loading');
    setError(null);
    try {
      const form = new FormData();
      form.append('file', file);
      const res = await fetch(`${API_URL}/api/extract`, { method: 'POST', body: form });
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
  }, [file]);

  const reset = useCallback(() => {
    setFile(null);
    setPreviewUrl(null);
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
          onFile={handleFile}
          fileName={file?.name}
          previewUrl={previewUrl}
          disabled={status === 'loading'}
        />

        <div className="stage-actions">
          {status !== 'done' && (
            <button
              type="button"
              className="btn btn-primary"
              disabled={!file || status === 'loading'}
              onClick={runAudit}
            >
              {status === 'loading' ? (
                <span className="scanning-label">
                  <span className="scan-bar" />
                  Reading document…
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

        {status === 'done' && result && <LedgerResult result={result} />}
      </main>

      <footer className="site-footer">
        <span>Sarvam Document Intelligence · Digitise → structured audit</span>
      </footer>
    </div>
  );
}

export default App;
