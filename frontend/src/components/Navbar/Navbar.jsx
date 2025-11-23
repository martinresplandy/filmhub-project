import { useState } from 'react';
import './Navbar.css';

export default function Navbar({ user, onLogout, onNavigate }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    onLogout();
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <h1 className="navbar-logo" onClick={() => onNavigate('home')}>
          FilmHub
        </h1>

        <div className="navbar-links">
          <button 
            className="navbar-link" 
            onClick={() => onNavigate('home')}
          >
            Home
          </button>
          <button 
            className="navbar-link" 
            onClick={() => onNavigate('recommendations')}
          >
            Recommendations
          </button>
        </div>

        <div className="navbar-user">
          <button 
            className="navbar-user-btn"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {user?.username || 'User'}
          </button>
          
          {menuOpen && (
            <div className="navbar-dropdown">
              <button 
                className="navbar-dropdown-item"
                onClick={() => onNavigate('my-ratings')}
              >
                My Ratings
              </button>
              <button 
                className="navbar-dropdown-item navbar-logout"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}