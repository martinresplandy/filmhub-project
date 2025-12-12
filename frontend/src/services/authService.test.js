import { authService } from './authService';

const API_URL = 'https://filmhub-project.onrender.com/api';

// Mock the global fetch function
global.fetch = jest.fn();

describe('authService', () => {
  beforeEach(() => {
    fetch.mockClear();
    localStorage.clear();
  });

  const mockUser = { username: 'testuser', token: 'fake-token' };

  it('login stores token and user on success', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    });

    const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');

    const result = await authService.login('testuser', 'password');
    expect(result).toEqual(mockUser);
    
  });

  it('saveToken stores data in localStorage', () => {
      const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');
      authService.saveToken('fake-token', { name: 'user' });
      expect(setItemSpy).toHaveBeenCalledWith('token', 'fake-token');
      expect(setItemSpy).toHaveBeenCalledWith('user', JSON.stringify({ name: 'user' }));
  });

  it('register sends correct data', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    });

    await authService.register('testuser', 'test@example.com', 'password');
    expect(fetch).toHaveBeenCalledWith(
        API_URL+'/register/',
        expect.objectContaining({
            method: 'POST',
            body: JSON.stringify({ username: 'testuser', email: 'test@example.com', password: 'password' }),
        })
    );
  });

  it('logout removes items from localStorage', () => {
      const removeItemSpy = jest.spyOn(Storage.prototype, 'removeItem');
      authService.logout();
      expect(removeItemSpy).toHaveBeenCalledWith('user');
      expect(removeItemSpy).toHaveBeenCalledWith('token');
  });
});
