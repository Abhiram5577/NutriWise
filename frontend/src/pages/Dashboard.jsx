import { Link } from 'react-router-dom';
import HealthStatus from '../components/HealthStatus';
import './Dashboard.css';

/**
 * Dashboard — Editorial Wellness & Nutrition Intelligence Hub.
 * Features an asymmetric editorial hero, lifestyle compositions, biomarker stories,
 * live system telemetry, and structured feature suites.
 */
export default function Dashboard() {
  const features = [
    {
      num: '01',
      icon: '🌿',
      title: 'Food Diary',
      description: 'Track artisanal meals with granular macro and micronutrient calibration.',
      status: 'Ready',
      path: '/food-diary',
      cta: 'Log Daily Meal',
    },
    {
      num: '02',
      icon: '🥑',
      title: 'Health Profile',
      description: 'Record biometric markers, dietary preferences, and metabolic requirements.',
      status: 'Ready',
      path: '/health-profile',
      cta: 'Update Biometrics',
    },
    {
      num: '03',
      icon: '🩸',
      title: 'Lab Results',
      description: 'Monitor clinical blood panels: vitamin D3, B12, iron saturation, and calcium.',
      status: 'Ready',
      path: '/blood-tests',
      cta: 'Review Blood Work',
    },
    {
      num: '04',
      icon: '✨',
      title: 'Symptom Tracker',
      description: 'Correlate physical symptoms with dietary patterns to identify food triggers.',
      status: 'Ready',
      path: '/symptoms',
      cta: 'Record Symptoms',
    },
    {
      num: '05',
      icon: '🔐',
      title: 'User Auth',
      description: 'Encrypted JWT authentication securing your personalized clinical data.',
      status: 'Ready',
      path: '/login',
      cta: 'Manage Account',
    },
    {
      num: '06',
      icon: '🌱',
      title: 'AI Insights',
      description: 'Predictive machine intelligence tailored to your unique metabolic profile.',
      status: 'Future',
      path: '#',
      cta: 'Preview Protocol',
    },
  ];

  return (
    <div className="page-container">
      {/* ── Editorial Hero (Asymmetric 2-Column) ── */}
      <section className="editorial-hero fade-in" id="dashboard-hero">
        <div className="hero-content">
          <div className="eyebrow-label">Clinical Wellness &amp; Metabolic Balance</div>
          <h1 className="hero-title">
            Mindful Nourishment, <em>Measured with Precision.</em>
          </h1>
          <p className="hero-description">
            NutriWise bridges organic whole-food nutrition with diagnostic biomarker intelligence — 
            empowering you to align dietary choices with cellular longevity.
          </p>
          <div className="hero-actions">
            <Link to="/food-diary" className="btn btn-primary" id="hero-cta-diary">
              Log Today's Meal <span>→</span>
            </Link>
            <Link to="/blood-tests" className="btn btn-secondary" id="hero-cta-labs">
              Explore Lab Markers
            </Link>
          </div>
          <div className="hero-meta-bar">
            <div className="hero-meta-item">
              <span className="hero-meta-dot"></span>
              <span>40+ Micronutrients</span>
            </div>
            <div className="hero-meta-item">
              <span className="hero-meta-dot"></span>
              <span>Clinical Reference Ranges</span>
            </div>
            <div className="hero-meta-item">
              <span className="hero-meta-dot"></span>
              <span>Holistic Correlation</span>
            </div>
          </div>
        </div>

        <div className="hero-visual-wrapper fade-in fade-in-delay-1">
          <div className="hero-image-frame">
            <img 
              src="/assets/hero_wellness.jpg" 
              alt="Editorial botanical nourishment and organic ingredients" 
              className="hero-img"
              loading="lazy"
            />
          </div>
          <div className="hero-floating-badge" id="hero-floating-badge">
            <div className="floating-badge-icon">🌿</div>
            <div className="floating-badge-text">
              <h4>Metabolic Harmony</h4>
              <p>Real-time dietary feedback mapped to your personalized wellness blueprint.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Editorial Full-Width Statement ── */}
      <section className="editorial-statement-section fade-in fade-in-delay-2" id="editorial-quote-banner">
        <blockquote className="statement-quote">
          “Food is not merely caloric fuel — it is biological information that informs your vitality, immune resilience, and metabolic state.”
        </blockquote>
        <span className="statement-author">The NutriWise Philosophy</span>
      </section>

      {/* ── Section 1: Storytelling (Image + Text Asymmetric Layout) ── */}
      <section className="editorial-story-section fade-in fade-in-delay-2" id="biomarker-story-section">
        <div className="story-image-frame">
          <img 
            src="/assets/biomarkers.jpg" 
            alt="Botanical herbal infusions and clinical wellness still life" 
            className="story-img"
            loading="lazy"
          />
        </div>
        <div className="story-content">
          <div className="eyebrow-label eyebrow-label--forest">Biomarker Synergy</div>
          <h2>Connect Symptoms with Nutritional Chemistry</h2>
          <p>
            By logging micronutrient density alongside clinical blood test values (such as Vitamin D3, 
            Ferritin, and Calcium), NutriWise helps uncover hidden deficiencies before they manifest as fatigue or inflammation.
          </p>
          <div className="biomarker-pills">
            <span className="biomarker-chip"><span className="biomarker-chip-dot"></span> Vitamin D3 (25-OH)</span>
            <span className="biomarker-chip"><span className="biomarker-chip-dot"></span> Vitamin B12</span>
            <span className="biomarker-chip"><span className="biomarker-chip-dot"></span> Serum Iron &amp; Ferritin</span>
            <span className="biomarker-chip"><span className="biomarker-chip-dot"></span> Hemoglobin</span>
          </div>
          <Link to="/blood-tests" className="btn btn-secondary">
            View Blood Work &amp; Reference Ranges <span>→</span>
          </Link>
        </div>
      </section>

      {/* ── Section 2: Live Diagnostics & System Overview ── */}
      <div className="grid-2" style={{ marginBottom: 'var(--space-3xl)' }}>
        <HealthStatus />

        <div className="editorial-card fade-in fade-in-delay-2" id="quick-stats-card">
          <div className="eyebrow-label">System Architecture</div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.4rem', color: 'var(--accent-botanical)' }}>
            Telemetry Overview
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Live microservices status &amp; operational metrics.
          </p>
          <div className="stats-editorial-grid">
            <div className="stat-editorial-box">
              <div className="stat-num">5</div>
              <div className="stat-lbl">API Endpoints</div>
            </div>
            <div className="stat-editorial-box">
              <div className="stat-num">5</div>
              <div className="stat-lbl">DB Tables</div>
            </div>
            <div className="stat-editorial-box">
              <div className="stat-num">v0.1</div>
              <div className="stat-lbl">Version</div>
            </div>
            <div className="stat-editorial-box">
              <div className="stat-num">W1</div>
              <div className="stat-lbl">Milestone</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Section 3: Feature Editorial Suite ── */}
      <div className="features-section-header fade-in fade-in-delay-3">
        <div className="eyebrow-label">Integrated Ecosystem</div>
        <h2>Architected for Holistic Health Intelligence</h2>
      </div>

      <div className="features-editorial-grid">
        {features.map((feature, idx) => (
          <Link
            key={feature.title}
            to={feature.path === '#' ? undefined : feature.path}
            className={`feature-editorial-card fade-in fade-in-delay-${Math.min(idx + 1, 4)}`}
            id={`feature-card-${feature.title.toLowerCase().replace(/\s+/g, '-')}`}
          >
            <div>
              <div className="feature-card-top">
                <span className="feature-index">{feature.num}</span>
                <span
                  className={`badge ${
                    feature.status === 'Ready'
                      ? 'badge-success'
                      : feature.status === 'Coming Soon'
                      ? 'badge-warning'
                      : 'badge-error'
                  }`}
                >
                  {feature.status}
                </span>
              </div>
              <div className="feature-card-main">
                <span className="feature-icon-badge">{feature.icon}</span>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-desc">{feature.description}</p>
              </div>
            </div>
            <div className="feature-card-footer">
              <span className="feature-action-link">
                {feature.cta} <span>→</span>
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
