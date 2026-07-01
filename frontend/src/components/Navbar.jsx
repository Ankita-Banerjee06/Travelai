import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Menu, X, Plane, LogOut, LayoutDashboard, MapPin } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setMobileOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container container">
        <Link to="/" className="navbar-brand" onClick={() => setMobileOpen(false)}>
          <div className="navbar-logo">
            <Plane size={22} />
          </div>
          <span className="navbar-title">TravelAI</span>
        </Link>

        <div className="navbar-links hide-mobile">
          {user ? (
            <>
              <Link to="/dashboard" className="nav-link">
                <LayoutDashboard size={16} />
                Dashboard
              </Link>
              <Link to="/plan" className="nav-link">
                <MapPin size={16} />
                Plan Trip
              </Link>
              <div className="nav-user">
                <span className="nav-username">{user.username}</span>
                <button onClick={handleLogout} className="btn btn-secondary btn-sm" id="logout-btn">
                  <LogOut size={14} />
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-secondary btn-sm" id="login-link">Login</Link>
              <Link to="/register" className="btn btn-primary btn-sm" id="register-link">Get Started</Link>
            </>
          )}
        </div>

        <button
          className="navbar-toggle"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle navigation"
          id="navbar-toggle"
        >
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            className="navbar-mobile"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {user ? (
              <>
                <Link to="/dashboard" className="nav-link-mobile" onClick={() => setMobileOpen(false)}>
                  <LayoutDashboard size={16} /> Dashboard
                </Link>
                <Link to="/plan" className="nav-link-mobile" onClick={() => setMobileOpen(false)}>
                  <MapPin size={16} /> Plan Trip
                </Link>
                <button onClick={handleLogout} className="nav-link-mobile logout-mobile">
                  <LogOut size={16} /> Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="nav-link-mobile" onClick={() => setMobileOpen(false)}>Login</Link>
                <Link to="/register" className="nav-link-mobile" onClick={() => setMobileOpen(false)}>Get Started</Link>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
