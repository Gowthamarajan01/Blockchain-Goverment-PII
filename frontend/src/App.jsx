import React, { useState, useEffect } from 'react';
import './App.css';

// Dynamically detect the server IP for mobile access
const API_BASE = `http://${window.location.hostname}:8000`;

function App() {
  const [activeTab, setActiveTab] = useState('scan');
  const [inputText, setInputText] = useState('');
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [isDragging, setIsDragging] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);

  // Check backend connectivity on load
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch(`${API_BASE}/`);
        if (res.ok) setBackendStatus('Online');
        else setBackendStatus('Error');
      } catch {
        setBackendStatus('Offline');
      }
    };
    checkBackend();
    const interval = setInterval(checkBackend, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleTextScan = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setScanProgress(0);
    setError(null);
    let interval = setInterval(() => setScanProgress(p => p < 90 ? p + 10 : p), 200);
    try {
      const res = await fetch(`${API_BASE}/scan-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });
      clearInterval(interval);
      setScanProgress(100);
      if (!res.ok) throw new Error(`Server Error: ${res.status}`);
      const data = await res.json();
      setResults(data);
      fetchLogs();
    } catch (err) {
      setError(`Connection failed: ${err.message}. Is the backend running?`);
    } finally {
      setLoading(false);
      setTimeout(() => setScanProgress(0), 500);
    }
  };

  const handleFileScan = async () => {
    if (!file) return;
    setLoading(true);
    setScanProgress(0);
    setError(null);
    let interval = setInterval(() => setScanProgress(p => p < 90 ? p + 5 : p), 300);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${API_BASE}/scan-file`, {
        method: 'POST',
        body: formData,
      });
      clearInterval(interval);
      setScanProgress(100);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server Error: ${res.status}`);
      }
      const data = await res.json();
      setResults(data);
      fetchLogs();
    } catch (err) {
      setError(`Scan Failed: ${err.message}. Check if Tesseract is installed if scanning a photo.`);
    } finally {
      setLoading(false);
      setTimeout(() => setScanProgress(0), 500);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_BASE}/logs`);
      const data = await res.json();
      setLogs(data);
    } catch (err) {
      console.error('Error fetching logs', err);
    }
  };

  const handleClearLogs = async () => {
    if (!window.confirm('Are you sure you want to permanently erase the Audit Vault and reset the current session?')) return;
    try {
      const res = await fetch(`${API_BASE}/logs`, { method: 'DELETE' });
      if (res.ok) {
        setLogs([]);
        setResults(null);
        setInputText('');
        setFile(null);
        alert('Vault erased and session reset successfully.');
      } else {
        const errorData = await res.json().catch(() => ({}));
        alert(`Failed to erase vault: ${errorData.detail || 'Unknown server error'}`);
      }
    } catch (err) {
      console.error('Error clearing logs', err);
      alert('Connection error: Could not reach the server.');
    }
  };

  const handleDownload = () => {
    if (!results || !results.masked_text) return;
    const blob = new Blob([results.masked_text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sanitized_${new Date().getTime()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    if (activeTab === 'logs') {
      fetchLogs();
    }
  }, [activeTab]);

  const handleExportTemplate = () => {
    const card = document.getElementById('aadhaar-card');
    if (!card) return;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>Aadhaar Template</title>
          <style>
            body { display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #eee; }
            ${document.querySelector('style')?.innerHTML || ''}
            .sidebar, .nav-links, .content > *:not(.scan-section), .scan-controls, .findings, .masking h3, .masked-output, .actions { display: none !important; }
            .dashboard { display: block !important; }
            .content { padding: 0 !important; background: transparent !important; }
            .aadhaar-template-wrapper { margin: 0 !important; }
            .aadhaar-footer {
  background: #138808 !important;
  font-family: 'JetBrains Mono', monospace !important;
  letter-spacing: 6px !important;
}

.aadhaar-body {
  display: flex !important;
  padding: 25px !important;
  gap: 25px !important;
  background: white !important;
}

.photo-placeholder {
  width: 110px !important;
  height: 135px !important;
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 3rem !important;
  border-radius: 8px !important;
  flex-shrink: 0 !important;
}

.aadhaar-info {
  display: flex !important;
  flex-direction: column !important;
  gap: 15px !important;
  flex-grow: 1 !important;
  text-align: left !important;
}

.info-field {
  display: flex !important;
  flex-direction: column !important;
  gap: 2px !important;
}

.info-field b {
  color: #64748b !important;
  font-size: 0.65rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  margin: 0 !important;
}

.value-masked {
  color: #1e293b !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
  margin: 0 !important;
  line-height: 1.2 !important;
  word-break: break-word !important;
}
          </style>
        </head>
        <body>
          <div class="aadhaar-template-wrapper">
            ${card.outerHTML}
          </div>
          <script>
            setTimeout(() => { window.print(); window.close(); }, 500);
          </script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  return (
    <div className="dashboard">
      {/* Sidebar */}
      <nav className="sidebar">
        <div className="logo">
          <span className="shield-icon">💠</span>
          <h1>HideX</h1>
        </div>
        <ul className="nav-links">
          <li className={activeTab === 'scan' ? 'active' : ''} onClick={() => setActiveTab('scan')}>
            <i>⚡</i> <span>Monitor</span>
          </li>
          <li className={activeTab === 'logs' ? 'active' : ''} onClick={() => setActiveTab('logs')}>
            <i>📂</i> <span>Audit Vault</span>
          </li>
        </ul>
        <div className="sidebar-footer">
          <p>SYSTEM. v2.0</p>
          <p style={{marginTop: '4px'}}>SECURE_LINK: ACTIVE</p>
        </div>
      </nav>

      {/* Main Content */}
      <main className="content">
        <header>
          <h2>{activeTab === 'scan' ? 'Core Processor' : 'Audit Logs'}</h2>
          <div className={`status-indicator ${backendStatus.toLowerCase()}`}>
            <span className="dot"></span> 
            <span>ENGINES {backendStatus.toUpperCase()}</span>
          </div>
        </header>

        {activeTab === 'scan' && (
          <div className="scan-section animate-fade-in">
            <div 
              className={`scan-controls glass-card ${isDragging ? 'drag-active' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {loading && (
                <div className="scan-overlay">
                  <div className="scanning-line"></div>
                  <div className="scan-status-text">ANALYZING_PACKETS... {scanProgress}%</div>
                </div>
              )}
              <div className="tabs-mini">
                <button className={!file ? 'active' : ''} onClick={() => setFile(null)}>TEXT STREAM</button>
                <div className="upload-wrapper">
                  <input type="file" onChange={(e) => setFile(e.target.files[0])} id="fileInput" hidden />
                  <label htmlFor="fileInput" className={file ? 'active label' : 'label'}>
                    {file ? 'CHANGE FILE' : 'DATA UPLOAD'}
                  </label>
                </div>
              </div>

              {!file ? (
                <textarea 
                  placeholder="Insert encrypted or raw data stream for analysis..." 
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                />
              ) : (
                <div className="file-preview">
                  <div className="file-icon">📄</div>
                  <div>
                    <p style={{fontWeight: 700, fontSize: '1.2rem'}}>{file.name}</p>
                    <p style={{color: 'var(--text-muted)'}}>{(file.size / 1024).toFixed(2)} KB // READY_FOR_SCAN</p>
                  </div>
                </div>
              )}

              <button className="btn-primary" onClick={file ? handleFileScan : handleTextScan} disabled={loading}>
                {loading ? 'EXECUTING SCAN...' : 'INITIATE ANALYSIS'}
              </button>
              {error && <p className="error-msg" style={{color: 'var(--danger)', marginTop: '1rem', fontWeight: 600}}>{error}</p>}
            </div>

            {results && (
              <div className="results-container animate-fade-in">
                <div className="results-grid">
                  <div className="findings glass-card">
                    <h3><span>🔍</span> DETECTED_PII [{results.pii_found?.length || 0}]</h3>
                    <div className="findings-list">
                      {results.pii_found?.map((item, idx) => (
                        <div key={idx} className={`finding-item ${item.sensitivity.toLowerCase()}`}>
                          <div style={{display: 'flex', flexDirection: 'column'}}>
                             <span className="type">{item.type}</span>
                             <code className="value">{item.value}</code>
                          </div>
                          <span className="severity">{item.sensitivity} RISK</span>
                        </div>
                      ))}
                      {!results.pii_found?.length && <p className="placeholder-text">NO VULNERABILITIES DETECTED.</p>}
                    </div>
                  </div>

                  <div className="masking glass-card">
                    <div className="mask-header">
                      <h3><span>🔒</span> SANITIZED_STREAM</h3>
                      <div className="actions" style={{display: 'flex', gap: '8px'}}>
                        <button className="btn-small" onClick={() => navigator.clipboard.writeText(results.masked_text)}>COPY</button>
                        <button className="btn-small btn-download" onClick={handleDownload}>EXPORT</button>
                      </div>
                    </div>
                    <pre className="masked-output">{results.masked_text}</pre>
                    
                      <div className="aadhaar-template-wrapper animate-fade-in" style={{marginTop: '2.5rem'}}>
                        <div className="template-header" style={{display: 'flex', justifyContent: 'space-between', marginBottom: '15px', width: '100%', maxWidth: '450px'}}>
                          <h4 style={{fontSize: '0.8rem', color: '#94a3b8', letterSpacing: '2px'}}>VISUAL_ID_GEN</h4>
                          <button className="btn-small" style={{background: 'var(--glass)', borderColor: 'var(--primary)'}} onClick={handleExportTemplate}>TEMPLATE_PRINT</button>
                        </div>
                        <div className="aadhaar-card-template" id="aadhaar-card">
                          <div className="aadhaar-header">
                            <div className="gov-logo" style={{color: '#1e1b4b'}}>GOVERNMENT OF INDIA</div>
                            <div className="aadhaar-logo">AADHAAR</div>
                          </div>
                          <div className="aadhaar-body">
                            <div className="photo-placeholder">👤</div>
                            <div className="aadhaar-info">
                              <div className="info-field">
                                <b>Name / नाम</b>
                                <div className="value-masked">
                                  {(() => {
                                    const name = results.pii_found?.find(p => p.type === 'Full_Name')?.value;
                                    return name ? `${name.substring(0, 2)}${'*'.repeat(name.length - 2)}` : 'VERIFIED_USER';
                                  })()}
                                </div>
                              </div>
                              <div className="info-field">
                                <b>Gender / लिंग</b>
                                <div className="value-masked">REDACTED / संरक्षित</div>
                              </div>
                              <div className="info-field">
                                <b>Address / पता</b>
                                <div className="value-masked">
                                  {(() => {
                                    const loc = results.pii_found?.find(p => p.type === 'Location')?.value;
                                    return loc ? `${loc.substring(0, 5)}${'*'.repeat(12)}` : 'SECURE_ZONE_INDIA';
                                  })()}
                                </div>
                              </div>
                            </div>
                            <div className="watermark">SECURE</div>
                          </div>
                          <div className="aadhaar-footer">
                            {(() => {
                              const raw = results.pii_found?.find(p => p.type === 'Aadhaar')?.value || 'XXXX XXXX XXXX';
                              return raw.replace(/(\d{4}) (\d{4}) (\d{4})/, 'XXXX XXXX $3').replace(/\d{8}/, 'XXXXXXXX');
                            })()}
                          </div>
                        </div>
                      </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="logs-section animate-fade-in">
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem'}}>
              <h3 style={{margin: 0, color: 'var(--primary)', letterSpacing: '2px'}}>NETWORK_VAULT_HISTORY</h3>
              <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
                <span style={{fontSize: '0.75rem', color: 'var(--success)', background: 'rgba(16, 185, 129, 0.1)', padding: '4px 10px', borderRadius: '4px', border: '1px solid var(--success)'}}>
                  🛡️ AUTO_WIPE: ACTIVE
                </span>
                <button className="btn-small btn-danger" onClick={handleClearLogs} style={{background: 'rgba(239, 68, 68, 0.1)', borderColor: 'var(--danger)', color: 'var(--danger)'}}>
                  ERASE_VAULT
                </button>
              </div>
            </div>
            <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem', fontStyle: 'italic'}}>
              NOTE: To protect PII, this vault is automatically wiped before every new scan. Only your most recent activity is displayed.
            </p>
            <div className="glass-card" style={{overflowX: 'auto', padding: '1rem'}}>
              <table className="logs-table">
                <thead>
                  <tr>
                    <th>TIMESTAMP</th>
                    <th>DATA_SOURCE</th>
                    <th>PII_COUNT</th>
                    <th>PROTOCOL</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log, idx) => (
                    <tr key={idx}>
                      <td style={{fontFamily: 'JetBrains Mono', color: 'var(--accent)'}}>{new Date(log.timestamp).toLocaleString().toUpperCase()}</td>
                      <td style={{fontWeight: 600}}>{log.file_name || 'RAW_INPUT'}</td>
                      <td>
                        <span className="count" style={{
                          background: log.count > 0 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                          color: log.count > 0 ? 'var(--danger)' : 'var(--success)',
                          border: `1px solid ${log.count > 0 ? 'var(--danger)' : 'var(--success)'}`
                        }}>
                          {log.count} FOUND
                        </span>
                      </td>
                      <td><span className="status-tag">COMMITTED</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!logs.length && <div className="empty-logs" style={{textAlign: 'center', padding: '4rem', color: 'var(--text-muted)'}}>VAULT IS CURRENTLY EMPTY.</div>}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
