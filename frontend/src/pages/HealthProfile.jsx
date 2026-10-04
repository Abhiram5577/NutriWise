/**
 * HealthProfile — interactive form for viewing and editing the user's health profile.
 * Loads existing data on mount, supports create and update via the API.
 */
import { useState, useEffect } from 'react';
import { getHealthProfile, createHealthProfile, updateHealthProfile } from '../api/healthProfile';
import './HealthProfile.css';

const ACTIVITY_LEVELS = [
  { value: 'sedentary', label: 'Sedentary', desc: 'Little or no exercise' },
  { value: 'light', label: 'Light', desc: '1-3 days/week' },
  { value: 'moderate', label: 'Moderate', desc: '3-5 days/week' },
  { value: 'active', label: 'Active', desc: '6-7 days/week' },
  { value: 'very_active', label: 'Very Active', desc: 'Intense daily exercise' },
];

const DIETARY_PREFERENCES = [
  'omnivore', 'vegetarian', 'vegan', 'pescatarian',
  'keto', 'paleo', 'gluten_free', 'dairy_free', 'other',
];

const GENDERS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
  { value: 'prefer_not_to_say', label: 'Prefer not to say' },
];

const INITIAL_FORM = {
  age: '',
  gender: '',
  height_cm: '',
  weight_kg: '',
  activity_level: '',
  dietary_preference: '',
  allergies: '',
  medical_conditions: '',
  health_goals: '',
};

export default function HealthProfile() {
  const [form, setForm] = useState(INITIAL_FORM);
  const [profileExists, setProfileExists] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    setLoading(true);
    try {
      const data = await getHealthProfile();
      setForm({
        age: data.age ?? '',
        gender: data.gender ?? '',
        height_cm: data.height_cm ?? '',
        weight_kg: data.weight_kg ?? '',
        activity_level: data.activity_level ?? '',
        dietary_preference: data.dietary_preference ?? '',
        allergies: data.allergies ?? '',
        medical_conditions: data.medical_conditions ?? '',
        health_goals: data.health_goals ?? '',
      });
      setProfileExists(true);
    } catch (err) {
      if (err.response?.status === 404) {
        // No profile yet — keep blank form
        setProfileExists(false);
      } else {
        setMessage({ type: 'error', text: 'Failed to load health profile.' });
      }
    } finally {
      setLoading(false);
    }
  }

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setMessage({ type: '', text: '' });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    // Build payload, converting empty strings to null
    const payload = {};
    for (const [key, val] of Object.entries(form)) {
      if (val === '' || val === null) {
        payload[key] = null;
      } else if (key === 'age') {
        payload[key] = parseInt(val, 10);
      } else if (key === 'height_cm' || key === 'weight_kg') {
        payload[key] = parseFloat(val);
      } else {
        payload[key] = val;
      }
    }

    try {
      if (profileExists) {
        await updateHealthProfile(payload);
        setMessage({ type: 'success', text: 'Profile updated successfully!' });
      } else {
        await createHealthProfile(payload);
        setProfileExists(true);
        setMessage({ type: 'success', text: 'Profile created successfully!' });
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      let errorMsg = 'Failed to save profile.';
      if (typeof detail === 'string') {
        errorMsg = detail;
      } else if (Array.isArray(detail)) {
        errorMsg = detail.map((d) => d.msg || d.message || JSON.stringify(d)).join(', ');
      }
      setMessage({ type: 'error', text: errorMsg });
    } finally {
      setSaving(false);
    }
  }

  // Computed BMI
  const bmi =
    form.height_cm && form.weight_kg
      ? (parseFloat(form.weight_kg) / Math.pow(parseFloat(form.height_cm) / 100, 2)).toFixed(1)
      : null;

  function bmiCategory(val) {
    if (!val) return '';
    const n = parseFloat(val);
    if (n < 18.5) return 'Underweight';
    if (n < 25) return 'Normal';
    if (n < 30) return 'Overweight';
    return 'Obese';
  }

  function bmiColor(val) {
    if (!val) return 'var(--text-muted)';
    const n = parseFloat(val);
    if (n < 18.5) return 'var(--accent-amber)';
    if (n < 25) return 'var(--accent-green)';
    if (n < 30) return 'var(--accent-amber)';
    return 'var(--accent-rose)';
  }

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: '4rem' }}>
        <div className="hp-loading-spinner" />
        <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-md)' }}>Loading your health profile…</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header fade-in">
        <div className="eyebrow-label">Biometrics &amp; Metabolic Baseline</div>
        <h1>Health Profile</h1>
        <p>Curate your physical parameters, metabolic activity, and personalized dietary blueprint.</p>
      </div>

      {/* Message banner */}
      {message.text && (
        <div className={`hp-message hp-message--${message.type} fade-in`} id="hp-message">
          <span>{message.type === 'success' ? '✅' : '⚠️'}</span>
          <span>{message.text}</span>
        </div>
      )}

      <div className="hp-layout">
        {/* Left: Form */}
        <form className="glass-card hp-form fade-in fade-in-delay-1" onSubmit={handleSubmit} id="health-profile-form">
          <h2 className="hp-form-title">
            {profileExists ? '✏️ Edit Profile' : '🆕 Create Profile'}
          </h2>

          {/* Bio Section */}
          <div className="hp-section">
            <h3 className="hp-section-title">Biometrics</h3>

            <div className="hp-row">
              <div className="hp-field">
                <label htmlFor="hp-age">Age</label>
                <input
                  type="number"
                  id="hp-age"
                  name="age"
                  min="1"
                  max="150"
                  placeholder="e.g. 25"
                  value={form.age}
                  onChange={handleChange}
                />
              </div>
              <div className="hp-field">
                <label htmlFor="hp-gender">Gender</label>
                <select id="hp-gender" name="gender" value={form.gender} onChange={handleChange}>
                  <option value="">Select gender</option>
                  {GENDERS.map((g) => (
                    <option key={g.value} value={g.value}>{g.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="hp-row">
              <div className="hp-field">
                <label htmlFor="hp-height">Height (cm)</label>
                <input
                  type="number"
                  id="hp-height"
                  name="height_cm"
                  min="1"
                  max="300"
                  step="0.1"
                  placeholder="e.g. 175"
                  value={form.height_cm}
                  onChange={handleChange}
                />
              </div>
              <div className="hp-field">
                <label htmlFor="hp-weight">Weight (kg)</label>
                <input
                  type="number"
                  id="hp-weight"
                  name="weight_kg"
                  min="1"
                  max="700"
                  step="0.1"
                  placeholder="e.g. 70"
                  value={form.weight_kg}
                  onChange={handleChange}
                />
              </div>
            </div>
          </div>

          {/* Lifestyle Section */}
          <div className="hp-section">
            <h3 className="hp-section-title">Lifestyle</h3>

            <div className="hp-field">
              <label htmlFor="hp-activity">Activity Level</label>
              <div className="hp-activity-grid">
                {ACTIVITY_LEVELS.map((level) => (
                  <button
                    key={level.value}
                    type="button"
                    className={`hp-activity-btn ${form.activity_level === level.value ? 'hp-activity-btn--active' : ''}`}
                    onClick={() => {
                      setForm((prev) => ({ ...prev, activity_level: level.value }));
                      setMessage({ type: '', text: '' });
                    }}
                  >
                    <span className="hp-activity-label">{level.label}</span>
                    <span className="hp-activity-desc">{level.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="hp-field">
              <label htmlFor="hp-diet">Dietary Preference</label>
              <select id="hp-diet" name="dietary_preference" value={form.dietary_preference} onChange={handleChange}>
                <option value="">Select preference</option>
                {DIETARY_PREFERENCES.map((d) => (
                  <option key={d} value={d}>{d.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Medical Info & Goals */}
          <div className="hp-section">
            <h3 className="hp-section-title">Medical Info &amp; Goals</h3>
            <div className="hp-field">
              <label htmlFor="hp-medical-conditions">Medical Conditions</label>
              <textarea
                id="hp-medical-conditions"
                name="medical_conditions"
                rows="3"
                placeholder="e.g. diabetes, hypertension"
                value={form.medical_conditions}
                onChange={handleChange}
                maxLength={500}
              />
              <span className="hp-field-hint">Separate multiple conditions with commas</span>
            </div>
            <div className="hp-field">
              <label htmlFor="hp-allergies">Allergies &amp; Intolerances</label>
              <textarea
                id="hp-allergies"
                name="allergies"
                rows="3"
                placeholder="e.g. peanuts, shellfish, gluten"
                value={form.allergies}
                onChange={handleChange}
                maxLength={500}
              />
              <span className="hp-field-hint">Separate multiple items with commas</span>
            </div>
            <div className="hp-field">
              <label htmlFor="hp-health-goals">Health Goals</label>
              <textarea
                id="hp-health-goals"
                name="health_goals"
                rows="3"
                placeholder="e.g. lose 5kg, build muscle, improve stamina"
                value={form.health_goals}
                onChange={handleChange}
                maxLength={500}
              />
              <span className="hp-field-hint">Separate multiple goals with commas</span>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary hp-submit"
            disabled={saving}
            id="hp-submit-btn"
          >
            {saving ? 'Saving…' : profileExists ? 'Update Profile' : 'Create Profile'}
          </button>
        </form>

        {/* Right: Preview Cards */}
        <div className="hp-sidebar fade-in fade-in-delay-2">
          {/* BMI Card */}
          <div className="glass-card hp-bmi-card" id="hp-bmi-card">
            <h3 className="hp-card-title">BMI Calculator</h3>
            {bmi ? (
              <div className="hp-bmi-content">
                <div className="hp-bmi-value" style={{ color: bmiColor(bmi) }}>
                  {bmi}
                </div>
                <div className="hp-bmi-category" style={{ color: bmiColor(bmi) }}>
                  {bmiCategory(bmi)}
                </div>
                <div className="hp-bmi-bar">
                  <div
                    className="hp-bmi-indicator"
                    style={{
                      left: `${Math.min(Math.max(((parseFloat(bmi) - 15) / 25) * 100, 0), 100)}%`,
                      background: bmiColor(bmi),
                    }}
                  />
                </div>
                <div className="hp-bmi-labels">
                  <span>15</span><span>18.5</span><span>25</span><span>30</span><span>40</span>
                </div>
              </div>
            ) : (
              <p className="hp-card-empty">Enter height and weight to see your BMI</p>
            )}
          </div>

          {/* Profile Summary Card */}
          <div className="glass-card hp-summary-card" id="hp-summary-card">
            <h3 className="hp-card-title">Profile Summary</h3>
            <div className="hp-summary-items">
              <SummaryItem icon="🎂" label="Age" value={form.age ? `${form.age} years` : '—'} />
              <SummaryItem icon="⚧" label="Gender" value={form.gender ? form.gender.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : '—'} />
              <SummaryItem icon="📏" label="Height" value={form.height_cm ? `${form.height_cm} cm` : '—'} />
              <SummaryItem icon="⚖️" label="Weight" value={form.weight_kg ? `${form.weight_kg} kg` : '—'} />
              <SummaryItem icon="🏃" label="Activity" value={form.activity_level ? form.activity_level.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : '—'} />
              <SummaryItem icon="🥬" label="Diet" value={form.dietary_preference ? form.dietary_preference.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : '—'} />
              <SummaryItem icon="⚠️" label="Allergies" value={form.allergies || '—'} />
              <SummaryItem icon="🏥" label="Conditions" value={form.medical_conditions || '—'} />
              <SummaryItem icon="🎯" label="Goals" value={form.health_goals || '—'} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SummaryItem({ icon, label, value }) {
  return (
    <div className="hp-summary-item">
      <span className="hp-summary-icon">{icon}</span>
      <div>
        <div className="hp-summary-label">{label}</div>
        <div className="hp-summary-value">{value}</div>
      </div>
    </div>
  );
}
