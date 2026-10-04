import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import FoodDiary from './pages/FoodDiary';
import HealthProfile from './pages/HealthProfile';
import Symptoms from './pages/Symptoms';
import BloodTests from './pages/BloodTests';
import AiInsights from './pages/AiInsights';
import Login from './pages/Login';
import Register from './pages/Register';

/**
 * ProtectedRoute — redirects unauthenticated users to /login.
 */
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: '4rem' }}>
        <span style={{ fontSize: '2rem' }}>⏳</span>
        <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-md)' }}>Loading…</p>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

/**
 * GuestRoute — redirects authenticated users away from login/register.
 */
function GuestRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return null;
  return isAuthenticated ? <Navigate to="/" replace /> : children;
}

/**
 * AppRoutes — separated so useAuth can be called inside Router + AuthProvider.
 */
function AppRoutes() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/food-diary" element={<ProtectedRoute><FoodDiary /></ProtectedRoute>} />
        <Route path="/health-profile" element={<ProtectedRoute><HealthProfile /></ProtectedRoute>} />
        <Route path="/symptoms" element={<ProtectedRoute><Symptoms /></ProtectedRoute>} />
        <Route path="/blood-tests" element={<ProtectedRoute><BloodTests /></ProtectedRoute>} />
        <Route path="/ai-insights" element={<ProtectedRoute><AiInsights /></ProtectedRoute>} />
        <Route path="/login" element={<GuestRoute><Login /></GuestRoute>} />
        <Route path="/register" element={<GuestRoute><Register /></GuestRoute>} />
      </Routes>
    </>
  );
}

/**
 * App — root component with AuthProvider, Router, and layout.
 */
export default function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}
