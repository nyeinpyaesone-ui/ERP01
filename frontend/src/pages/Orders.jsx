import { useCallback, useEffect, useState } from "react";
import { CheckCircle2, CirclePlus, ClipboardList, Plus, RefreshCw, Truck, XCircle } from "lucide-react";
import api, { fetchAll } from "../api";
import Loading from "../components/Loading";
import Modal from "../components/Modal";
import StatusBadge from "../components/StatusBadge";
import { errorMessage, formatDate, formatMoney } from "../utils";
import { useAuth } from "../context/AuthContext";

function newOrderNumber() {
  return "SO-" + new Date().toISOString().slice(0, 10).replaceAll("-", "") + "-" + String(Date.now()).slice(-5);
}

export default function Orders() {
  const { currency } = useAuth();
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [modal, setModal] = useState("");
  const [target, setTarget] = useState(null);
  const [newForm, setNewForm] = useState({
    customer: "", order_number: newOrderNumber(), notes: "",
    product: "", quantity: "1", unit_price: "", discount_amount: "0",
  });
  const [itemForm, setItemForm] = useState({
    product: "", quantity: "1", unit_price: "", discount_amount: "0",
  });
  const [warehouseId, setWarehouseId] = useState("");

  const refresh = useCallback(async () => {
    try {
      setError("");
      const [orderRows, customerRows, productRows, warehouseRows] = await Promise.all([
        fetchAll("/sales/orders/"),
        fetchAll("/sales/customers/?is_active=true"),
        fetchAll("/inventory/products/?is_active=true"),
        fetchAll("/inventory/warehouses/"),
      ]);
      setOrders(orderRows);
      setCustomers(customerRows.filter((c) => c.is_active));
      setProducts(productRows.filter((p) => p.is_active));
      setWarehouses(warehouseRows.filter((w) => w.is_active));
    } catch (err) {
      setError(errorMessage(err, "Sales orders could not be loaded."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  function updateProduct(field, productId, currentForm, setForm) {
    const product = products.find((item) => String(item.id) === String(productId));
    setForm({
      ...currentForm,
      [field]: productId,
      unit_price: product ? String(product.unit_price) : "",
    });
  }

  async function createOrder(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { data: order } = await api.post("/sales/orders/", {
        customer: Number(newForm.customer),
        order_number: newForm.order_number.trim(),
        notes: newForm.notes,
      });
      if (newForm.product) {
        await api.post("/sales/orders/" + order.id + "/add_item/", {
          product: Number(newForm.product),
          quantity: Number(newForm.quantity),
          unit_price: newForm.unit_price,
          discount_amount: newForm.discount_amount || "0",
        });
      }
      setModal("");
      setNewForm({
        customer: "", order_number: newOrderNumber(), notes: "",
        product: "", quantity: "1", unit_price: "", discount_amount: "0",
      });
      setNotice("Draft order created.");
      await refresh();
    } catch (err) {
      setError(errorMessage(err, "Order could not be created. If a draft was already created, it remains available."));
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function addItem(event) {
    event.preventDefault();
    if (!target) return;
    setBusy(true);
    setError("");
    try {
      await api.post("/sales/orders/" + target.id + "/add_item/", {
        product: Number(itemForm.product),
        quantity: Number(itemForm.quantity),
        unit_price: itemForm.unit_price,
        discount_amount: itemForm.discount_amount || "0",
      });
      setModal("");
      setTarget(null);
      setNotice("Order line added.");
      await refresh();
    } catch (err) {
      setError(errorMessage(err, "Order line could not be added."));
    } finally {
      setBusy(false);
    }
  }

  async function transition(order, action, payload = {}) {
    setBusy(true);
    setError("");
    try {
      await api.post("/sales/orders/" + order.id + "/" + action + "/", payload);
      setModal("");
      setTarget(null);
      setNotice("Order " + order.order_number + " updated.");
      await refresh();
    } catch (err) {
      setError(errorMessage(err, "The order transition was rejected."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-heading">
        <div><h1>Orders</h1><p>Create draft orders, submit them, and fulfil against warehouse stock.</p></div>
        <button className="btn" type="button" onClick={() => {
          setError("");
          setNewForm({
            customer: "", order_number: newOrderNumber(), notes: "",
            product: "", quantity: "1", unit_price: "", discount_amount: "0",
          });
          setModal("create");
        }}><Plus size={15} /> New order</button>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      {notice && <div className="alert alert-success" role="status">{notice}<button type="button" onClick={() => setNotice("")} style={{ float: "right", border: 0, background: "transparent", color: "inherit" }}>Dismiss</button></div>}
      <section className="panel">
        <div className="toolbar">
          <div className="stat-label"><ClipboardList size={14} /> {orders.length} orders</div>
          <button className="btn btn-quiet btn-small" type="button" onClick={refresh} style={{ marginLeft: "auto" }}><RefreshCw size={13} /> Refresh</button>
        </div>
        {loading ? <Loading /> : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Order no.</th><th>Customer</th><th>Order date</th><th>Lines</th><th>Total</th><th>Status</th><th>Actions</th></tr></thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id}>
                    <td><strong>{order.order_number}</strong></td>
                    <td>{order.customer_name}</td>
                    <td>{formatDate(order.order_date)}</td>
                    <td>{order.items?.length || 0}</td>
                    <td>{formatMoney(order.total_amount, currency)}</td>
                    <td><StatusBadge value={order.status} /></td>
                    <td>
                      <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                        {order.status === "DRAFT" && <>
                          <button className="btn btn-secondary btn-small" type="button" onClick={() => {
                            setTarget(order);
                            setItemForm({ product: "", quantity: "1", unit_price: "", discount_amount: "0" });
                            setModal("item");
                          }} title="Add a line"><CirclePlus size={13} /> Line</button>
                          <button className="btn btn-small" type="button" onClick={() => transition(order, "submit")} disabled={busy}><CheckCircle2 size={13} /> Submit</button>
                          <button className="btn btn-danger btn-small" type="button" onClick={() => transition(order, "cancel")} disabled={busy}><XCircle size={13} /></button>
                        </>}
                        {order.status === "SUBMITTED" && <>
                          <button className="btn btn-small" type="button" disabled={busy || !warehouses.length} onClick={() => {
                            setTarget(order);
                            setWarehouseId(warehouses[0] ? String(warehouses[0].id) : "");
                            setModal("fulfill");
                          }}><Truck size={13} /> Fulfil</button>
                          <button className="btn btn-danger btn-small" type="button" onClick={() => transition(order, "cancel")} disabled={busy}><XCircle size={13} /></button>
                        </>}
                        {order.status !== "DRAFT" && order.status !== "SUBMITTED" && <span className="muted">—</span>}
                      </div>
                    </td>
                  </tr>
                ))}
                {!orders.length && <tr><td colSpan="7"><div className="empty">No orders yet. Create a draft order to begin.</div></td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {modal === "create" && <Modal title="Create draft order" onClose={() => setModal("")}>
        <form onSubmit={createOrder}>
          <div className="form-grid">
            <div className="field"><label htmlFor="order-number">Order number</label><input id="order-number" value={newForm.order_number} onChange={(e) => setNewForm({ ...newForm, order_number: e.target.value })} required maxLength="50" /></div>
            <div className="field"><label htmlFor="order-customer">Customer</label><select id="order-customer" value={newForm.customer} onChange={(e) => setNewForm({ ...newForm, customer: e.target.value })} required><option value="">Select customer</option>{customers.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
            <div className="field"><label htmlFor="order-product">First product line</label><select id="order-product" value={newForm.product} onChange={(e) => updateProduct("product", e.target.value, newForm, setNewForm)}><option value="">Create without lines</option>{products.map((p) => <option key={p.id} value={p.id}>{p.sku} · {p.name}</option>)}</select></div>
            <div className="field"><label htmlFor="order-quantity">Quantity</label><input id="order-quantity" type="number" min="1" step="1" value={newForm.quantity} onChange={(e) => setNewForm({ ...newForm, quantity: e.target.value })} disabled={!newForm.product} /></div>
            <div className="field"><label htmlFor="order-price">Unit price</label><input id="order-price" type="number" min="0" step="0.01" value={newForm.unit_price} onChange={(e) => setNewForm({ ...newForm, unit_price: e.target.value })} required={Boolean(newForm.product)} disabled={!newForm.product} /></div>
            <div className="field"><label htmlFor="order-discount">Line discount</label><input id="order-discount" type="number" min="0" step="0.01" value={newForm.discount_amount} onChange={(e) => setNewForm({ ...newForm, discount_amount: e.target.value })} disabled={!newForm.product} /></div>
          </div>
          <div className="field" style={{ marginTop: 13 }}><label htmlFor="order-notes">Notes</label><textarea id="order-notes" rows="2" value={newForm.notes} onChange={(e) => setNewForm({ ...newForm, notes: e.target.value })} /></div>
          {!customers.length && <div className="alert alert-error" style={{ marginTop: 12 }}>Create a customer before creating an order.</div>}
          <div className="form-actions"><button className="btn btn-quiet" type="button" onClick={() => setModal("")}>Cancel</button><button className="btn" type="submit" disabled={busy || !customers.length}>{busy ? "Creating…" : "Create draft"}</button></div>
        </form>
      </Modal>}

      {modal === "item" && target && <Modal title={"Add line · " + target.order_number} onClose={() => setModal("")}>
        <form onSubmit={addItem}>
          <div className="form-grid">
            <div className="field"><label htmlFor="line-product">Product</label><select id="line-product" value={itemForm.product} onChange={(e) => updateProduct("product", e.target.value, itemForm, setItemForm)} required><option value="">Select product</option>{products.map((p) => <option key={p.id} value={p.id}>{p.sku} · {p.name}</option>)}</select></div>
            <div className="field"><label htmlFor="line-quantity">Quantity</label><input id="line-quantity" type="number" min="1" step="1" value={itemForm.quantity} onChange={(e) => setItemForm({ ...itemForm, quantity: e.target.value })} required /></div>
            <div className="field"><label htmlFor="line-price">Unit price</label><input id="line-price" type="number" min="0" step="0.01" value={itemForm.unit_price} onChange={(e) => setItemForm({ ...itemForm, unit_price: e.target.value })} required /></div>
            <div className="field"><label htmlFor="line-discount">Discount</label><input id="line-discount" type="number" min="0" step="0.01" value={itemForm.discount_amount} onChange={(e) => setItemForm({ ...itemForm, discount_amount: e.target.value })} /></div>
          </div>
          <div className="form-actions"><button className="btn btn-quiet" type="button" onClick={() => setModal("")}>Cancel</button><button className="btn" type="submit" disabled={busy}>{busy ? "Saving…" : "Add line"}</button></div>
        </form>
      </Modal>}

      {modal === "fulfill" && target && <Modal title={"Fulfil · " + target.order_number} onClose={() => setModal("")}>
        <form onSubmit={(event) => { event.preventDefault(); transition(target, "fulfill", { warehouse_id: Number(warehouseId) }); }}>
          <div className="field"><label htmlFor="fulfil-warehouse">Dispatch warehouse</label><select id="fulfil-warehouse" value={warehouseId} onChange={(e) => setWarehouseId(e.target.value)} required><option value="">Select warehouse</option>{warehouses.map((w) => <option key={w.id} value={w.id}>{w.code} · {w.name}</option>)}</select></div>
          <p className="muted" style={{ fontSize: 11, marginTop: 14 }}>The server verifies available stock and deducts every order line in one transaction. If any line is short, no stock is deducted.</p>
          <div className="form-actions"><button className="btn btn-quiet" type="button" onClick={() => setModal("")}>Cancel</button><button className="btn" type="submit" disabled={busy || !warehouseId}>{busy ? "Processing…" : "Confirm fulfilment"}</button></div>
        </form>
      </Modal>}
    </>
  );
}
