import { useState, useEffect, useCallback } from 'react';
import { getLabResults, createLabResult, updateLabResult, deleteLabResult } from '../api/labResults';
import './BloodTests.css';

// Standard clinical biomarker presets required by NutriWise
export const CLINICAL_BLOOD_TESTS = [
  { name: 'Hemoglobin', unit: 'g/dL', ref: '13.8 - 17.2 (Male), 12.1 - 15.1 (Female)', icon: '🩸', desc: 'Oxygen-carrying protein in red blood cells' },
  { name: 'Vitamin D', unit: 'ng/mL', ref: '30 - 100', icon: '☀️', desc: 'Bone density, immune health, and mood' },
  { name: 'Vitamin B12', unit: 'pg/mL', ref: '200 - 900', icon: '⚡', desc: 'Nerve function, brain activity, and RBC creation' },
  { name: 'Iron', unit: 'mcg/dL', ref: '60 - 170', icon: '🧲', desc: 'Serum iron concentration and cellular energy' },
  { name: 'Calcium', unit: 'mg/dL', ref: '8.5 - 10.2', icon: '🦴', desc: 'Bones, muscle contraction, and cardiac rhythm' },
];

const EMPTY_FORM = {
  test_name: '',
  result_value: '',
  unit: '',
  reference_range: '',
  test_date: new Date().toISOString().split('T')[0],
  notes: '',
};

export default function BloodTests() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  // Delete confirm
  const [deleteId, setDeleteId] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const loadRecords = useCallback(async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });
    try {
      const data = await getLabResults();
      setRecords(data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load blood tests.' });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRecords();
  }, [loadRecords]);

  function openAddModal() {
    setEditingEntry(null);
    setForm({ ...EMPTY_FORM, test_date: new Date().toISOString().split('T')[0] });
    setFormError('');
    setShowModal(true);
  }

  function openEditModal(entry) {
    setEditingEntry(entry);
    setForm({
      test_name: entry.test_name,
      result_value: entry.result_value?.toString() || '',
      unit: entry.unit,
      reference_range: entry.reference_range || '',
      test_date: entry.test_date,
      notes: entry.notes || '',
    });
    setFormError('');
    setShowModal(true);
  }

  function closeModal() {
    setShowModal(false);
    setEditingEntry(null);
    setForm(EMPTY_FORM);
    setFormError('');
  }

  function handleFormChange(e) {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
    setFormError('');
  }

  async function handleFormSubmit(e) {
    e.preventDefault();
    setFormError('');

    if (!form.test_name.trim()) {
      setFormError('Test name is required.');
      return;
    }
    if (!form.result_value || isNaN(parseFloat(form.result_value))) {
      setFormError('A valid numeric result value is required.');
      return;
    }
    if (!form.unit.trim()) {
      setFormError('Unit is required.');
      return;
    }
    if (!form.test_date) {
      setFormError('Date is required.');
      return;
    }

    const payload = {
      test_name: form.test_name.trim(),
      result_value: parseFloat(form.result_value),
      unit: form.unit.trim(),
      test_date: form.test_date,
      reference_range: form.reference_range.trim() || null,
      notes: form.notes.trim() || null,
    };

    setSaving(true);
    try {
      if (editingEntry) {
        await updateLabResult(editingEntry.id, payload);
        setMessage({ type: 'success', text: `Updated "${payload.test_name}"` });
      } else {
        await createLabResult(payload);
        setMessage({ type: 'success', text: `Added "${payload.test_name}"` });
      }
      closeModal();
      loadRecords();
    } catch (err) {
      const detail = err.response?.data?.detail;
      let msg = 'Failed to save record.';
      if (typeof detail === 'string') msg = detail;
      else if (Array.isArray(detail)) msg = detail.map(d => d.msg || JSON.stringify(d)).join(', ');
      setFormError(msg);
    } finally {
      setSaving(false);
    }
  }

  async function confirmDelete() {
    if (!deleteId) return;
    setDeleting(true);
    try {
      await deleteLabResult(deleteId);
      setMessage({ type: 'success', text: 'Record deleted.' });
      setDeleteId(null);
      loadRecords();
    } catch {
      setMessage({ type: 'error', text: 'Failed to delete record.' });
    } finally {
      setDeleting(false);
    }
  }

  // Format date for display
  function displayDate(dateStr) {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  return (
    <div className="page-container">
      <div className="page-header fade-in">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.25rem' }}>
          <div>
            <div className="eyebrow-label">Diagnostic Telemetry &amp; Lab Work</div>
            <h1>Blood Tests &amp; Biomarkers</h1>
            <p>Monitor clinical lab values against calibrated reference ranges to optimize physiological balance.</p>
          </div>
          <button className="btn btn-primary" onClick={openAddModal}>+ Add Custom Record</button>
        </div>
      </div>

      {/* Structured Clinical Biomarker Panels */}
      <div className="glass-card bt-panels-card fade-in">
        <div className="bt-panels-header">
          <h3 style={{ margin: 0, fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            🩸 Essential Clinical Blood Biomarkers
          </h3>
          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
            One-click structured entry with standardized clinical units & reference ranges:
          </p>
        </div>
        <div className="bt-panels-grid">
          {CLINICAL_BLOOD_TESTS.map((test) => {
            const latest = records
              .filter(r => r.test_name.toLowerCase() === test.name.toLowerCase())
              .sort((a, b) => new Date(b.test_date) - new Date(a.test_date))[0];

            return (
              <div key={test.name} className={`bt-panel-item ${latest ? 'bt-panel-item--logged' : ''}`}>
                <div className="bt-panel-item-top">
                  <span className="bt-panel-icon">{test.icon}</span>
                  <div className="bt-panel-info">
                    <strong>{test.name}</strong>
                    <span className="bt-panel-unit">Unit: {test.unit}</span>
                  </div>
                </div>
                <div className="bt-panel-ref">
                  <span>Ref: {test.ref}</span>
                </div>
                {latest ? (
                  <div className="bt-panel-latest">
                    <span>Latest: <strong>{latest.result_value} {latest.unit}</strong></span>
                    <span className="bt-panel-latest-date">({displayDate(latest.test_date)})</span>
                  </div>
                ) : (
                  <div className="bt-panel-desc">{test.desc}</div>
                )}
                <button
                  type="button"
                  className="btn btn-secondary bt-panel-btn"
                  onClick={() => {
                    openAddModal();
                    setForm(prev => ({
                      ...prev,
                      test_name: test.name,
                      unit: test.unit,
                      reference_range: test.ref,
                      notes: test.desc,
                    }));
                  }}
                >
                  {latest ? '⚡ Log New Value' : '+ Enter ' + test.name}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {message.text && (
        <div className={`bt-message bt-message--${message.type} fade-in`}>
          <span>{message.type === 'success' ? '✅' : '⚠️'}</span>
          <span>{message.text}</span>
          <button className="bt-message-close" onClick={() => setMessage({ type: '', text: '' })}>✕</button>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: 'var(--space-2xl)' }}>
          <div className="bt-loading-spinner" />
          <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-md)' }}>Loading records…</p>
        </div>
      ) : records.length === 0 ? (
        <div className="glass-card bt-empty fade-in">
          <div className="bt-empty-icon">💉</div>
          <h3>No blood tests logged yet</h3>
          <p>Start tracking your laboratory results to monitor your biomarkers using the clinical panels above or custom records.</p>
          <button className="btn btn-primary" onClick={openAddModal} style={{ marginTop: '1rem' }}>Log First Test</button>
        </div>
      ) : (
        <div className="glass-card bt-table-container fade-in">
          <table className="bt-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Test Name</th>
                <th>Result</th>
                <th className="hide-mobile">Reference Range</th>
                <th className="hide-mobile">Notes</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {records.map(record => (
                <tr key={record.id}>
                  <td className="bt-cell-date">{displayDate(record.test_date)}</td>
                  <td className="bt-cell-name"><strong>{record.test_name}</strong></td>
                  <td className="bt-cell-result">
                    <span className="bt-value">{record.result_value}</span> <span className="bt-unit">{record.unit}</span>
                  </td>
                  <td className="hide-mobile bt-cell-ref">{record.reference_range || '-'}</td>
                  <td className="hide-mobile bt-cell-notes">{record.notes || '-'}</td>
                  <td className="bt-cell-actions text-right">
                    <button className="bt-icon-btn edit" onClick={() => openEditModal(record)} title="Edit">✏️</button>
                    <button className="bt-icon-btn delete" onClick={() => setDeleteId(record.id)} title="Delete">🗑️</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Add/Edit Modal ─────────────────────────────────────── */}
      {showModal && (
        <div className="bt-modal-overlay" onClick={closeModal}>
          <div className="bt-modal glass-card fade-in" onClick={e => e.stopPropagation()}>
            <div className="bt-modal-header">
              <h2>{editingEntry ? '✏️ Edit Blood Test' : '💉 Add Blood Test'}</h2>
              <button className="bt-modal-close" onClick={closeModal}>✕</button>
            </div>

            {formError && (
              <div className="bt-form-error">
                <span>⚠️</span> {formError}
              </div>
            )}

            {/* Quick Biomarker Presets */}
            {!editingEntry && (
              <div className="bt-preset-section">
                <span className="bt-preset-label">Quick select target biomarker:</span>
                <div className="bt-preset-chips">
                  {CLINICAL_BLOOD_TESTS.map(t => (
                    <button
                      key={t.name}
                      type="button"
                      className={`bt-chip ${form.test_name === t.name ? 'bt-chip--active' : ''}`}
                      onClick={() => setForm(prev => ({
                        ...prev,
                        test_name: t.name,
                        unit: t.unit,
                        reference_range: t.ref,
                        notes: prev.notes || t.desc
                      }))}
                    >
                      {t.icon} {t.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <form onSubmit={handleFormSubmit} className="bt-form">
              <div className="bt-form-row">
                <div className="bt-form-field">
                  <label htmlFor="bt-name">Test Name *</label>
                  <input
                    type="text"
                    id="bt-name"
                    name="test_name"
                    placeholder="e.g. Hemoglobin, LDL"
                    value={form.test_name}
                    onChange={handleFormChange}
                    autoFocus
                  />
                </div>
                <div className="bt-form-field">
                  <label htmlFor="bt-date">Date *</label>
                  <input
                    type="date"
                    id="bt-date"
                    name="test_date"
                    value={form.test_date}
                    onChange={handleFormChange}
                  />
                </div>
              </div>

              <div className="bt-form-row three-cols">
                <div className="bt-form-field">
                  <label htmlFor="bt-value">Result Value *</label>
                  <input
                    type="number"
                    id="bt-value"
                    name="result_value"
                    step="any"
                    placeholder="e.g. 14.5"
                    value={form.result_value}
                    onChange={handleFormChange}
                  />
                </div>
                <div className="bt-form-field">
                  <label htmlFor="bt-unit">Unit *</label>
                  <input
                    type="text"
                    id="bt-unit"
                    name="unit"
                    placeholder="e.g. g/dL, mg/dL"
                    value={form.unit}
                    onChange={handleFormChange}
                  />
                </div>
                <div className="bt-form-field">
                  <label htmlFor="bt-ref">Ref Range</label>
                  <input
                    type="text"
                    id="bt-ref"
                    name="reference_range"
                    placeholder="e.g. 13.8-17.2"
                    value={form.reference_range}
                    onChange={handleFormChange}
                  />
                </div>
              </div>

              <div className="bt-form-field">
                <label htmlFor="bt-notes">Notes</label>
                <textarea
                  id="bt-notes"
                  name="notes"
                  rows="2"
                  placeholder="Fasting, non-fasting, etc..."
                  value={form.notes}
                  onChange={handleFormChange}
                />
              </div>

              <div className="bt-form-actions">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Saving…' : editingEntry ? 'Update' : 'Save Record'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Delete Confirm ─────────────────────────────────────── */}
      {deleteId && (
        <div className="bt-modal-overlay" onClick={() => setDeleteId(null)}>
          <div className="bt-modal bt-modal--small glass-card fade-in" onClick={e => e.stopPropagation()}>
            <div className="bt-delete-content">
              <span style={{ fontSize: '2.5rem' }}>🗑️</span>
              <h3>Delete Record?</h3>
              <p>This action cannot be undone.</p>
              <div className="bt-delete-actions">
                <button className="btn btn-secondary" onClick={() => setDeleteId(null)}>Cancel</button>
                <button className="btn bt-delete-confirm" onClick={confirmDelete} disabled={deleting}>
                  {deleting ? 'Deleting…' : 'Delete'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
