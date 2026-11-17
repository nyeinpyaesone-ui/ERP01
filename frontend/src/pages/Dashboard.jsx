import { useEffect, useState } from "react";
import { Activity, Boxes, ClipboardList, Users, AlertTriangle } from "lucide-react";
import api from "../api";
import Loading from "../components/Loading";
import StatusBadge from "../components/StatusBadge";
import { errorMessage, formatDate, formatMoney } from "../utils";

function StatCard({ label, value, note, icon: Icon }) {
  return (
    <article className="stat-card">
      <div className="stat-label"><Icon size={15} /> {label}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-note">{note}</div>
    </article>
  );
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    api.get("/dashboard/")
      .then(({ data: payload }) => { if (active) setData(payload); })
      .catch((err) => { if (active) setError(errorMessage(err, "Dashboard data could not be loaded.")); });
    return () => { active = false; };
  }, []);

  return (
    <>
      <div className="page-heading">
        <div><h1>Dashboard</h1><p>Live overview of your inventory and sales operations.</p></div>
        <span className="muted" style={{ fontSize: 11 }}>Database-backed metrics</span>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      {!data && !error && <Loading label="Loading business metrics…" />}
      {data && (
        <>
          <section className="grid stats-grid" aria-label="Business metrics">
            <StatCard label="Fulfilled sales · This month" value={formatMoney(data.fulfilled_sales_this_month, data.currency)} note="Completed order value, not cash receipts" icon={Activity} />
            <StatCard label="Orders today" value={Number(data.orders_today || 0).toLocaleString()} note={String(data.open_orders || 0) + " open orders"} icon={ClipboardList} />
            <StatCard label="Active customers" value={Number(data.customers || 0).toLocaleString()} note="Customer accounts" icon={Users} />
            <StatCard label="Low-stock products" value={Number(data.low_stock_products || 0).toLocaleString()} note={String(data.active_products || 0) + " active products"} icon={AlertTriangle} />
          </section>
          <section className="grid dashboard-grid">
            <article className="panel">
              <h2>Recent orders</h2>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Order</th><th>Customer</th><th>Date</th><th>Status</th><th>Total</th></tr></thead>
                  <tbody>
                    {(data.recent_orders || []).map((order) => (
                      <tr key={order.id}>
                        <td><strong>{order.order_number}</strong></td>
                        <td>{order.customer_name}</td>
                        <td>{formatDate(order.order_date)}</td>
                        <td><StatusBadge value={order.status} /></td>
                        <td>{formatMoney(order.total_amount, data.currency)}</td>
                      </tr>
                    ))}
                    {!data.recent_orders?.length && <tr><td colSpan="5"><div className="empty">No orders have been recorded yet.</div></td></tr>}
                  </tbody>
                </table>
              </div>
            </article>
            <article className="panel">
              <h2>Workspace snapshot</h2>
              <div style={{ display: "grid", gap: 18 }}>
                <div><div className="stat-label"><Boxes size={14} /> Active products</div><div className="stat-value">{data.active_products}</div></div>
                <div><div className="stat-label"><ClipboardList size={14} /> Open orders</div><div className="stat-value">{data.open_orders}</div></div>
                <div><div className="stat-label">Fulfilled sales · Today</div><div className="stat-value" style={{ fontSize: 20 }}>{formatMoney(data.fulfilled_sales_today, data.currency)}</div></div>
              </div>
              <p className="muted" style={{ fontSize: 10, marginTop: 20 }}>Updated {new Date(data.as_of).toLocaleString()}</p>
            </article>
          </section>
        </>
      )}
    </>
  );
}
