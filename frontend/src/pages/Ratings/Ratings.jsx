import { useState, useEffect, useCallback } from "react";
import MovieList from "../../components/MovieList/MovieList";
import { movieService } from "../../services/movieService";
import "./Ratings.css";

export default function Ratings() {
  const [ratings, setRatings] = useState([]);
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadRatings = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const ratingsData = await movieService.getRatings();
      const ratingsArray = Array.isArray(ratingsData) ? ratingsData : [];
      setRatings(ratingsArray);

      const allMovies = await movieService.getMovies();
      const moviesArray = Array.isArray(allMovies) ? allMovies : [];

      const ratedMovieIds = ratingsArray.map((rating) => rating.movie);

      const moviesFromRatings = moviesArray.filter((movie) =>
        ratedMovieIds.includes(movie.external_id)
      );

      setMovies(moviesFromRatings);
    } catch (err) {
      console.error("Error loading ratings:", err);
      setError("Error loading your ratings. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRatings();
  }, [loadRatings]);

  const handleRate = async (movieId, rating) => {
    try {
      await movieService.rateMovie(movieId, rating);
      loadRatings();
    } catch (err) {
      console.error("Error rating movie:", err);
    }
  };

  return (
    <div className="ratings-page">
      <div className="ratings-content">
        <header className="ratings-header">
          <h1 className="ratings-title">My Ratings</h1>
          <p className="ratings-subtitle">Movies you've rated and reviewed</p>
        </header>
        {console.log(ratings)}
        <main className="ratings-movies">
          <MovieList
            title=""
            movies={movies}
            loading={loading}
            error={error}
            onRate={handleRate}
            emptyMessage="You haven't rated any movies yet"
          />
        </main>
      </div>
    </div>
  );
}
