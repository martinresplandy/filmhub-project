import { useState } from 'react';
import './SearchBar.css';

export default function SearchBar({ onSearch, placeholder = "Search movies..." }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery('');
    onSearch('');
  };

  return (
    <form className="searchbar" onSubmit={handleSubmit}>
      <div className="searchbar-container">
        <svg 
          className="searchbar-icon" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="M21 21l-4.35-4.35" />
        </svg>
        
        <input
          type="text"
          className="searchbar-input"
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        
        {query && (
          <button 
            type="button" 
            className="searchbar-clear"
            onClick={handleClear}
          >
            ✕
          </button>
        )}
        
        <button type="submit" className="searchbar-btn">
          Search
        </button>
      </div>
    </form>
  );
}