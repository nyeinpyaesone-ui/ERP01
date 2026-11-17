import { NavLink, Outlet } from "react-router-dom";
import {
  BarChart3, Boxes, Building2, ClipboardList,
  LayoutDashboard, LogOut, Users,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

const platformEnabled = import.meta.env.VITE_PLATFORM_ENABLED === "true";

export default function Layout() {
  const { user, logout } = useAuth();
  const initials = (user?.first_name || user?.username || "U").slice(0, 1).toUpperCase();
  const links = [
    { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
    { to: "/inventory", label: "Inventory", icon: Boxes },
    { to: "/orders", label: "Orders", icon: ClipboardList },
    { to: "/customers", label: "Customers", icon: Users },
    { to: "/reports", label: "Reports", icon: BarChart3 },
    { to: "/business-profile", label: "Business profile", icon: Building2 },
    ...(platformEnabled && (user?.is_staff || user?.is_superuser)
      ? [{ to: "/finance", label: "Finance", icon: BarChart3 }]
      : []),
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Main navigation">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">E</div>
          <div><strong>ERP01</strong><small>Business Suite</small></div>
        </div>
        <div>
          <div className="nav-label">Workspace</div>
          <nav className="nav-list" aria-label="Workspace">
            {links.map(({ to, label, icon: Icon, end }) => (
              <NavLink key={to} to={to} end={end} className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>
                <Icon size={17} aria-hidden="true" /><span>{label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="sidebar-footer">
          <div>ERP01 · v1.2.0</div>
          <div>Inventory & Sales Operations</div>
        </div>
      </aside>
      <div className="main-area">
        <header className="topbar">
          <div className="topbar-title">Business operations / <strong>Workspace</strong></div>
          <div className="user-menu">
            <div className="avatar" aria-hidden="true">{initials}</div>
            <span>{user?.first_name || user?.username}</span>
            <button className="btn btn-quiet btn-small" type="button" onClick={logout} aria-label="Sign out">
              <LogOut size={14} /> Sign out
            </button>
          </div>
        </header>
        <main className="content"><Outlet /></main>
      </div>
    </div>
  );
}
