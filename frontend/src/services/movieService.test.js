import { movieService } from './movieService';
import { API_URL } from '../config';


global.fetch = jest.fn();

describe('movieService', () => {
  beforeEach(() => {
    fetch.mockClear();
    localStorage.clear();
  });

  const mockMovies = [
    { id: 1, title: 'Movie 1', external_id: 101 },
    { id: 2, title: 'Movie 2', external_id: 102 },
  ];

  it('getMovies fetches movies successfully', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockMovies,
    });

    const movies = await movieService.getMovies();
    expect(movies).toEqual(mockMovies);
    expect(fetch).toHaveBeenCalledWith(`${API_URL}/movies/`, expect.any(Object));
  });

  it('getMovies throws an error on failure', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
    });

    await expect(movieService.getMovies()).rejects.toThrow('Failed to fetch movies catalog');
  });

  it('searchMovies fetches movies with query', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMovies,
      });

      const query = 'test';
      await movieService.searchMovies(query);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`search=${query}`),
        expect.any(Object)
      );
  });
  
  it('getMovie fetches a specific movie', async () => {
      const movie = { id: 1, title: 'Target Movie', external_id: 123 };
      
      fetch.mockImplementation((url) => {
          if (url.includes('/movies/') && !url.includes('watch_list') && !url.includes('watched')) {
              return Promise.resolve({
                  ok: true,
                  json: async () => ({ popular: [movie] })
              });
          }
           return Promise.resolve({
                  ok: true,
                  json: async () => []
              });
      });

      const result = await movieService.getMovie(123);
      expect(result).toEqual(movie);
  });

  it('rateMovie sends a POST request', async () => {
      fetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true }),
      });

      await movieService.rateMovie(123, 8, 'Good');
      expect(fetch).toHaveBeenCalledWith(
          `${API_URL}/ratings/`,
          expect.objectContaining({
              method: 'POST',
              body: JSON.stringify({ movie: 123, score: 8, comment: 'Good' }),
          })
      );
  });
});
