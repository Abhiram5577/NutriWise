/**
 * Register — user registration page matching the dark glassmorphism style.
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ name: '', email: '', username: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Client-side validation
    if (!form.name || !form.email || !form.username || !form.password || !form.confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (form.username.length < 3) {
      setError('Username must be at least 3 characters.');
      return;
    }

    setLoading(true);
    try {
      await register({
        name: form.name,
        email: form.email,
        username: form.username,
        password: form.password,
      });
      setSuccess(true);
    } catch (err) {
      const detail = err.response?.data?.detail;
      // Handle Pydantic validation errors (array of objects)
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg || d.message).join('. '));
      } else {
        setError(detail || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="page-container">
        <div className="auth-wrapper">
          <div className="glass-card auth-card fade-in" id="register-success-card">
            <div className="auth-header">
              <span className="auth-icon">✅</span>
              <h1 className="auth-title">Account Created!</h1>
              <p className="auth-subtitle">Your account has been created successfully.</p>
            </div>
            <Link to="/login" className="btn btn-primary auth-submit" id="go-to-login-after-register">
              Sign In Now
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="auth-wrapper">
        <form className="glass-card auth-card fade-in" onSubmit={handleSubmit} id="register-card">
          <div className="auth-header">
            <span className="auth-icon">🌿</span>
            <h1 className="auth-title">Create Account</h1>
            <p className="auth-subtitle">Begin your journey to conscious nutritional wellness</p>
          </div>

          {error && (
            <div className="auth-error" id="register-error">
              <span>⚠️</span> {error}
            </div>
          )}

          <div className="auth-fields">
            <div className="auth-field">
              <label htmlFor="register-name">Full Name</label>
              <input
                type="text"
                id="register-name"
                name="name"
                placeholder="John Doe"
                value={form.name}
                onChange={handleChange}
                autoComplete="name"
              />
            </div>
            <div className="auth-field">
              <label htmlFor="register-email">Email</label>
              <input
                type="email"
                id="register-email"
                name="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
                autoComplete="email"
              />
            </div>
            <div className="auth-field">
              <label htmlFor="register-username">Username</label>
              <input
                type="text"
                id="register-username"
                name="username"
                placeholder="johndoe"
                value={form.username}
                onChange={handleChange}
                autoComplete="username"
              />
            </div>
            <div className="auth-row">
              <div className="auth-field">
                <label htmlFor="register-password">Password</label>
                <input
                  type="password"
                  id="register-password"
                  name="password"
                  placeholder="Min 8 characters"
                  value={form.password}
                  onChange={handleChange}
                  autoComplete="new-password"
                />
              </div>
              <div className="auth-field">
                <label htmlFor="register-confirm-password">Confirm</label>
                <input
                  type="password"
                  id="register-confirm-password"
                  name="confirmPassword"
                  placeholder="Repeat password"
                  value={form.confirmPassword}
                  onChange={handleChange}
                  autoComplete="new-password"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary auth-submit"
            disabled={loading}
            id="register-submit-btn"
          >
            {loading ? 'Creating account…' : 'Create Account'}
          </button>

          <p className="auth-footer">
            Already have an account?{' '}
            <Link to="/login" className="auth-link" id="go-to-login">
              Sign In
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
