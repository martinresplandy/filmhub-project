import { useState } from 'react';
import { authService } from '../../services/authService';
import { AuthInput } from './AuthInput';
import './Auth.css';

export default function Auth() {
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
      } else {
        // Processar erros do backend
        if (data.username) {
          const errorMsg = Array.isArray(data.username) ? data.username[0] : data.username;
          setError(errorMsg === 'This field may not be blank.' ? 'Username field may not be blank.' : errorMsg);
        } else if (data.email) {
          const errorMsg = Array.isArray(data.email) ? data.email[0] : data.email;
          setError(errorMsg === 'This field may not be blank.' ? 'Email field may not be blank.' : errorMsg);
        } else if (data.password) {
          const errorMsg = Array.isArray(data.password) ? data.password[0] : data.password;
          setError(errorMsg === 'This field may not be blank.' ? 'Password field may not be blank.' : errorMsg);
        } else if (data.error) {
          setError(data.error);
        } else if (data.detail) {
          setError(data.detail);
        } else {
          setError('Authentication error');
        }
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
            required={false}
          />

          {!isLogin && (
            <AuthInput
              type="text"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              required={false}
            />
          )}

          <AuthInput
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required={false}
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
          {isLogin ? 'Don’t have an account?' : 'Already have an account?'}
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