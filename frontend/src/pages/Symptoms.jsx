import { useState, useEffect, useCallback } from 'react';
import { getSymptoms, createSymptom, updateSymptom, deleteSymptom } from '../api/symptoms';
import './Symptoms.css';

const SEVERITY_LEVELS = ['mild', 'moderate', 'severe'];

const SEVERITY_ICONS = {
  mild: '🟢',
  moderate: '🟡',
  severe: '🔴',
};

// Target clinical symptom assessment checklist
export const QUESTIONNAIRE_SYMPTOMS = [
  { name: 'Fatigue', icon: '🔋', category: 'Energy & Vitality', desc: 'Feeling unusually tired, lethargic, or exhausted' },
  { name: 'Hair loss', icon: '💇', category: 'Dermatological', desc: 'Excessive shedding, thinning, or brittle hair' },
  { name: 'Skin conditions', icon: '✨', category: 'Dermatological', desc: 'Dryness, eczema, unusual rashes, or slow healing' },
  { name: 'Muscle weakness', icon: '💪', category: 'Musculoskeletal', desc: 'Reduced strength, cramps, or muscle aches' },
  { name: 'Mood-related symptoms', icon: '🧠', category: 'Neurological & Mental', desc: 'Brain fog, irritability, anxiety, or low mood' },
];

const EMPTY_FORM = {
  symptom_name: '',
  severity: 'mild',
  symptom_date: new Date().toISOString().split('T')[0],
  notes: '',
};

export default function Symptoms() {
  const [symptoms, setSymptoms] = useState([]);
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

  const loadSymptoms = useCallback(async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });
    try {
      const data = await getSymptoms();
      setSymptoms(data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load symptoms.' });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSymptoms();
  }, [loadSymptoms]);

  function openAddModal() {
    setEditingEntry(null);
    setForm({ ...EMPTY_FORM, symptom_date: new Date().toISOString().split('T')[0] });
    setFormError('');
    setShowModal(true);
  }

  function openEditModal(entry) {
    setEditingEntry(entry);
    setForm({
      symptom_name: entry.symptom_name,
      severity: entry.severity,
      symptom_date: entry.symptom_date,
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

    if (!form.symptom_name.trim()) {
      setFormError('Symptom name is required.');
      return;
    }
    if (!form.symptom_date) {
      setFormError('Date is required.');
      return;
    }

    const payload = {
      symptom_name: form.symptom_name.trim(),
      severity: form.severity,
      symptom_date: form.symptom_date,
      notes: form.notes.trim() || null,
    };

    setSaving(true);
    try {
      if (editingEntry) {
        await updateSymptom(editingEntry.id, payload);
        setMessage({ type: 'success', text: `Updated "${payload.symptom_name}"` });
      } else {
        await createSymptom(payload);
        setMessage({ type: 'success', text: `Added "${payload.symptom_name}"` });
      }
      closeModal();
      loadSymptoms();
    } catch (err) {
      const detail = err.response?.data?.detail;
      let msg = 'Failed to save entry.';
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
      await deleteSymptom(deleteId);
      setMessage({ type: 'success', text: 'Entry deleted.' });
      setDeleteId(null);
      loadSymptoms();
    } catch {
      setMessage({ type: 'error', text: 'Failed to delete entry.' });
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
            <div className="eyebrow-label">Deficiency Indicators &amp; Correlation</div>
            <h1>Symptom Log</h1>
            <p>Track physiological signals over time to uncover dietary triggers and nutritional imbalances.</p>
          </div>
          <button className="btn btn-primary" onClick={openAddModal}>+ Add Custom Symptom</button>
        </div>
      </div>

      {/* Structured Clinical Questionnaire Assessment Section */}
      <div className="glass-card symp-questionnaire-card fade-in">
        <div className="symp-q-header">
          <div>
            <h3 style={{ margin: 0, fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              📋 Clinical Deficiency Symptom Assessment
            </h3>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
              Quickly assess common nutritional deficiency warning signs:
            </p>
          </div>
        </div>
        <div className="symp-q-grid">
          {QUESTIONNAIRE_SYMPTOMS.map((q) => {
            const isLogged = symptoms.some(s => s.symptom_name.toLowerCase() === q.name.toLowerCase());
            return (
              <div key={q.name} className={`symp-q-item ${isLogged ? 'symp-q-item--logged' : ''}`}>
                <div className="symp-q-item-top">
                  <span className="symp-q-icon">{q.icon}</span>
                  <div className="symp-q-info">
                    <strong>{q.name}</strong>
                    <span className="symp-q-category">{q.category}</span>
                  </div>
                </div>
                <p className="symp-q-desc">{q.desc}</p>
                <button
                  type="button"
                  className="btn btn-secondary symp-q-btn"
                  onClick={() => {
                    openAddModal();
                    setForm(prev => ({ ...prev, symptom_name: q.name, notes: q.desc }));
                  }}
                >
                  {isLogged ? '⚡ Log Again' : '+ Assess & Log'}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {message.text && (
        <div className={`symp-message symp-message--${message.type} fade-in`}>
          <span>{message.type === 'success' ? '✅' : '⚠️'}</span>
          <span>{message.text}</span>
          <button className="symp-message-close" onClick={() => setMessage({ type: '', text: '' })}>✕</button>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: 'var(--space-2xl)' }}>
          <div className="symp-loading-spinner" />
          <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-md)' }}>Loading symptoms…</p>
        </div>
      ) : symptoms.length === 0 ? (
        <div className="glass-card symp-empty fade-in">
          <div className="symp-empty-icon">🤒</div>
          <h3>No symptoms logged yet</h3>
          <p>Start tracking your symptoms using the clinical questionnaire above or add a custom symptom.</p>
          <button className="btn btn-primary" onClick={openAddModal} style={{ marginTop: '1rem' }}>Log First Symptom</button>
        </div>
      ) : (
        <div className="symp-list fade-in">
          {symptoms.map(symptom => (
            <div key={symptom.id} className="glass-card symp-card">
              <div className="symp-card-header">
                <div className="symp-card-title">
                  <span className="symp-icon">{SEVERITY_ICONS[symptom.severity]}</span>
                  <span>{symptom.symptom_name}</span>
                </div>
                <div className="symp-card-date">{displayDate(symptom.symptom_date)}</div>
              </div>
              <div className="symp-card-body">
                <span className={`badge badge-${symptom.severity === 'severe' ? 'error' : symptom.severity === 'moderate' ? 'warning' : 'success'}`}>
                  {symptom.severity.toUpperCase()}
                </span>
                {symptom.notes && <p className="symp-card-notes">{symptom.notes}</p>}
              </div>
              <div className="symp-card-actions">
                <button className="symp-action-btn symp-action-edit" onClick={() => openEditModal(symptom)} title="Edit">✏️ Edit</button>
                <button className="symp-action-btn symp-action-delete" onClick={() => setDeleteId(symptom.id)} title="Delete">🗑️ Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="symp-modal-overlay" onClick={closeModal}>
          <div className="symp-modal glass-card fade-in" onClick={e => e.stopPropagation()}>
            <div className="symp-modal-header">
              <h2>{editingEntry ? '✏️ Edit Symptom' : '🤒 Add Symptom'}</h2>
              <button className="symp-modal-close" onClick={closeModal}>✕</button>
            </div>

            {formError && (
              <div className="symp-form-error">
                <span>⚠️</span> {formError}
              </div>
            )}

            {/* Quick Presets for Target Symptoms */}
            {!editingEntry && (
              <div className="symp-preset-section">
                <span className="symp-preset-label">Quick select target symptom:</span>
                <div className="symp-preset-chips">
                  {QUESTIONNAIRE_SYMPTOMS.map(item => (
                    <button
                      key={item.name}
                      type="button"
                      className={`symp-chip ${form.symptom_name === item.name ? 'symp-chip--active' : ''}`}
                      onClick={() => setForm(prev => ({ ...prev, symptom_name: item.name, notes: prev.notes || item.desc }))}
                    >
                      {item.icon} {item.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <form onSubmit={handleFormSubmit} className="symp-form">
              <div className="symp-form-field">
                <label htmlFor="symp-name">Symptom Name *</label>
                <input
                  type="text"
                  id="symp-name"
                  name="symptom_name"
                  placeholder="e.g. Fatigue, Muscle weakness"
                  value={form.symptom_name}
                  onChange={handleFormChange}
                  autoFocus
                />
              </div>

              <div className="symp-form-row">
                <div className="symp-form-field">
                  <label htmlFor="symp-severity">Severity *</label>
                  <select id="symp-severity" name="severity" value={form.severity} onChange={handleFormChange}>
                    {SEVERITY_LEVELS.map(s => (
                      <option key={s} value={s}>
                        {SEVERITY_ICONS[s]} {s.charAt(0).toUpperCase() + s.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="symp-form-field">
                  <label htmlFor="symp-date">Date *</label>
                  <input
                    type="date"
                    id="symp-date"
                    name="symptom_date"
                    value={form.symptom_date}
                    onChange={handleFormChange}
                  />
                </div>
              </div>

              <div className="symp-form-field">
                <label htmlFor="symp-notes">Notes</label>
                <textarea
                  id="symp-notes"
                  name="notes"
                  rows="3"
                  placeholder="Additional context or triggers..."
                  value={form.notes}
                  onChange={handleFormChange}
                />
              </div>

              <div className="symp-form-actions">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Saving…' : editingEntry ? 'Update' : 'Save Symptom'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deleteId && (
        <div className="symp-modal-overlay" onClick={() => setDeleteId(null)}>
          <div className="symp-modal symp-modal--small glass-card fade-in" onClick={e => e.stopPropagation()}>
            <div className="symp-delete-content">
              <span style={{ fontSize: '2.5rem' }}>🗑️</span>
              <h3>Delete Symptom?</h3>
              <p>This action cannot be undone.</p>
              <div className="symp-delete-actions">
                <button className="btn btn-secondary" onClick={() => setDeleteId(null)}>Cancel</button>
                <button className="btn symp-delete-confirm" onClick={confirmDelete} disabled={deleting}>
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
