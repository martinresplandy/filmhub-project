import MovieCard from "../MovieCard/MovieCard";
import "./MovieList.css";

export default function MovieList({
  movies,
  title,
  loading,
  error,
  onRate,
  ratings = [],
  emptyMessage = "No movies found",
}) {
  if (loading) {
    return (
      <div className="movie-list-section">
        {title && <h2 className="movie-list-title">{title}</h2>}
        <div className="movie-list-loading">
          <div className="loading-spinner"></div>
          <p>Loading movies...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="movie-list-section">
        {title && <h2 className="movie-list-title">{title}</h2>}
        <div className="movie-list-error">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const uniqueMovies = movies ? 
    Array.from(new Map(movies.map(m => [m.external_id, m])).values()) : 
    [];

  if (!uniqueMovies || uniqueMovies.length === 0) {
    return (
      <div className="movie-list-section">
        {title && <h2 className="movie-list-title">{title}</h2>}
        <div className="movie-list-empty">
          <span className="empty-icon">🎬</span>
          <p>{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="movie-list-section">
      {title && <h2 className="movie-list-title">{title}</h2>}
      <div className="movie-list-grid">
        {uniqueMovies.map((movie) => (
          <MovieCard 
            key={movie.external_id} 
            movie={movie} 
            onRate={onRate}
            userRatings={ratings}
          />
        ))}
      </div>
    </div>
  );
}