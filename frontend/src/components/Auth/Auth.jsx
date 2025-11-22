import { useState } from 'react';
import { authService } from '../../services/authService';
import { AuthInput } from './AuthInput';
import './Auth.css';

export default function Auth({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const data = isLogin
        ? await authService.login(formData.username, formData.password)
        : await authService.register(formData.username, formData.email, formData.password);

      if (data.token) {
        authService.saveToken(data.token, data.user);
        setSuccess(isLogin ? 'Login successful!' : 'Account created successfully!');
        setFormData({ username: '', email: '', password: '' });
        
        // Notify parent component of successful login
        if (onLoginSuccess) {
          setTimeout(() => {
            onLoginSuccess(data.user);
          }, 500);
        }
      } else {
        setError(data.error || data.username?.[0] || data.email?.[0] || 'Authentication error');
      }
    } catch (err) {
      setError('Error connecting to server');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setSuccess('');
  };

  return (
    <div className="auth-container">
      <h1 className="auth-title">FilmHub</h1>

      <div className="auth-box">
        <h2 className="auth-heading">
          {isLogin ? 'Login' : 'Create Account'}
        </h2>

        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <AuthInput
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
          />

          {!isLogin && (
            <AuthInput
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
            />
          )}

          <AuthInput
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
          />

          <button
            type="submit"
            disabled={loading}
            className="auth-button"
          >
            {loading ? 'Loading...' : (isLogin ? 'Login' : 'Create Account')}
          </button>
        </form>

        <p className="auth-footer">
          {isLogin ? "Don't have an account?" : 'Already have an account?'}
          {' '}
          <button
            type="button"
            onClick={toggleMode}
            className="auth-toggle"
          >
            {isLogin ? 'Create' : 'Login'}
          </button>
        </p>
      </div>
    </div>
  );
}