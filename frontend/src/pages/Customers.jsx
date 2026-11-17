import { useCallback, useEffect, useMemo, useState } from "react";
import { Plus, RefreshCw, Search } from "lucide-react";
import { fetchAll } from "../api";
import api from "../api";
import Loading from "../components/Loading";
import Modal from "../components/Modal";
import { errorMessage, formatDate } from "../utils";

const initialForm = {
  name: "", customer_type: "BUSINESS", email: "", phone: "",
  billing_address: "", shipping_address: "",
};

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState(initialForm);

  const refresh = useCallback(async () => {
    try {
      setError("");
      setCustomers(await fetchAll("/sales/customers/"));
    } catch (err) {
      setError(errorMessage(err, "Customer records could not be loaded."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const visible = useMemo(() => {
    const needle = search.trim().toLowerCase();
    if (!needle) return customers;
    return customers.filter((customer) =>
      [customer.name, customer.email, customer.phone].some((value) =>
        String(value || "").toLowerCase().includes(needle)
      )
    );
  }, [customers, search]);

  async function createCustomer(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.post("/sales/customers/", form);
      setModal(false);
      setForm(initialForm);
      setNotice("Customer created.");
      await refresh();
    } catch (err) {
      setError(errorMessage(err, "Customer could not be created."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-heading">
        <div><h1>Customers</h1><p>Customer accounts and relationship records.</p></div>
        <button className="btn" type="button" onClick={() => { setError(""); setModal(true); }}><Plus size={15} /> Add customer</button>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      {notice && <div className="alert alert-success" role="status">{notice}<button type="button" onClick={() => setNotice("")} style={{ float: "right", border: 0, background: "transparent", color: "inherit" }}>Dismiss</button></div>}
      <section className="panel">
        <div className="toolbar">
          <div className="field search-field">
            <label htmlFor="customer-search">Search customers</label>
            <div style={{ position: "relative" }}><Search size={15} style={{ position: "absolute", left: 11, top: 10, color: "#8792a4" }} /><input id="customer-search" style={{ paddingLeft: 34 }} value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Name, email or phone" /></div>
          </div>
          <button className="btn btn-quiet btn-small" type="button" onClick={refresh}><RefreshCw size={13} /> Refresh</button>
          <span className="muted" style={{ fontSize: 11, marginLeft: "auto" }}>{visible.length} customers</span>
        </div>
        {loading ? <Loading /> : (
          <div className="table-wrap"><table>
            <thead><tr><th>Customer</th><th>Type</th><th>Email</th><th>Phone</th><th>Orders</th><th>Created</th><th>Status</th></tr></thead>
            <tbody>
              {visible.map((customer) => (
                <tr key={customer.id}>
                  <td><strong>{customer.name}</strong></td><td>{customer.customer_type}</td>
                  <td>{customer.email}</td><td>{customer.phone || "—"}</td>
                  <td>{customer.orders_count}</td><td>{formatDate(customer.created_at)}</td>
                  <td><span className={"status " + (customer.is_active ? "FULFILLED" : "CANCELLED")}>{customer.is_active ? "ACTIVE" : "INACTIVE"}</span></td>
                </tr>
              ))}
              {!visible.length && <tr><td colSpan="7"><div className="empty">{search ? "No customers match your search." : "No customer accounts yet."}</div></td></tr>}
            </tbody>
          </table></div>
        )}
      </section>
      {modal && <Modal title="Add customer" onClose={() => setModal(false)}>
        <form onSubmit={createCustomer}>
          <div className="form-grid">
            <div className="field"><label htmlFor="customer-name">Customer name</label><input id="customer-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required maxLength="200" /></div>
            <div className="field"><label htmlFor="customer-type">Customer type</label><select id="customer-type" value={form.customer_type} onChange={(e) => setForm({ ...form, customer_type: e.target.value })}><option value="BUSINESS">Business</option><option value="INDIVIDUAL">Individual</option></select></div>
            <div className="field"><label htmlFor="customer-email">Email</label><input id="customer-email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></div>
            <div className="field"><label htmlFor="customer-phone">Phone</label><input id="customer-phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} maxLength="30" /></div>
          </div>
          <div className="field" style={{ marginTop: 13 }}><label htmlFor="billing-address">Billing address</label><textarea id="billing-address" rows="2" value={form.billing_address} onChange={(e) => setForm({ ...form, billing_address: e.target.value })} /></div>
          <div className="field" style={{ marginTop: 13 }}><label htmlFor="shipping-address">Shipping address</label><textarea id="shipping-address" rows="2" value={form.shipping_address} onChange={(e) => setForm({ ...form, shipping_address: e.target.value })} /></div>
          <div className="form-actions"><button className="btn btn-quiet" type="button" onClick={() => setModal(false)}>Cancel</button><button className="btn" type="submit" disabled={busy}>{busy ? "Saving…" : "Create customer"}</button></div>
        </form>
      </Modal>}
    </>
  );
}
