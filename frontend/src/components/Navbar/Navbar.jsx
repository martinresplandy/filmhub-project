import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./Navbar.css";

export default function Navbar({ user, onLogout }) {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);
  const buttonRef = useRef(null);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    onLogout();
    setMenuOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        menuRef.current &&
        buttonRef.current &&
        !menuRef.current.contains(event.target) &&
        !buttonRef.current.contains(event.target)
      ) {
        setMenuOpen(false);
      }
    };

    if (menuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("touchstart", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
    };
  }, [menuOpen]);

  // Close menu on ESC key
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === "Escape" && menuOpen) {
        setMenuOpen(false);
      }
    };

    if (menuOpen) {
      document.addEventListener("keydown", handleEscape);
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, [menuOpen]);

  const handleNavigate = (path) => {
    navigate(path);
    setMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <h1 className="navbar-logo" onClick={() => navigate("/")}>
          FilmHub
        </h1>

        <div className="navbar-links">
          <button className="navbar-link" onClick={() => navigate("/")}>
            Home
          </button>
          <button
            className="navbar-link"
            onClick={() => navigate("/recommendations")}
          >
            Recommendations
          </button>
        </div>

        <div className="navbar-user">
          <button
            ref={buttonRef}
            className={`navbar-user-btn ${menuOpen ? "active" : ""}`}
            onClick={() => setMenuOpen(!menuOpen)}
            aria-expanded={menuOpen}
            aria-haspopup="true"
          >
            {user?.username || "User"}
          </button>

          <div
            ref={menuRef}
            className={`navbar-dropdown ${menuOpen ? "open" : ""}`}
            role="menu"
          >
            <button
              className="navbar-dropdown-item"
              onClick={() => handleNavigate("/ratings")}
              role="menuitem"
            >
              My Ratings
            </button>
            <button
              className="navbar-dropdown-item"
              onClick={() => handleNavigate("/profile")}
              role="menuitem"
            >
              Profile
            </button>
            <button
              className="navbar-dropdown-item navbar-logout"
              onClick={handleLogout}
              role="menuitem"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
