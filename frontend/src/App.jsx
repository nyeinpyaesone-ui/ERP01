import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Inventory from "./pages/Inventory";
import Customers from "./pages/Customers";
import Orders from "./pages/Orders";
import Reports from "./pages/Reports";
import BusinessProfile from "./pages/BusinessProfile";
import Finance from "./pages/Finance";

const platformEnabled = import.meta.env.VITE_PLATFORM_ENABLED === "true";

function LoadingScreen() {
  return <main className="login-screen" aria-label="Loading ERP"><div><div className="spinner" /><p className="muted">Loading your workspace…</p></div></main>;
}

export default function App() {
  const { user, loading } = useAuth();
  if (loading) return <LoadingScreen />;

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route element={user ? <Layout /> : <Navigate to="/login" replace />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/inventory" element={<Inventory />} />
        <Route path="/customers" element={<Customers />} />
        <Route path="/orders" element={<Orders />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/business-profile" element={<BusinessProfile />} />
        {platformEnabled && (user?.is_staff || user?.is_superuser) && (
          <Route path="/finance" element={<Finance />} />
        )}
      </Route>
      <Route path="*" element={<Navigate to={user ? "/" : "/login"} replace />} />
    </Routes>
  );
}
