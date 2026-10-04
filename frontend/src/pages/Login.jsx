/**
 * Login — functional login page matching the dark glassmorphism style.
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!form.email || !form.password) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    try {
      await login({ email: form.email, password: form.password });
      navigate('/');
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="auth-wrapper">
        <form className="glass-card auth-card fade-in" onSubmit={handleSubmit} id="login-card">
          <div className="auth-header">
            <span className="auth-icon">🌿</span>
            <h1 className="auth-title">Welcome Back</h1>
            <p className="auth-subtitle">Access your personalized nutritional intelligence</p>
          </div>

          {error && (
            <div className="auth-error" id="login-error">
              <span>⚠️</span> {error}
            </div>
          )}

          <div className="auth-fields">
            <div className="auth-field">
              <label htmlFor="login-email">Email</label>
              <input
                type="email"
                id="login-email"
                name="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
                autoComplete="email"
              />
            </div>
            <div className="auth-field">
              <label htmlFor="login-password">Password</label>
              <input
                type="password"
                id="login-password"
                name="password"
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
                autoComplete="current-password"
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary auth-submit"
            disabled={loading}
            id="login-submit-btn"
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>

          <p className="auth-footer">
            Don't have an account?{' '}
            <Link to="/register" className="auth-link" id="go-to-register">
              Create one
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
