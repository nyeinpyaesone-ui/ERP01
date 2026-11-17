import { useEffect, useState } from "react";
import { Download, FileBarChart } from "lucide-react";
import api from "../api";
import Loading from "../components/Loading";
import { errorMessage, formatMoney } from "../utils";

export default function Reports() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    api.get("/dashboard/")
      .then(({ data }) => { if (active) setSummary(data); })
      .catch((err) => { if (active) setError(errorMessage(err)); });
    return () => { active = false; };
  }, []);

  function exportSnapshot() {
    if (!summary) return;
    const rows = [
      ["Metric", "Value", "Currency"],
      ["Fulfilled sales today", summary.fulfilled_sales_today, summary.currency],
      ["Fulfilled sales this month", summary.fulfilled_sales_this_month, summary.currency],
      ["Orders today", summary.orders_today, ""],
      ["Open orders", summary.open_orders, ""],
      ["Active customers", summary.customers, ""],
      ["Active products", summary.active_products, ""],
      ["Low-stock products", summary.low_stock_products, ""],
    ];
    const csv = rows.map((row) => row.map((cell) => '"' + String(cell ?? "").replaceAll('"', '""') + '"').join(",")).join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "erp01-dashboard-summary.csv";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <>
      <div className="page-heading">
        <div><h1>Reports</h1><p>Export current operational summary from committed ERP records.</p></div>
        <button className="btn btn-secondary" type="button" onClick={exportSnapshot} disabled={!summary}><Download size={15} /> Export CSV</button>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      {!summary && !error && <Loading />}
      {summary && (
        <section className="panel">
          <h2><FileBarChart size={16} style={{ verticalAlign: "middle", marginRight: 7 }} /> Operational summary</h2>
          <div className="table-wrap">
            <table><tbody>
              <tr><th>Fulfilled sales · Today</th><td>{formatMoney(summary.fulfilled_sales_today, summary.currency)}</td></tr>
              <tr><th>Fulfilled sales · This month</th><td>{formatMoney(summary.fulfilled_sales_this_month, summary.currency)}</td></tr>
              <tr><th>Orders · Today</th><td>{summary.orders_today}</td></tr>
              <tr><th>Open orders</th><td>{summary.open_orders}</td></tr>
              <tr><th>Active customers</th><td>{summary.customers}</td></tr>
              <tr><th>Active products</th><td>{summary.active_products}</td></tr>
              <tr><th>Low-stock products</th><td>{summary.low_stock_products}</td></tr>
            </tbody></table>
          </div>
          <p className="muted" style={{ fontSize: 11, marginTop: 18 }}>
            Sales totals represent fulfilled order line values. They are not cash-received figures because customer payment tracking is not implemented in this release.
          </p>
        </section>
      )}
    </>
  );
}
