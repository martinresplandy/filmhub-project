import { useState, useEffect } from "react";
import useAuth from "../../hooks/useAuth";
import { authService } from "../../services/authService";
import { AuthInput } from "../Auth/AuthInput";
import "./Profile.css";

export default function Profile() {
  const { auth, setAuth } = useAuth();
  const [loading, setLoading] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const userData = await authService.getProfile();
        setFormData({
          username: userData.username || "",
          email: userData.email || "",
          password: "",
          confirmPassword: "",
        });
      } catch (err) {
        setError("Failed to load profile data");
      } finally {
        setLoadingProfile(false);
      }
    };

    fetchProfile();
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear errors when user starts typing
    if (error) setError("");
    if (success) setSuccess("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    // Validate password if password fields are shown
    if (formData.password && formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }
    if (formData.password && formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      setLoading(false);
      return;
    }

    try {
      const updatedUser = await authService.updateProfile(
        formData.username,
        formData.email,
        formData.password || undefined
      );

      setAuth({ ...auth, user: updatedUser });

      setSuccess("Profile updated successfully!");
      setFormData({
        ...formData,
        password: "",
        confirmPassword: "",
      });

      setTimeout(() => {
        setSuccess("");
      }, 3000);
    } catch (err) {
      if (err.username) {
        const errorMsg = Array.isArray(err.username)
          ? err.username[0]
          : err.username;
        setError(errorMsg);
      } else if (err.email) {
        const errorMsg = Array.isArray(err.email) ? err.email[0] : err.email;
        setError(errorMsg);
      } else if (err.password) {
        const errorMsg = Array.isArray(err.password)
          ? err.password[0]
          : err.password;
        setError(errorMsg);
      } else if (err.error) {
        setError(err.error);
      } else if (err.detail) {
        setError(err.detail);
      } else {
        setError("Failed to update profile. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  if (loadingProfile) {
    return (
      <div className="profile-container">
        <div className="profile-loading">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-box">
        <h2 className="profile-heading">Profile</h2>

        {error && <div className="profile-error">{error}</div>}
        {success && <div className="profile-success">{success}</div>}

        <form onSubmit={handleSubmit} className="profile-form">
          <AuthInput
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required={true}
          />

          <AuthInput
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required={true}
          />

          <>
            <AuthInput
              type="password"
              name="password"
              placeholder="New Password"
              value={formData.password}
              onChange={handleChange}
              required={false}
            />

            <AuthInput
              type="password"
              name="confirmPassword"
              placeholder="Confirm Password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required={false}
            />
          </>

          <button type="submit" disabled={loading} className="profile-button">
            {loading ? "Saving..." : "Save"}
          </button>
        </form>
      </div>
    </div>
  );
}
