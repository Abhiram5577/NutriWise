/**
 * FoodDiary — full CRUD page for food diary entries.
 * Integrated with Nutrition API for food search.
 */
import { useState, useEffect, useCallback } from 'react';
import { getFoodEntriesByDate, createFoodEntry, updateFoodEntry, deleteFoodEntry } from '../api/foodDiary';
import { searchNutrition } from '../api/nutrition';
import './FoodDiary.css';

const MEAL_TYPES = ['breakfast', 'lunch', 'dinner', 'snack'];

const MEAL_ICONS = {
  breakfast: '🌅',
  lunch: '☀️',
  dinner: '🌙',
  snack: '🍎',
};

const EMPTY_FORM = {
  food_name: '',
  quantity_g: '',
  meal_type: 'breakfast',
  notes: '',
  calories: '',
  protein_g: '',
  carbs_g: '',
  fat_g: '',
  fiber_g: '',
};

function todayStr() {
  return new Date().toISOString().split('T')[0];
}

export default function FoodDiary() {
  const [selectedDate, setSelectedDate] = useState(todayStr());
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  // Nutrition API Search State
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState('');
  const [selectedNutrition, setSelectedNutrition] = useState(null);

  // Delete confirm
  const [deleteId, setDeleteId] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const loadEntries = useCallback(async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });
    try {
      const data = await getFoodEntriesByDate(selectedDate);
      setEntries(data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load food entries.' });
    } finally {
      setLoading(false);
    }
  }, [selectedDate]);

  useEffect(() => {
    loadEntries();
  }, [loadEntries]);

  // Group entries by meal type
  function groupByMeal(items) {
    const groups = {};
    for (const meal of MEAL_TYPES) {
      groups[meal] = items.filter((e) => e.meal_type === meal);
    }
    return groups;
  }

  // Totals
  function totals(items) {
    return items.reduce(
      (acc, e) => ({
        calories: acc.calories + (e.calories || 0),
        protein: acc.protein + (e.protein_g || 0),
        carbs: acc.carbs + (e.carbs_g || 0),
        fat: acc.fat + (e.fat_g || 0),
        fiber: acc.fiber + (e.fiber_g || 0),
      }),
      { calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0 }
    );
  }

  // ── Modal handlers ───────────────────────────────────────────
  function openAddModal(mealType = 'breakfast') {
    setEditingEntry(null);
    setForm({ ...EMPTY_FORM, meal_type: mealType });
    setFormError('');
    setSearchQuery('');
    setSearchResults([]);
    setSearchError('');
    setSelectedNutrition(null);
    setShowModal(true);
  }

  function openEditModal(entry) {
    setEditingEntry(entry);
    setForm({
      food_name: entry.food_name,
      quantity_g: entry.quantity_g?.toString() ?? '',
      meal_type: entry.meal_type,
      notes: entry.notes ?? '',
      calories: entry.calories?.toString() ?? '',
      protein_g: entry.protein_g?.toString() ?? '',
      carbs_g: entry.carbs_g?.toString() ?? '',
      fat_g: entry.fat_g?.toString() ?? '',
      fiber_g: entry.fiber_g?.toString() ?? '',
    });
    setFormError('');
    setSearchQuery('');
    setSearchResults([]);
    setSearchError('');
    setSelectedNutrition(null);
    setShowModal(true);
  }

  function closeModal() {
    setShowModal(false);
    setEditingEntry(null);
    setForm(EMPTY_FORM);
    setFormError('');
    setSearchResults([]);
  }

  // ── Nutrition API Integration ────────────────────────────────
  async function handleSearch(e) {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setSearchError('');
    setSearchResults([]);
    
    try {
      const results = await searchNutrition(searchQuery, 8);
      setSearchResults(results);
      if (results.length === 0) {
        setSearchError('No foods found. Try a different search or enter manually.');
      }
    } catch (err) {
      setSearchError(err.response?.data?.detail || 'Failed to search nutrition database. Please enter manually.');
    } finally {
      setIsSearching(false);
    }
  }

  function selectSearchResult(food) {
    setSelectedNutrition(food);
    
    // Auto-calculate for a default 100g serving initially
    const qty = 100;
    
    setForm(prev => ({
      ...prev,
      food_name: food.food_name,
      quantity_g: qty.toString(),
      calories: food.calories_100g.toFixed(1),
      protein_g: food.protein_100g.toFixed(1),
      carbs_g: food.carbs_100g.toFixed(1),
      fat_g: food.fat_100g.toFixed(1),
      fiber_g: food.fiber_100g.toFixed(1),
    }));
    
    setSearchResults([]);
    setSearchQuery('');
    setSearchError('');
  }

  // Recalculate nutrition when quantity changes (if a DB item is selected)
  function handleFormChange(e) {
    const { name, value } = e.target;
    
    setForm(prev => {
      const updated = { ...prev, [name]: value };
      
      // If we are changing quantity AND we have a selected nutrition base, auto-recalculate
      if (name === 'quantity_g' && selectedNutrition && value) {
        const qty = parseFloat(value);
        if (!isNaN(qty) && qty > 0) {
          const ratio = qty / 100;
          updated.calories = (selectedNutrition.calories_100g * ratio).toFixed(1);
          updated.protein_g = (selectedNutrition.protein_100g * ratio).toFixed(1);
          updated.carbs_g = (selectedNutrition.carbs_100g * ratio).toFixed(1);
          updated.fat_g = (selectedNutrition.fat_100g * ratio).toFixed(1);
          updated.fiber_g = (selectedNutrition.fiber_100g * ratio).toFixed(1);
        }
      }
      
      return updated;
    });
    setFormError('');
  }

  async function handleFormSubmit(e) {
    e.preventDefault();
    setFormError('');

    if (!form.food_name.trim()) {
      setFormError('Food name is required.');
      return;
    }
    if (!form.quantity_g || parseFloat(form.quantity_g) <= 0) {
      setFormError('Quantity must be greater than 0.');
      return;
    }

    const payload = {
      food_name: form.food_name.trim(),
      quantity_g: parseFloat(form.quantity_g),
      meal_type: form.meal_type,
      entry_date: selectedDate,
    };

    if (form.notes.trim()) payload.notes = form.notes.trim();
    if (form.calories) payload.calories = parseFloat(form.calories);
    if (form.protein_g) payload.protein_g = parseFloat(form.protein_g);
    if (form.carbs_g) payload.carbs_g = parseFloat(form.carbs_g);
    if (form.fat_g) payload.fat_g = parseFloat(form.fat_g);
    if (form.fiber_g) payload.fiber_g = parseFloat(form.fiber_g);

    setSaving(true);
    try {
      if (editingEntry) {
        await updateFoodEntry(editingEntry.id, payload);
        setMessage({ type: 'success', text: `Updated "${payload.food_name}"` });
      } else {
        await createFoodEntry(payload);
        setMessage({ type: 'success', text: `Added "${payload.food_name}"` });
      }
      closeModal();
      loadEntries();
    } catch (err) {
      const detail = err.response?.data?.detail;
      let msg = 'Failed to save entry.';
      if (typeof detail === 'string') msg = detail;
      else if (Array.isArray(detail)) msg = detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
      setFormError(msg);
    } finally {
      setSaving(false);
    }
  }

  // ── Delete handler ───────────────────────────────────────────
  async function confirmDelete() {
    if (!deleteId) return;
    setDeleting(true);
    try {
      await deleteFoodEntry(deleteId);
      setMessage({ type: 'success', text: 'Entry deleted.' });
      setDeleteId(null);
      loadEntries();
    } catch {
      setMessage({ type: 'error', text: 'Failed to delete entry.' });
    } finally {
      setDeleting(false);
    }
  }

  // ── Date navigation ──────────────────────────────────────────
  function shiftDate(days) {
    const d = new Date(selectedDate);
    d.setDate(d.getDate() + days);
    setSelectedDate(d.toISOString().split('T')[0]);
  }

  const isToday = selectedDate === todayStr();
  const grouped = groupByMeal(entries);
  const dayTotals = totals(entries);

  function displayDate(dateStr) {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  }

  return (
    <div className="page-container">
      <div className="page-header fade-in">
        <div className="eyebrow-label">Dietary Intake &amp; Balance</div>
        <h1>Food Diary</h1>
        <p>Record daily meals and calibrate whole-food nutrition with precision.</p>
      </div>

      {message.text && (
        <div className={`fd-message fd-message--${message.type} fade-in`} id="fd-message">
          <span>{message.type === 'success' ? '✅' : '⚠️'}</span>
          <span>{message.text}</span>
          <button className="fd-message-close" onClick={() => setMessage({ type: '', text: '' })}>✕</button>
        </div>
      )}

      {/* Date Picker Bar */}
      <div className="glass-card fd-date-bar fade-in fade-in-delay-1" id="fd-date-bar">
        <button className="fd-date-arrow" onClick={() => shiftDate(-1)} title="Previous day">‹</button>
        <div className="fd-date-center">
          <input type="date" className="fd-date-input" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)} max={todayStr()} id="fd-date-picker" />
          <div className="fd-date-display">{displayDate(selectedDate)}</div>
          {isToday && <span className="badge badge-success fd-today-badge">Today</span>}
        </div>
        <button className="fd-date-arrow" onClick={() => shiftDate(1)} disabled={isToday} title="Next day">›</button>
      </div>

      {/* Daily Summary */}
      <div className="fd-summary-row fade-in fade-in-delay-2">
        <div className="glass-card fd-summary-card">
          <div className="fd-summary-value" style={{ color: 'var(--accent-botanical)' }}>{Math.round(dayTotals.calories)}</div>
          <div className="fd-summary-label">Calories</div>
        </div>
        <div className="glass-card fd-summary-card">
          <div className="fd-summary-value" style={{ color: 'var(--accent-gold-dark)' }}>{dayTotals.protein.toFixed(1)}g</div>
          <div className="fd-summary-label">Protein</div>
        </div>
        <div className="glass-card fd-summary-card">
          <div className="fd-summary-value" style={{ color: 'var(--accent-sage)' }}>{dayTotals.carbs.toFixed(1)}g</div>
          <div className="fd-summary-label">Carbs</div>
        </div>
        <div className="glass-card fd-summary-card">
          <div className="fd-summary-value" style={{ color: 'var(--accent-terracotta)' }}>{dayTotals.fat.toFixed(1)}g</div>
          <div className="fd-summary-label">Fat</div>
        </div>
        <div className="glass-card fd-summary-card">
          <div className="fd-summary-value" style={{ color: 'var(--accent-slate)' }}>{dayTotals.fiber.toFixed(1)}g</div>
          <div className="fd-summary-label">Fiber</div>
        </div>
      </div>

      {/* Loading */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: 'var(--space-2xl)' }}>
          <div className="fd-loading-spinner" />
          <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-md)' }}>Loading entries…</p>
        </div>
      ) : (
        <div className="fd-meals fade-in fade-in-delay-3">
          {MEAL_TYPES.map((meal) => (
            <div key={meal} className="glass-card fd-meal-group" id={`fd-meal-${meal}`}>
              <div className="fd-meal-header">
                <div className="fd-meal-title">
                  <span className="fd-meal-icon">{MEAL_ICONS[meal]}</span>
                  <span>{meal.charAt(0).toUpperCase() + meal.slice(1)}</span>
                  {grouped[meal].length > 0 && (
                    <span className="badge badge-success" style={{ marginLeft: '0.5rem' }}>{grouped[meal].length}</span>
                  )}
                </div>
                <button className="btn btn-secondary fd-add-btn" onClick={() => openAddModal(meal)} id={`fd-add-${meal}`}>
                  + Add
                </button>
              </div>

              {grouped[meal].length === 0 ? (
                <div className="fd-empty-meal">
                  No {meal} entries yet.{' '}
                  <button className="fd-empty-add" onClick={() => openAddModal(meal)}>Add food</button>
                </div>
              ) : (
                <div className="fd-entry-list">
                  {grouped[meal].map((entry) => (
                    <div key={entry.id} className="fd-entry" id={`fd-entry-${entry.id}`}>
                      <div className="fd-entry-main">
                        <div className="fd-entry-name">{entry.food_name}</div>
                        <div className="fd-entry-meta">
                          <span>{entry.quantity_g}g</span>
                          {entry.calories != null && <span>• {Math.round(entry.calories)} kcal</span>}
                          {entry.protein_g != null && <span>• P: {entry.protein_g}g</span>}
                          {entry.carbs_g != null && <span>• C: {entry.carbs_g}g</span>}
                          {entry.fat_g != null && <span>• F: {entry.fat_g}g</span>}
                        </div>
                        {entry.notes && <div className="fd-entry-notes">📝 {entry.notes}</div>}
                      </div>
                      <div className="fd-entry-actions">
                        <button className="fd-action-btn fd-action-edit" onClick={() => openEditModal(entry)} title="Edit">✏️</button>
                        <button className="fd-action-btn fd-action-delete" onClick={() => setDeleteId(entry.id)} title="Delete">🗑️</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── Add/Edit Modal ─────────────────────────────────────── */}
      {showModal && (
        <div className="fd-modal-overlay" onClick={closeModal}>
          <div className="fd-modal glass-card fade-in" onClick={(e) => e.stopPropagation()} id="fd-modal">
            <div className="fd-modal-header">
              <h2>{editingEntry ? '✏️ Edit Food' : '🍽️ Add Food'}</h2>
              <button className="fd-modal-close" onClick={closeModal}>✕</button>
            </div>

            {formError && (
              <div className="fd-form-error">
                <span>⚠️</span> {formError}
              </div>
            )}

            {/* Nutrition Search UI (Only on Add, not Edit to keep it simple) */}
            {!editingEntry && (
              <div className="fd-search-section">
                <form onSubmit={handleSearch} className="fd-search-form">
                  <input
                    type="text"
                    placeholder="Search food database (e.g., Apple, Chicken)..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="fd-search-input"
                  />
                  <button type="submit" className="btn btn-secondary fd-search-btn" disabled={isSearching || !searchQuery.trim()}>
                    {isSearching ? '🔍...' : 'Search'}
                  </button>
                </form>

                {searchError && <div className="fd-search-error">{searchError}</div>}

                {searchResults.length > 0 && (
                  <div className="fd-search-results fade-in">
                    {searchResults.map((res, i) => (
                      <div key={i} className="fd-search-item" onClick={() => selectSearchResult(res)}>
                        {res.image_url ? (
                          <img src={res.image_url} alt={res.food_name} className="fd-search-img" />
                        ) : (
                          <div className="fd-search-img-placeholder">🍽️</div>
                        )}
                        <div className="fd-search-item-info">
                          <div className="fd-search-item-name">{res.food_name}</div>
                          <div className="fd-search-item-meta">
                            100g • {Math.round(res.calories_100g)} kcal • P: {Math.round(res.protein_100g)}g
                          </div>
                        </div>
                        <button className="fd-search-select">Select</button>
                      </div>
                    ))}
                  </div>
                )}
                
                {selectedNutrition && (
                  <div className="fd-search-selected">
                    <span style={{color: 'var(--accent-green)'}}>✓</span> Using data for: <strong>{selectedNutrition.food_name}</strong>
                    <button type="button" className="fd-clear-selection" onClick={() => {
                      setSelectedNutrition(null);
                      setForm({ ...EMPTY_FORM, meal_type: form.meal_type });
                    }}>Clear</button>
                  </div>
                )}
                
                <div className="fd-search-divider">
                  <span>OR ENTER MANUALLY</span>
                </div>
              </div>
            )}

            <form onSubmit={handleFormSubmit} className="fd-form">
              <div className="fd-form-row">
                <div className="fd-form-field fd-form-field--wide">
                  <label htmlFor="fd-food-name">Food Name *</label>
                  <input
                    type="text"
                    id="fd-food-name"
                    name="food_name"
                    placeholder="e.g. Grilled Chicken Breast"
                    value={form.food_name}
                    onChange={handleFormChange}
                    maxLength={255}
                    autoFocus={!!editingEntry}
                  />
                </div>
              </div>

              <div className="fd-form-row">
                <div className="fd-form-field">
                  <label htmlFor="fd-quantity">Quantity (g) * {selectedNutrition && <span className="fd-auto-calc-hint">(Auto-calculates)</span>}</label>
                  <input
                    type="number"
                    id="fd-quantity"
                    name="quantity_g"
                    min="0.1"
                    max="10000"
                    step="0.1"
                    placeholder="e.g. 150"
                    value={form.quantity_g}
                    onChange={handleFormChange}
                  />
                </div>
                <div className="fd-form-field">
                  <label htmlFor="fd-meal-type">Meal Type *</label>
                  <select id="fd-meal-type" name="meal_type" value={form.meal_type} onChange={handleFormChange}>
                    {MEAL_TYPES.map((m) => (
                      <option key={m} value={m}>
                        {MEAL_ICONS[m]} {m.charAt(0).toUpperCase() + m.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Nutrition fields */}
              <div className="fd-form-section">
                <h3 className="fd-form-section-title">Nutrition (optional)</h3>
                <div className="fd-form-grid">
                  <div className="fd-form-field">
                    <label htmlFor="fd-calories">Calories</label>
                    <input type="number" id="fd-calories" name="calories" min="0" step="0.1" placeholder="kcal" value={form.calories} onChange={handleFormChange} />
                  </div>
                  <div className="fd-form-field">
                    <label htmlFor="fd-protein">Protein (g)</label>
                    <input type="number" id="fd-protein" name="protein_g" min="0" step="0.1" placeholder="g" value={form.protein_g} onChange={handleFormChange} />
                  </div>
                  <div className="fd-form-field">
                    <label htmlFor="fd-carbs">Carbs (g)</label>
                    <input type="number" id="fd-carbs" name="carbs_g" min="0" step="0.1" placeholder="g" value={form.carbs_g} onChange={handleFormChange} />
                  </div>
                  <div className="fd-form-field">
                    <label htmlFor="fd-fat">Fat (g)</label>
                    <input type="number" id="fd-fat" name="fat_g" min="0" step="0.1" placeholder="g" value={form.fat_g} onChange={handleFormChange} />
                  </div>
                  <div className="fd-form-field">
                    <label htmlFor="fd-fiber">Fiber (g)</label>
                    <input type="number" id="fd-fiber" name="fiber_g" min="0" step="0.1" placeholder="g" value={form.fiber_g} onChange={handleFormChange} />
                  </div>
                </div>
              </div>

              {/* Notes */}
              <div className="fd-form-field">
                <label htmlFor="fd-notes">Notes</label>
                <textarea id="fd-notes" name="notes" rows="2" placeholder="Any additional notes…" value={form.notes} onChange={handleFormChange} maxLength={500} />
              </div>

              <div className="fd-form-actions">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving} id="fd-submit-btn">
                  {saving ? 'Saving…' : editingEntry ? 'Update' : 'Add Food'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Delete Confirm Modal ───────────────────────────────── */}
      {deleteId && (
        <div className="fd-modal-overlay" onClick={() => setDeleteId(null)}>
          <div className="fd-modal fd-modal--small glass-card fade-in" onClick={(e) => e.stopPropagation()} id="fd-delete-modal">
            <div className="fd-delete-content">
              <span style={{ fontSize: '2.5rem' }}>🗑️</span>
              <h3>Delete Entry?</h3>
              <p>This action cannot be undone.</p>
              <div className="fd-delete-actions">
                <button className="btn btn-secondary" onClick={() => setDeleteId(null)}>Cancel</button>
                <button className="btn fd-delete-confirm" onClick={confirmDelete} disabled={deleting}>
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
