import { useCallback, useEffect, useMemo, useState } from "react";
import { Plus, RefreshCw, Search, SlidersHorizontal } from "lucide-react";
import api, { fetchAll } from "../api";
import Loading from "../components/Loading";
import Modal from "../components/Modal";
import { errorMessage, formatMoney } from "../utils";
import { useAuth } from "../context/AuthContext";

const emptyProduct = {
  sku: "", name: "", category: "", unit_price: "", cost_price: "0",
  reorder_level: "0", description: "",
};

export default function Inventory() {
  const { currency } = useAuth();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [levels, setLevels] = useState([]);
  const [movements, setMovements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [search, setSearch] = useState("");
  const [modal, setModal] = useState("");
  const [productForm, setProductForm] = useState(emptyProduct);
  const [stockForm, setStockForm] = useState({
    product_id: "", warehouse_id: "", movement_type: "IN", quantity: "1",
    reference: "", notes: "",
  });
  const [warehouseForm, setWarehouseForm] = useState({
    name: "", code: "", address: "",
  });
  const [categoryForm, setCategoryForm] = useState({
    name: "", parent: "", description: "",
  });

  const refresh = useCallback(async () => {
    setError("");
    try {
      const [productRows, categoryRows, warehouseRows, levelRows, movementRows] = await Promise.all([
        fetchAll("/inventory/products/"),
        fetchAll("/inventory/categories/"),
        fetchAll("/inventory/warehouses/"),
        fetchAll("/inventory/stock-levels/"),
        fetchAll("/inventory/stock-movements/"),
      ]);
      setProducts(productRows);
      setCategories(categoryRows);
      setWarehouses(warehouseRows);
      setLevels(levelRows);
      setMovements(movementRows);
    } catch (err) {
      setError(errorMessage(err, "Inventory data could not be loaded."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const visibleProducts = useMemo(() => {
    const needle = search.trim().toLowerCase();
    if (!needle) return products;
    return products.filter((item) =>
      [item.sku, item.name, item.category_name].some((value) =>
        String(value || "").toLowerCase().includes(needle)
      )
    );
  }, [products, search]);

  async function createProduct(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.post("/inventory/products/", {
        ...productForm,
        category: productForm.category ? Number(productForm.category) : null,
        unit_price: productForm.unit_price,
        cost_price: productForm.cost_price || "0",
        reorder_level: Number(productForm.reorder_level || 0),
      });
      setModal("");
      setProductForm(emptyProduct);
      setNotice("Product created.");
      await refresh();
    } catch (err) {
      setError(errorMessage(err, "Product could not be created."));
    } finally {
      setBusy(false);
    }
  }

  async function createCategory(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.post("/inventory/categories/", {
        ...categoryForm,
        parent: categoryForm.parent ? Number(categoryForm.parent) : null,
      });
      setModal("");
      setCategoryForm({ name: "", parent: "", description: "" });
      setNotice("Category created.");
      await refresh();
    } catch (err) {
      setError(errorMessage(err, "Category could not be created."));
    } finally {
      setBusy(false);
    }
  }

  async function createWarehouse(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.post("/inventory/warehouses/", warehouseForm);
      setModal("");
      setWarehouseForm({ name: "", code: "", address: "" });
      setNotice("Warehouse created.");
      await refresh();
    } catch (err) {
      setError(errorMessage(err, "Warehouse could not be created."));
    } finally {
      setBusy(false);
    }
  }

  async function adjustStock(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.post("/inventory/stock-movements/adjust_stock/", {
        ...stockForm,
        product_id: Number(stockForm.product_id),
        warehouse_id: Number(stockForm.warehouse_id),
        quantity: Number(stockForm.quantity),
      });
      setModal("");
      setNotice("Stock movement recorded.");
      await refresh();
    } catch (err) {
      setError(errorMessage(err, "Stock movement was rejected."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-heading">
        <div><h1>Inventory</h1><p>Products, stock positions and immutable stock movements.</p></div>
        <div className="toolbar" style={{ margin: 0 }}>
          <button className="btn btn-quiet" type="button" onClick={() => { setError(""); setModal("category"); }}>
            <Plus size={15} /> Add category
          </button>
          <button className="btn btn-quiet" type="button" onClick={() => { setError(""); setModal("warehouse"); }}>
            <Plus size={15} /> Add warehouse
          </button>
          <button className="btn btn-secondary" type="button" onClick={() => { setError(""); setModal("stock"); }}>
            <SlidersHorizontal size={15} /> Adjust stock
          </button>
          <button className="btn" type="button" onClick={() => { setError(""); setProductForm(emptyProduct); setModal("product"); }}>
            <Plus size={15} /> Add product
          </button>
        </div>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      {notice && <div className="alert alert-success" role="status">{notice}<button type="button" onClick={() => setNotice("")} style={{ float: "right", border: 0, background: "transparent", color: "inherit" }}>Dismiss</button></div>}
      <section className="panel">
        <div className="toolbar">
          <div className="field search-field">
            <label htmlFor="inventory-search">Search products</label>
            <div style={{ position: "relative" }}>
              <Search size={15} style={{ position: "absolute", left: 11, top: 10, color: "#8792a4" }} />
              <input id="inventory-search" style={{ paddingLeft: 34 }} value={search} onChange={(e) => setSearch(e.target.value)} placeholder="SKU, product or category" />
            </div>
          </div>
          <button className="btn btn-quiet btn-small" type="button" onClick={refresh}><RefreshCw size={13} /> Refresh</button>
          <span className="muted" style={{ fontSize: 11, marginLeft: "auto" }}>{visibleProducts.length} products</span>
        </div>
        {loading ? <Loading /> : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>SKU</th><th>Product</th><th>Category</th><th>Unit price</th><th>On hand</th><th>Reorder at</th><th>Status</th></tr></thead>
              <tbody>
                {visibleProducts.map((product) => (
                  <tr key={product.id}>
                    <td><strong>{product.sku}</strong></td>
                    <td>{product.name}</td>
                    <td>{product.category_name || "—"}</td>
                    <td>{formatMoney(product.unit_price, currency)}</td>
                    <td>{Number(product.total_stock || 0).toLocaleString()}</td>
                    <td>{product.reorder_level}</td>
                    <td><span className={"status " + (product.is_active ? "FULFILLED" : "CANCELLED")}>{product.is_active ? "ACTIVE" : "INACTIVE"}</span></td>
                  </tr>
                ))}
                {!visibleProducts.length && <tr><td colSpan="7"><div className="empty">{search ? "No products match your search." : "No products yet. Add your first product to begin."}</div></td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <section className="panel" style={{ marginTop: 16 }}>
        <h2>Warehouse stock positions</h2>
        <div className="table-wrap">
          <table>
            <thead><tr><th>SKU</th><th>Product</th><th>Warehouse</th><th>On hand</th><th>Reserved</th><th>Available</th></tr></thead>
            <tbody>
              {levels.map((level) => (
                <tr key={level.id}>
                  <td>{level.product_sku}</td><td>{level.product_name}</td>
                  <td>{level.warehouse_name}</td><td>{level.quantity}</td>
                  <td>{level.reserved_quantity}</td><td><strong>{level.available_quantity}</strong></td>
                </tr>
              ))}
              {!levels.length && <tr><td colSpan="6"><div className="empty">No warehouse stock has been recorded.</div></td></tr>}
            </tbody>
          </table>
        </div>
      </section>


      <section className="panel" style={{ marginTop: 16 }}>
        <h2>Stock movement ledger</h2>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Date</th><th>Type</th><th>SKU</th><th>Product</th><th>Warehouse</th><th>Quantity</th><th>Reference</th><th>Performed by</th></tr></thead>
            <tbody>
              {movements.map((movement) => (
                <tr key={movement.id}>
                  <td>{new Date(movement.created_at).toLocaleString()}</td>
                  <td><span className="status">{movement.movement_type}</span></td>
                  <td>{movement.product_sku}</td>
                  <td>{movement.product_name}</td>
                  <td>{movement.warehouse_name}</td>
                  <td>{movement.quantity}</td>
                  <td>{movement.reference || "—"}</td>
                  <td>{movement.performed_by || "—"}</td>
                </tr>
              ))}
              {!movements.length && <tr><td colSpan="8"><div className="empty">No stock movements have been recorded.</div></td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      {modal === "product" && (
        <Modal title="Add product" onClose={() => setModal("")}>
          <form onSubmit={createProduct}>
            <div className="form-grid">
              <div className="field"><label htmlFor="sku">SKU</label><input id="sku" value={productForm.sku} onChange={(e) => setProductForm({ ...productForm, sku: e.target.value })} required maxLength="50" /></div>
              <div className="field"><label htmlFor="product-name">Product name</label><input id="product-name" value={productForm.name} onChange={(e) => setProductForm({ ...productForm, name: e.target.value })} required maxLength="200" /></div>
              <div className="field"><label htmlFor="product-category">Category</label><select id="product-category" value={productForm.category} onChange={(e) => setProductForm({ ...productForm, category: e.target.value })}><option value="">Uncategorized</option>{categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
              <div className="field"><label htmlFor="unit-price">Unit price</label><input id="unit-price" type="number" min="0" step="0.01" value={productForm.unit_price} onChange={(e) => setProductForm({ ...productForm, unit_price: e.target.value })} required /></div>
              <div className="field"><label htmlFor="cost-price">Cost price</label><input id="cost-price" type="number" min="0" step="0.01" value={productForm.cost_price} onChange={(e) => setProductForm({ ...productForm, cost_price: e.target.value })} /></div>
              <div className="field"><label htmlFor="reorder-level">Reorder level</label><input id="reorder-level" type="number" min="0" step="1" value={productForm.reorder_level} onChange={(e) => setProductForm({ ...productForm, reorder_level: e.target.value })} /></div>
            </div>
            <div className="field" style={{ marginTop: 13 }}><label htmlFor="product-description">Description</label><textarea id="product-description" rows="3" value={productForm.description} onChange={(e) => setProductForm({ ...productForm, description: e.target.value })} /></div>
            <div className="form-actions"><button className="btn btn-quiet" type="button" onClick={() => setModal("")}>Cancel</button><button className="btn" type="submit" disabled={busy}>{busy ? "Saving…" : "Create product"}</button></div>
          </form>
        </Modal>
      )}

      {modal === "category" && (
        <Modal title="Add product category" onClose={() => setModal("")}>
          <form onSubmit={createCategory}>
            <div className="form-grid">
              <div className="field"><label htmlFor="category-name">Category name</label><input id="category-name" value={categoryForm.name} onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })} required maxLength="100" /></div>
              <div className="field"><label htmlFor="category-parent">Parent category</label><select id="category-parent" value={categoryForm.parent} onChange={(e) => setCategoryForm({ ...categoryForm, parent: e.target.value })}><option value="">No parent</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></div>
            </div>
            <div className="field" style={{ marginTop: 13 }}><label htmlFor="category-description">Description</label><textarea id="category-description" rows="3" value={categoryForm.description} onChange={(e) => setCategoryForm({ ...categoryForm, description: e.target.value })} /></div>
            <div className="form-actions"><button className="btn btn-quiet" type="button" onClick={() => setModal("")}>Cancel</button><button className="btn" type="submit" disabled={busy}>{busy ? "Saving…" : "Create category"}</button></div>
          </form>
        </Modal>
      )}

      {modal === "warehouse" && (
        <Modal title="Add warehouse" onClose={() => setModal("")}>
          <form onSubmit={createWarehouse}>
            <div className="form-grid">
              <div className="field"><label htmlFor="warehouse-name">Warehouse name</label><input id="warehouse-name" value={warehouseForm.name} onChange={(e) => setWarehouseForm({ ...warehouseForm, name: e.target.value })} required maxLength="100" /></div>
              <div className="field"><label htmlFor="warehouse-code">Warehouse code</label><input id="warehouse-code" value={warehouseForm.code} onChange={(e) => setWarehouseForm({ ...warehouseForm, code: e.target.value.toUpperCase() })} required maxLength="20" /></div>
            </div>
            <div className="field" style={{ marginTop: 13 }}><label htmlFor="warehouse-address">Address</label><textarea id="warehouse-address" rows="3" value={warehouseForm.address} onChange={(e) => setWarehouseForm({ ...warehouseForm, address: e.target.value })} /></div>
            <div className="form-actions"><button className="btn btn-quiet" type="button" onClick={() => setModal("")}>Cancel</button><button className="btn" type="submit" disabled={busy}>{busy ? "Saving…" : "Create warehouse"}</button></div>
          </form>
        </Modal>
      )}

      {modal === "stock" && (
        <Modal title="Record stock movement" onClose={() => setModal("")}>
          {!warehouses.length && <div className="alert alert-error">Create an active warehouse before recording stock.</div>}
          <form onSubmit={adjustStock}>
            <div className="form-grid">
              <div className="field"><label htmlFor="stock-product">Product</label><select id="stock-product" value={stockForm.product_id} onChange={(e) => setStockForm({ ...stockForm, product_id: e.target.value })} required><option value="">Select product</option>{products.filter((p) => p.is_active).map((p) => <option key={p.id} value={p.id}>{p.sku} · {p.name}</option>)}</select></div>
              <div className="field"><label htmlFor="stock-warehouse">Warehouse</label><select id="stock-warehouse" value={stockForm.warehouse_id} onChange={(e) => setStockForm({ ...stockForm, warehouse_id: e.target.value })} required><option value="">Select warehouse</option>{warehouses.filter((w) => w.is_active).map((w) => <option key={w.id} value={w.id}>{w.code} · {w.name}</option>)}</select></div>
              <div className="field"><label htmlFor="movement-type">Movement type</label><select id="movement-type" value={stockForm.movement_type} onChange={(e) => setStockForm({ ...stockForm, movement_type: e.target.value })}><option value="IN">Stock in</option><option value="OUT">Stock out</option><option value="ADJUSTMENT">Set on-hand quantity</option></select></div>
              <div className="field"><label htmlFor="movement-quantity">{stockForm.movement_type === "ADJUSTMENT" ? "New on-hand quantity" : "Quantity"}</label><input id="movement-quantity" type="number" min={stockForm.movement_type === "ADJUSTMENT" ? "0" : "1"} step="1" value={stockForm.quantity} onChange={(e) => setStockForm({ ...stockForm, quantity: e.target.value })} required /></div>
              <div className="field"><label htmlFor="stock-reference">Reference</label><input id="stock-reference" value={stockForm.reference} onChange={(e) => setStockForm({ ...stockForm, reference: e.target.value })} maxLength="100" /></div>
              <div className="field"><label htmlFor="stock-notes">Notes</label><input id="stock-notes" value={stockForm.notes} onChange={(e) => setStockForm({ ...stockForm, notes: e.target.value })} /></div>
            </div>
            <p className="muted" style={{ fontSize: 10 }}>Every stock change is saved as an immutable ledger entry. Incorrect entries must be corrected with a compensating movement.</p>
            <div className="form-actions"><button className="btn btn-quiet" type="button" onClick={() => setModal("")}>Cancel</button><button className="btn" type="submit" disabled={busy || !products.length || !warehouses.length}>{busy ? "Recording…" : "Record movement"}</button></div>
          </form>
        </Modal>
      )}
    </>
  );
}
