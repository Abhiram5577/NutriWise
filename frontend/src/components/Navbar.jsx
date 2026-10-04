import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

/**
 * Navbar — responsive top navigation with auth-aware links.
 */
export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar" id="main-navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="navbar-brand" id="navbar-brand">
          <span className="brand-icon">🌿</span>
          <div className="brand-text-group">
            <span className="brand-text">NutriWise</span>
            <span className="brand-subtext">Nutritional Intelligence</span>
          </div>
        </NavLink>

        <div className="navbar-links">
          {isAuthenticated ? (
            <>
              <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-dashboard" end>
                Dashboard
              </NavLink>
              <NavLink to="/food-diary" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-food-diary">
                Food Diary
              </NavLink>
              <NavLink to="/health-profile" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-health-profile">
                Health Profile
              </NavLink>
              <NavLink to="/symptoms" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-symptoms">
                Symptoms
              </NavLink>
              <NavLink to="/blood-tests" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-blood-tests">
                Blood Tests
              </NavLink>
              <NavLink to="/ai-insights" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-ai-insights">
                AI Insights ✨
              </NavLink>
              <div className="nav-user-section">
                <span className="nav-user-pill">
                  <span className="nav-user-dot"></span>
                  <span className="nav-user-name" id="nav-user-name">
                    {user?.name?.split(' ')[0] || 'User'}
                  </span>
                </span>
                <button className="nav-logout-btn" onClick={handleLogout} id="nav-logout-btn">
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <NavLink to="/login" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-login">
                Login
              </NavLink>
              <NavLink to="/register" className="nav-link nav-register-btn" id="nav-register">
                Sign Up
              </NavLink>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
