export function AuthInput({ type, name, placeholder, value, onChange, required = true }) {
  return (
    <input
      type={type}
      name={name}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      required={required}
      className="auth-input"
    />
  );
}