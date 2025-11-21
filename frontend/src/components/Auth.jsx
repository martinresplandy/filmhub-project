import { useState } from 'react';

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

  const API_URL = 'http://localhost:8000/api';

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
      const endpoint = isLogin ? 'login/' : 'register/';
      const payload = isLogin 
        ? { username: formData.username, password: formData.password }
        : { username: formData.username, email: formData.email, password: formData.password };

      const response = await fetch(`${API_URL}/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok) {
        const token = data.token;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(data.user));
        setSuccess(isLogin ? 'Login realizado com sucesso!' : 'Conta criada com sucesso!');
        setFormData({ username: '', email: '', password: '' });
        console.log('Autenticado com token:', token);
      } else {
        setError(data.error || data.username?.[0] || data.email?.[0] || 'Erro na autenticação');
      }
    } catch (err) {
      setError('Erro ao conectar com o servidor');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f5f5f5',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        gap: '20px'
    }}>

        {}
        <h1 style={{
        fontSize: '48px',
        fontWeight: '800',
        color: '#2fa700ff',
        textShadow: '0 4px 10px rgba(0,0,0,0.15)',
        marginBottom: '10px'
        }}>
        FilmHub
        </h1>

        <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '400px'
        }}>

        <h2 style={{
            textAlign: 'center',
            marginBottom: '30px',
            fontSize: '24px',
            color: '#333'
        }}>
            {isLogin ? 'Login' : 'Criar Conta'}
        </h2>

        {error && (
            <div style={{
            backgroundColor: '#fee',
            color: '#c33',
            padding: '12px',
            borderRadius: '4px',
            marginBottom: '20px',
            fontSize: '14px'
            }}>
            {error}
            </div>
        )}

        {success && (
            <div style={{
            backgroundColor: '#efe',
            color: '#3c3',
            padding: '12px',
            borderRadius: '4px',
            marginBottom: '20px',
            fontSize: '14px'
            }}>
            {success}
            </div>
        )}

        <div>
            <input
            type="text"
            name="username"
            placeholder="Utilizador"
            value={formData.username}
            onChange={handleChange}
            required
            style={{
                width: '100%',
                padding: '12px',
                marginBottom: '15px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px',
                boxSizing: 'border-box'
            }}
            />

            {!isLogin && (
            <input
                type="email"
                name="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                required
                style={{
                width: '100%',
                padding: '12px',
                marginBottom: '15px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px',
                boxSizing: 'border-box'
                }}
            />
            )}

            <input
            type="password"
            name="password"
            placeholder="Palavra-passe"
            value={formData.password}
            onChange={handleChange}
            required
            style={{
                width: '100%',
                padding: '12px',
                marginBottom: '20px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px',
                boxSizing: 'border-box'
            }}
            />

            <button
            onClick={handleSubmit}
            disabled={loading}
            style={{
                width: '100%',
                padding: '12px',
                backgroundColor: '#333',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.6 : 1
            }}
            >
            {loading ? 'A carregar...' : (isLogin ? 'Entrar' : 'Criar Conta')}
            </button>
        </div>

        <p style={{
            textAlign: 'center',
            marginTop: '20px',
            color: '#666',
            fontSize: '14px'
        }}>
            {isLogin ? 'Ainda não tens conta?' : 'Já tens conta?'}
            {' '}
            <button
            onClick={() => setIsLogin(!isLogin)}
            style={{
                background: 'none',
                border: 'none',
                color: '#0066cc',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                textDecoration: 'underline'
            }}
            >
            {isLogin ? 'Criar' : 'Entrar'}
            </button>
        </p>
        </div>
    </div>
    );
}