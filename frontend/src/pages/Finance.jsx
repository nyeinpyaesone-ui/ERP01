import { useCallback, useEffect, useState } from "react";
import { ArrowLeftRight, Plus, RefreshCw, Wallet } from "lucide-react";
import { financeApi } from "../api";
import Loading from "../components/Loading";
import Modal from "../components/Modal";
import { useAuth } from "../context/AuthContext";
import { errorMessage, formatDate, formatMoney } from "../utils";

const emptyAccount = {
  account_id: "", name: "", currency: "MMK", opening_balance: "0.00",
};

export default function Finance() {
  const { currency: defaultCurrency } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [modal, setModal] = useState("");
  const [accountForm, setAccountForm] = useState({
    ...emptyAccount,
    currency: defaultCurrency || "MMK",
  });
  const [transferForm, setTransferForm] = useState({
    from_account: "", to_account: "", amount: "", description: "", reference: "",
  });
  const [transferKey, setTransferKey] = useState("");

  const refresh = useCallback(async () => {
    try {
      setError("");
      const { data } = await financeApi.get("/accounts?limit=500");
      setAccounts(Array.isArray(data) ? data : data.results || []);
    } catch (err) {
      setError(errorMessage(err, "Finance service is not available or your account lacks staff access."));
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshTransactions = useCallback(async (accountId) => {
    if (!accountId) {
      setTransactions([]);
      return;
    }
    try {
      const { data } = await financeApi.get("/transactions/" + encodeURIComponent(accountId));
      setTransactions(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(errorMessage(err, "Transaction history could not be loaded."));
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);
  useEffect(() => { refreshTransactions(selectedAccount); }, [refreshTransactions, selectedAccount]);

  function closeModal() {
    setModal("");
  }

  async function createAccount(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await financeApi.post("/accounts", {
        ...accountForm,
        opening_balance: accountForm.opening_balance || "0.00",
      });
      closeModal();
      setAccountForm({ ...emptyAccount, currency: defaultCurrency || "MMK" });
      setNotice("Finance account created.");
      await refresh();
    } catch (err) {
      setError(errorMessage(err, "Account could not be created."));
    } finally {
      setBusy(false);
    }
  }

  function createIdempotencyKey() {
    const bytes = new Uint8Array(16);
    window.crypto.getRandomValues(bytes);
    return Array.from(bytes, (value) => value.toString(16).padStart(2, "0")).join("");
  }

  async function transfer(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const key = transferKey || createIdempotencyKey();
    setTransferKey(key);
    try {
      await financeApi.post(
        "/transaction",
        {
          ...transferForm,
          amount: transferForm.amount,
        },
        { headers: { "Idempotency-Key": key } },
      );
      setTransferKey("");
      setTransferForm({
        from_account: "", to_account: "", amount: "", description: "", reference: "",
      });
      setNotice("Transfer posted successfully.");
      await refresh();
      if (selectedAccount) await refreshTransactions(selectedAccount);
    } catch (err) {
      setError(errorMessage(err, "Transfer failed. Retry with the same form to safely reuse its idempotency key."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-heading">
        <div><h1>Finance</h1><p>Staff-only accounts, balances and idempotent account transfers.</p></div>
        <div className="toolbar" style={{ margin: 0 }}>
          <button className="btn btn-secondary" type="button" onClick={() => { setTransferKey(""); setModal("transfer"); }} disabled={accounts.length < 2}>
            <ArrowLeftRight size={15} /> New transfer
          </button>
          <button className="btn" type="button" onClick={() => { setError(""); setModal("account"); }}>
            <Plus size={15} /> New account
          </button>
        </div>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      {notice && <div className="alert alert-success" role="status">{notice}<button type="button" onClick={() => setNotice("")} style={{ float: "right", border: 0, background: "transparent", color: "inherit" }}>Dismiss</button></div>}

      <section className="panel">
        <div className="toolbar">
          <h2 style={{ margin: 0 }}><Wallet size={16} style={{ verticalAlign: "middle", marginRight: 7 }} /> Accounts</h2>
          <button className="btn btn-quiet btn-small" type="button" onClick={refresh} style={{ marginLeft: "auto" }}><RefreshCw size={13} /> Refresh</button>
        </div>
        {loading ? <Loading /> : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Account ID</th><th>Name</th><th>Currency</th><th>Balance</th><th>State</th><th>History</th></tr></thead>
              <tbody>
                {accounts.map((account) => (
                  <tr key={account.account_id}>
                    <td><strong>{account.account_id}</strong></td>
                    <td>{account.name}</td>
                    <td>{account.currency}</td>
                    <td>{formatMoney(account.balance, account.currency)}</td>
                    <td><span className={"status " + (account.is_active ? "FULFILLED" : "CANCELLED")}>{account.is_active ? "ACTIVE" : "INACTIVE"}</span></td>
                    <td><button className="btn btn-secondary btn-small" type="button" onClick={() => setSelectedAccount(account.account_id)}>View history</button></td>
                  </tr>
                ))}
                {!accounts.length && <tr><td colSpan="6"><div className="empty">No finance accounts exist yet. Create an account to begin.</div></td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="panel" style={{ marginTop: 16 }}>
        <div className="page-heading" style={{ marginBottom: 12 }}>
          <div><h2 style={{ margin: 0 }}>Transaction history</h2><p>Completed transfers for the selected account.</p></div>
          <div className="field" style={{ minWidth: 220 }}>
            <label htmlFor="finance-history-account">Account</label>
            <select id="finance-history-account" value={selectedAccount} onChange={(e) => setSelectedAccount(e.target.value)}>
              <option value="">Select account</option>
              {accounts.map((account) => <option key={account.account_id} value={account.account_id}>{account.account_id} · {account.name}</option>)}
            </select>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Created</th><th>From</th><th>To</th><th>Amount</th><th>Reference</th><th>Idempotency key</th></tr></thead>
            <tbody>
              {transactions.map((item) => (
                <tr key={item.transaction_id}>
                  <td>{formatDate(item.created_at)}</td>
                  <td>{item.from_account}</td>
                  <td>{item.to_account}</td>
                  <td>{formatMoney(item.amount, item.currency)}</td>
                  <td>{item.reference || "—"}</td>
                  <td>{item.idempotency_key}</td>
                </tr>
              ))}
              {!transactions.length && <tr><td colSpan="6"><div className="empty">{selectedAccount ? "No transfers found for this account." : "Select an account to view transaction history."}</div></td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      {modal === "account" && <Modal title="Create finance account" onClose={closeModal}>
        <form onSubmit={createAccount}>
          <div className="form-grid">
            <div className="field"><label htmlFor="finance-account-id">Account ID</label><input id="finance-account-id" value={accountForm.account_id} onChange={(e) => setAccountForm({ ...accountForm, account_id: e.target.value })} required maxLength="80" /></div>
            <div className="field"><label htmlFor="finance-account-name">Account name</label><input id="finance-account-name" value={accountForm.name} onChange={(e) => setAccountForm({ ...accountForm, name: e.target.value })} required maxLength="160" /></div>
            <div className="field"><label htmlFor="finance-account-currency">Currency</label><input id="finance-account-currency" value={accountForm.currency} onChange={(e) => setAccountForm({ ...accountForm, currency: e.target.value.toUpperCase() })} minLength="3" maxLength="3" pattern="[A-Z]{3}" required /></div>
            <div className="field"><label htmlFor="finance-opening-balance">Opening balance</label><input id="finance-opening-balance" type="number" min="0" step="0.01" value={accountForm.opening_balance} onChange={(e) => setAccountForm({ ...accountForm, opening_balance: e.target.value })} required /></div>
          </div>
          <p className="muted" style={{ fontSize: 11, marginTop: 12 }}>Opening balances are initial account setup values. They are not represented as a transfer or double-entry journal.</p>
          <div className="form-actions"><button className="btn btn-quiet" type="button" onClick={closeModal}>Cancel</button><button className="btn" type="submit" disabled={busy}>{busy ? "Saving…" : "Create account"}</button></div>
        </form>
      </Modal>}

      {modal === "transfer" && <Modal title="Transfer between accounts" onClose={closeModal}>
        <form onSubmit={transfer}>
          <div className="form-grid">
            <div className="field"><label htmlFor="transfer-from">From account</label><select id="transfer-from" value={transferForm.from_account} onChange={(e) => { setTransferKey(""); setTransferForm({ ...transferForm, from_account: e.target.value }); }} required><option value="">Select source</option>{accounts.filter((a) => a.is_active).map((a) => <option key={a.account_id} value={a.account_id}>{a.account_id} · {a.name} ({a.currency})</option>)}</select></div>
            <div className="field"><label htmlFor="transfer-to">To account</label><select id="transfer-to" value={transferForm.to_account} onChange={(e) => { setTransferKey(""); setTransferForm({ ...transferForm, to_account: e.target.value }); }} required><option value="">Select destination</option>{accounts.filter((a) => a.is_active && a.account_id !== transferForm.from_account).map((a) => <option key={a.account_id} value={a.account_id}>{a.account_id} · {a.name} ({a.currency})</option>)}</select></div>
            <div className="field"><label htmlFor="transfer-amount">Amount</label><input id="transfer-amount" type="number" min="0.01" step="0.01" value={transferForm.amount} onChange={(e) => { setTransferKey(""); setTransferForm({ ...transferForm, amount: e.target.value }); }} required /></div>
            <div className="field"><label htmlFor="transfer-reference">Reference</label><input id="transfer-reference" value={transferForm.reference} onChange={(e) => { setTransferKey(""); setTransferForm({ ...transferForm, reference: e.target.value }); }} maxLength="120" /></div>
          </div>
          <div className="field" style={{ marginTop: 13 }}><label htmlFor="transfer-description">Description</label><textarea id="transfer-description" rows="2" value={transferForm.description} onChange={(e) => { setTransferKey(""); setTransferForm({ ...transferForm, description: e.target.value }); }} maxLength="500" /></div>
          <p className="muted" style={{ fontSize: 11, marginTop: 12 }}>Transfers are atomic and require matching account currencies. Retrying an unchanged failed request reuses the same idempotency key.</p>
          <div className="form-actions"><button className="btn btn-quiet" type="button" onClick={closeModal}>Cancel</button><button className="btn" type="submit" disabled={busy || !accounts.length}>{busy ? "Posting…" : "Post transfer"}</button></div>
        </form>
      </Modal>}
    </>
  );
}
