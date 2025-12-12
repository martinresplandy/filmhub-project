const API_URL = "https://filmhub-project.onrender.com/api/";

export const authService = {
  login: async (username, password) => {
    const response = await fetch(`${API_URL}/login/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });
    return response.json();
  },

  logout: () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
  },

  register: async (username, email, password) => {
    const response = await fetch(`${API_URL}/register/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, email, password }),
    });
    return response.json();
  },

  saveToken: (token, user) => {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
  },

  getProfile: async () => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_URL}/profile/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error("Failed to fetch profile");
    }
    return response.json();
  },

  updateProfile: async (username, email, password) => {
    const token = localStorage.getItem("token");
    const body = { username, email };
    if (password) {
      body.password = password;
    }
    const response = await fetch(`${API_URL}/profile/`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      const error = await response.json();
      throw error;
    }
    const data = await response.json();
    // Update stored user data
    localStorage.setItem("user", JSON.stringify(data));
    return data;
  },
};
