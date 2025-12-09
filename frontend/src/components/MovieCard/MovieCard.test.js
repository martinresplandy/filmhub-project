import { render, screen, fireEvent } from '@testing-library/react';
import MovieCard from './MovieCard';
import { BrowserRouter } from 'react-router-dom';

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  __esModule: true,
  BrowserRouter: ({ children }) => <div>{children}</div>,
  useNavigate: () => mockNavigate,
}), { virtual: true });

describe('MovieCard', () => {
  const mockMovie = {
    external_id: 123,
    title: 'Test Movie',
    year: '2023',
    genre: 'Action',
    poster_url: 'http://example.com/poster.jpg',
    average_rating: 4.5,
  };

  const renderComponent = (props = {}) => {
    return render(
      <BrowserRouter>
        <MovieCard movie={mockMovie} {...props} />
      </BrowserRouter>
    );
  };

  it('renders movie information correctly', () => {
    renderComponent();
    expect(screen.getByText('Test Movie')).toBeInTheDocument();
    expect(screen.getByText('2023')).toBeInTheDocument();
    expect(screen.getByText('Action')).toBeInTheDocument();
    expect(screen.getByRole('img')).toHaveAttribute('src', 'http://example.com/poster.jpg');
    expect(screen.getByText('4.5')).toBeInTheDocument();
  });

  it('navigates to movie details on click', () => {
    renderComponent();
    fireEvent.click(screen.getByRole('img').parentElement);
    expect(mockNavigate).toHaveBeenCalledWith('/movie/123');
  });

  it('displays user rating if present', () => {
    const userRatings = [{ movie: 123, score: 8 }];
    renderComponent({ userRatings });
    expect(screen.getByText('8')).toBeInTheDocument();
    expect(screen.getByText('Your rating:')).toBeInTheDocument();
  });

  it('displays "Not rated" if no user rating', () => {
    renderComponent({ userRatings: [] });
    expect(screen.getByText('Not rated')).toBeInTheDocument();
  });
});
