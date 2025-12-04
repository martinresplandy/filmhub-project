import MovieCard from "../MovieCard/MovieCard";
import "./MovieList.css";

export default function MovieList({
  movies,
  title,
  loading,
  error,
  onRate,
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

  if (!movies || movies.length === 0) {
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
        {movies.map((movie) => (
          <MovieCard key={movie.id} movie={movie} onRate={onRate} />
        ))}
      </div>
    </div>
  );
}
