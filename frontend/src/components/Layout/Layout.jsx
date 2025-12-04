import { Outlet } from "react-router-dom";
import Navbar from "../Navbar/Navbar";
import useAuth from "../../hooks/useAuth";

const Layout = () => {
  const { auth, logout } = useAuth();

  return (
    <main className="App">
      <div className="content">
        <Outlet />
        <Navbar user={auth.user} onLogout={logout} />
      </div>
    </main>
  );
};

export default Layout;
