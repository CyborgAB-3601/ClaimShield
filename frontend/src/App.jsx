import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import './App.css';
import { INSURERS } from './catalog';
import { LANGUAGES, useTranslate } from './i18n';
import { getSubmissionSteps } from './submissionSteps';

const API_URL = import.meta.env.VITE_API_URL || '';

function StampBadge() {
  return (
    <div className="stamp-badge" aria-hidden="true">
      <span>PRE-SUBMISSION</span>
      <span>AUDIT</span>
    </div>
  );
}

function LanguageSelect({ lang, onChange }) {
  return (
    <select className="lang-select" value={lang} onChange={(e) => onChange(e.target.value)} aria-label="Language">
      {LANGUAGES.map((l) => (
        <option key={l.code} value={l.code}>
          {l.label}
        </option>
      ))}
    </select>
  );
}

function PolicySelector({ insurerId, policyType, onInsurerChange, onPolicyTypeChange, t }) {
  const insurer = INSURERS.find((i) => i.id === insurerId) || INSURERS[0];
  return (
    <div className="policy-selector">
      <label className="policy-select-field">
        <span>{t('insurerLabel')}</span>
        <select value={insurerId} onChange={(e) => onInsurerChange(e.target.value)}>
          {INSURERS.map((ins) => (
            <option key={ins.id} value={ins.id}>
              {ins.name}
            </option>
          ))}
        </select>
      </label>
      <label className="policy-select-field">
        <span>{t('policyTypeLabel')}</span>
        <select value={policyType} onChange={(e) => onPolicyTypeChange(e.target.value)}>
          {insurer.policyTypes.map((pt) => (
            <option key={pt} value={pt}>
              {pt}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}

function SubmissionSteps({ lang, portalName, t }) {
  const steps = useMemo(() => getSubmissionSteps(lang, portalName), [lang, portalName]);
  return (
    <div className="submission-steps">
      <h3>{t('stepsTitle')}</h3>
      <ol>
        {steps.map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>
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

function UploadCard({
  files,
  onAddFiles,
  onRemoveFile,
  disabled,
  single = false,
  title,
  hint,
  addLabel = 'Capture / choose files',
  moreLabel = 'Add another document',
}) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFiles = useCallback(
    (fileList) => {
      const incoming = Array.from(fileList || []);
      if (incoming.length) onAddFiles(single ? incoming.slice(0, 1) : incoming);
    },
    [onAddFiles, single],
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
          {files.length > 0
            ? single
              ? files[0].name
              : `${files.length} document${files.length > 1 ? 's' : ''} staged`
            : title}
        </p>
        <p className="upload-hint">{hint}</p>
        {(!single || files.length === 0) && (
          <button
            type="button"
            className="btn btn-outline"
            disabled={disabled}
            onClick={() => inputRef.current?.click()}
          >
            {files.length > 0 ? moreLabel : addLabel}
          </button>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*,.pdf"
          capture="environment"
          multiple={!single}
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

function fieldState(field) {
  if (!field.refused) return 'filled';
  return field.status === 'illegible' ? 'illegible' : 'missing';
}

function ChecklistRow({ spec, field }) {
  const [open, setOpen] = useState(false);
  const state = fieldState(field);

  return (
    <li className={`ledger-row field-state-${state}`}>
      <button
        type="button"
        className="ledger-row-main"
        onClick={() => setOpen((v) => !v)}
        disabled={!field.source_line}
      >
        <span className="ledger-label">{spec.label}</span>
        <span className="ledger-leader" aria-hidden="true" />
        {field.refused ? (
          <span className={`ledger-refused-value ledger-tag-${state}`}>
            {state === 'illegible' ? 'ASK DOCTOR / HOSPITAL' : 'MISSING'}
          </span>
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

function groupBySection(fieldSchema, mergedFields) {
  const fieldMap = new Map(mergedFields.map((f) => [f.field, f]));
  const sections = new Map();
  for (const spec of fieldSchema) {
    const field = fieldMap.get(spec.field_key);
    if (!field) continue;
    if (!sections.has(spec.section)) sections.set(spec.section, []);
    sections.get(spec.section).push({ spec, field });
  }
  return sections;
}

function ChecklistResult({ result, t }) {
  const [showRaw, setShowRaw] = useState(false);
  const sections = useMemo(
    () => groupBySection(result.field_schema, result.merged_fields),
    [result.field_schema, result.merged_fields],
  );
  const labelByKey = useMemo(
    () => new Map(result.field_schema.map((s) => [s.field_key, s.label])),
    [result.field_schema],
  );
  const illegible = result.merged_fields.filter((f) => f.refused && f.status === 'illegible');
  const missing = result.merged_fields.filter((f) => f.refused && f.status === 'missing');

  return (
    <div className="ledger">
      <Perforation />
      <div className="ledger-head">
        <h2>{t('checklistTitle')}</h2>
        <p className="ledger-sub">
          {illegible.length === 0 && missing.length === 0
            ? 'Every field your claim form asks for is filled with usable confidence'
            : `${illegible.length} illegible · ${missing.length} missing`}
        </p>
      </div>
      {[...sections.entries()].map(([section, rows]) => (
        <div key={section} className="ledger-section">
          <h3 className="ledger-section-head">{section}</h3>
          <ul className="ledger-list">
            {rows.map(({ spec, field }) => (
              <ChecklistRow key={spec.field_key} spec={spec} field={field} />
            ))}
          </ul>
        </div>
      ))}
      {(illegible.length > 0 || missing.length > 0) && (
        <div className="fix-checklist">
          <span className="stamp-mini">FIX BEFORE SUBMITTING</span>
          <div>
            {illegible.length > 0 && (
              <p>
                <strong>Present but unclear — ask the hospital/doctor to rewrite:</strong>{' '}
                {illegible.map((f) => labelByKey.get(f.field) || f.field).join(', ')}.
              </p>
            )}
            {missing.length > 0 && (
              <p>
                <strong>Not found in any uploaded document — obtain and re-upload:</strong>{' '}
                {missing.map((f) => labelByKey.get(f.field) || f.field).join(', ')}.
              </p>
            )}
          </div>
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
          {finding.clause_ref === 'not found' ? (
            <p className="finding-clause finding-clause-missing">
              No matching clause could be verified in the uploaded policy document.
            </p>
          ) : (
            <>
              <blockquote className="finding-quote">{finding.quote}</blockquote>
              <p className="finding-clause">
                Clause {finding.clause_ref}
                {finding.page != null ? ` · p.${finding.page}` : ' · page not stated'}
              </p>
            </>
          )}
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

function FindingsReport({ result, t }) {
  return (
    <div className="findings-report">
      <Perforation />
      <div className="findings-head">
        <h2>{t('findingsTitle')}</h2>
        <span className="stamp-mini">{result.policy_display_name}</span>
      </div>
      <div className="totals-strip">
        <div className="totals-cell">
          <span>{t('billTotalLabel')}</span>
          <strong>{money(result.totals.bill_total)}</strong>
        </div>
        <div className="totals-cell claimable">
          <span>{t('claimableLabel')}</span>
          <strong>{money(result.totals.claimable_amount)}</strong>
        </div>
        <div className="totals-cell deduct">
          <span>{t('deductibleLabel')}</span>
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

function DocumentChat({ rawMarkdown, extractedFields, findings, totals }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const scrollRef = useRef(null);

  // Auto-start chat if there are missing fields
  useEffect(() => {
    const hasMissing = extractedFields.some(f => f.refused || f.value == null);
    if (hasMissing && messages.length === 0 && !isLoading) {
      setIsOpen(true);
      const initChat = async () => {
        setIsLoading(true);
        try {
          const res = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              raw_markdown: rawMarkdown,
              extracted_fields: extractedFields,
              findings: findings,
              totals: totals,
              messages: [{ role: 'system', content: 'Initialize missing field interview' }]
            })
          });
          if (!res.ok) throw new Error('Chat failed');
          const data = await res.json();
          setMessages([{ role: 'assistant', content: data.reply }]);
        } catch (err) {
          console.error(err);
          // Set a message to prevent infinite retry loop
          setMessages([{ role: 'assistant', content: 'Sorry, I am unable to connect right now.' }]);
        } finally {
          setIsLoading(false);
        }
      };
      initChat();
    }
  }, [extractedFields, rawMarkdown, messages.length, isLoading]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const userMsg = { role: 'user', content: input.trim() };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);
    
    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_markdown: rawMarkdown,
          extracted_fields: extractedFields,
          findings: findings,
          totals: totals,
          messages: messages.length > 0 && messages[0].role === 'assistant' 
            ? [{ role: 'system', content: 'Initialize missing field interview' }, ...newMessages]
            : newMessages
        })
      });
      if (!res.ok) throw new Error('Chat failed');
      const data = await res.json();
      setMessages([...newMessages, { role: 'assistant', content: data.reply }]);
    } catch (err) {
      console.error(err);
      setMessages([...newMessages, { role: 'assistant', content: 'Sorry, there was an error processing your response.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <button 
        className="chat-fab" 
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle Claim Assistant"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </button>

      {isOpen && (
        <div className="document-chat">
          <div className="chat-header">
            <h3>Claim Assistant</h3>
            <button className="chat-close" onClick={() => setIsOpen(false)} aria-label="Close Chat">×</button>
          </div>
          <div className="chat-header-sub">
            <p>Let's complete your missing information.</p>
          </div>
          <div className="chat-messages" ref={scrollRef}>
            {messages.length === 0 && !isLoading && (
              <div className="chat-empty">All fields are present! You're ready to submit.</div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`chat-bubble ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {isLoading && (
              <div className="chat-bubble assistant loading">
                <span className="dot"></span><span className="dot"></span><span className="dot"></span>
              </div>
            )}
          </div>
          <form onSubmit={sendMessage} className="chat-input-form">
            <input 
              type="text" 
              value={input} 
              onChange={(e) => setInput(e.target.value)} 
              placeholder="Type your answer..."
              disabled={isLoading || (messages.length === 0 && extractedFields.every(f => !f.refused && f.value != null))}
            />
            <button type="submit" className="btn btn-primary" disabled={!input.trim() || isLoading}>
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}

function App() {
  const [files, setFiles] = useState([]);
  const [policyFiles, setPolicyFiles] = useState([]);
  const [claimFormFiles, setClaimFormFiles] = useState([]);
  const [status, setStatus] = useState('idle'); // idle | loading | done | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [fillStatus, setFillStatus] = useState('idle'); // idle | loading | error
  const [fillError, setFillError] = useState(null);
  const [lang, setLang] = useState('en');
  const [insurerId, setInsurerId] = useState(INSURERS[0].id);
  const [policyType, setPolicyType] = useState(INSURERS[0].policyTypes[0]);
  const t = useTranslate(lang);
  const selectedInsurer = INSURERS.find((i) => i.id === insurerId) || INSURERS[0];

  const handleInsurerChange = useCallback((id) => {
    setInsurerId(id);
    const insurer = INSURERS.find((i) => i.id === id) || INSURERS[0];
    setPolicyType(insurer.policyTypes[0]);
  }, []);

  const addFiles = useCallback((newFiles) => {
    setFiles((prev) => [...prev, ...newFiles]);
    setResult(null);
    setStatus('idle');
    setError(null);
  }, []);

  const removeFile = useCallback((file) => {
    setFiles((prev) => prev.filter((f) => f !== file));
  }, []);

  const addPolicyFiles = useCallback((newFiles) => {
    setPolicyFiles(newFiles);
    setResult(null);
    setStatus('idle');
    setError(null);
  }, []);

  const removePolicyFile = useCallback((file) => {
    setPolicyFiles((prev) => prev.filter((f) => f !== file));
  }, []);

  const addClaimFormFiles = useCallback((newFiles) => {
    setClaimFormFiles(newFiles);
    setResult(null);
    setStatus('idle');
    setError(null);
  }, []);

  const removeClaimFormFile = useCallback((file) => {
    setClaimFormFiles((prev) => prev.filter((f) => f !== file));
  }, []);

  const runAudit = useCallback(async () => {
    if (files.length === 0 || policyFiles.length === 0 || claimFormFiles.length === 0) return;
    setStatus('loading');
    setError(null);
    try {
      const form = new FormData();
      files.forEach((f) => form.append('files', f));
      form.append('policy_file', policyFiles[0]);
      form.append('claim_form', claimFormFiles[0]);
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
  }, [files, policyFiles, claimFormFiles]);

  const reset = useCallback(() => {
    setFiles([]);
    setPolicyFiles([]);
    setClaimFormFiles([]);
    setResult(null);
    setStatus('idle');
    setError(null);
    setFillStatus('idle');
    setFillError(null);
  }, []);

  const downloadFilledClaimForm = useCallback(async () => {
    if (!result || claimFormFiles.length === 0) return;
    setFillStatus('loading');
    setFillError(null);
    try {
      const form = new FormData();
      form.append('claim_form', claimFormFiles[0]);
      form.append('merged_fields', JSON.stringify(result.merged_fields));
      const res = await fetch(`${API_URL}/api/fill-claim-form`, { method: 'POST', body: form });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const disposition = res.headers.get('Content-Disposition') || '';
      const match = disposition.match(/filename="?([^"]+)"?/);
      a.download = match ? match[1] : 'claim_form_filled.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setFillStatus('idle');
    } catch (err) {
      setFillError(err.message || 'Something went wrong');
      setFillStatus('error');
    }
  }, [result, claimFormFiles]);

  return (
    <div className="page">
      <div className="top-bar">
        <LanguageSelect lang={lang} onChange={setLang} />
      </div>

      <header className="site-header">
        <div className="wordmark">
          <h1>Claim Shield</h1>
          <p className="tagline">{t('tagline')}</p>
        </div>
        <StampBadge />
      </header>

      <PolicySelector
        insurerId={insurerId}
        policyType={policyType}
        onInsurerChange={handleInsurerChange}
        onPolicyTypeChange={setPolicyType}
        t={t}
      />

      <main className="stage">
        <UploadCard
          files={files}
          onAddFiles={addFiles}
          onRemoveFile={removeFile}
          disabled={status === 'loading'}
          title={t('uploadDocsTitle')}
          hint={t('uploadDocsHint')}
          addLabel={t('captureChooseBtn')}
          moreLabel={t('addAnotherDocBtn')}
        />

        <div className="upload-grid">
          <UploadCard
            single
            files={policyFiles}
            onAddFiles={addPolicyFiles}
            onRemoveFile={removePolicyFile}
            disabled={status === 'loading'}
            title={t('uploadPolicyTitle')}
            hint={t('uploadPolicyHint')}
            addLabel={t('choosePolicyBtn')}
          />
          <UploadCard
            single
            files={claimFormFiles}
            onAddFiles={addClaimFormFiles}
            onRemoveFile={removeClaimFormFile}
            disabled={status === 'loading'}
            title={t('uploadClaimFormTitle')}
            hint={t('uploadClaimFormHint')}
            addLabel={t('chooseClaimFormBtn')}
          />
        </div>

        <div className="stage-actions">
          {status !== 'done' && (
            <button
              type="button"
              className="btn btn-primary"
              disabled={
                files.length === 0 || policyFiles.length === 0 || claimFormFiles.length === 0 || status === 'loading'
              }
              onClick={runAudit}
            >
              {status === 'loading' ? (
                <span className="scanning-label">
                  <span className="scan-bar" />
                  {t('scanningLabel')}
                </span>
              ) : (
                t('runAuditBtn')
              )}
            </button>
          )}
          {(status === 'done' || status === 'error') && (
            <button type="button" className="btn btn-outline" onClick={reset}>
              {t('newClaimBtn')}
            </button>
          )}
        </div>

        {status === 'error' && (
          <div className="error-banner">
            <strong>{t('auditFailedLabel')}</strong> {error}
          </div>
        )}

        {status === 'done' && result && (
          <div className="results-container">
            <ChecklistResult result={result} t={t} />
            <FindingsReport result={result} t={t} />
            <div className="fill-form-actions">
              <button
                type="button"
                className="btn btn-primary"
                disabled={fillStatus === 'loading'}
                onClick={downloadFilledClaimForm}
              >
                {fillStatus === 'loading' ? t('fillingLabel') : t('downloadFilledBtn')}
              </button>
              {fillStatus === 'error' && (
                <div className="error-banner">
                  <strong>Could not fill claim form.</strong> {fillError}
                </div>
              )}
              <SubmissionSteps lang={lang} portalName={selectedInsurer.portalName} t={t} />
            </div>
          </div>
        )}
      </main>

      {status === 'done' && result && (
        <DocumentChat 
          rawMarkdown={result.documents.map(d => d.raw_markdown).join('\n\n')}
          extractedFields={result.merged_fields} 
          findings={result.findings}
          totals={result.totals}
        />
      )}

      <footer className="site-footer">
        <span>{t('footerLine')}</span>
      </footer>
    </div>
  );
}

export default App;
