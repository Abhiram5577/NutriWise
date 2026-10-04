import { useState, useEffect } from 'react';
import apiClient from '../api/client';

/**
 * HealthStatus — displays real-time backend + database connection status.
 * Polls /api/health and /api/health/db on mount.
 */
export default function HealthStatus() {
  const [apiStatus, setApiStatus] = useState({ status: 'checking', loading: true });
  const [dbStatus, setDbStatus] = useState({ status: 'checking', loading: true });

  useEffect(() => {
    checkHealth();
  }, []);

  async function checkHealth() {
    // Check API health
    try {
      const res = await apiClient.get('/api/health');
      setApiStatus({ status: res.data.status, version: res.data.version, loading: false });
    } catch {
      setApiStatus({ status: 'unreachable', loading: false });
    }

    // Check DB health
    try {
      const res = await apiClient.get('/api/health/db');
      setDbStatus({ status: res.data.status, loading: false });
    } catch {
      setDbStatus({ status: 'unreachable', loading: false });
    }
  }

  const isApiOk = apiStatus.status === 'healthy';
  const isDbOk = dbStatus.status === 'connected';

  return (
    <div className="editorial-card fade-in fade-in-delay-1" id="health-status-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
        <div>
          <div className="eyebrow-label">Live Diagnostics</div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--accent-botanical)' }}>System Health</h2>
        </div>
        <button
          className="btn btn-secondary"
          onClick={checkHealth}
          style={{ padding: '0.4rem 0.9rem', fontSize: '0.8rem' }}
          id="refresh-health-btn"
        >
          ↻ Refresh
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        {/* API Status */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ fontSize: '1.25rem' }}>🔌</span>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Backend API</div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>FastAPI Server</div>
            </div>
          </div>
          {apiStatus.loading ? (
            <span className="badge badge-warning">Checking…</span>
          ) : (
            <span className={`badge ${isApiOk ? 'badge-success' : 'badge-error'}`}>
              <span className={`pulse-dot ${isApiOk ? 'green' : 'red'}`}></span>
              {isApiOk ? 'Connected' : 'Disconnected'}
            </span>
          )}
        </div>

        {/* DB Status */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ fontSize: '1.25rem' }}>🗄️</span>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Database</div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>PostgreSQL</div>
            </div>
          </div>
          {dbStatus.loading ? (
            <span className="badge badge-warning">Checking…</span>
          ) : (
            <span className={`badge ${isDbOk ? 'badge-success' : 'badge-error'}`}>
              <span className={`pulse-dot ${isDbOk ? 'green' : 'red'}`}></span>
              {isDbOk ? 'Connected' : 'Disconnected'}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
