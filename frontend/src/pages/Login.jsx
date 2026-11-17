import { useState } from "react";
import { Boxes, LockKeyhole } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(username.trim(), password);
    } catch {
      setError("Sign-in failed. Check your username and password, then try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-screen">
      <section className="login-card" aria-labelledby="login-title">
        <div className="brand">
          <div className="brand-mark"><Boxes size={20} /></div>
          <div><strong>ERP01</strong><small>Business Suite</small></div>
        </div>
        <h1 id="login-title">Welcome back</h1>
        <p>Sign in to manage your business operations.</p>
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        <form className="login-form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="username">Username</label>
            <input id="username" name="username" autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input id="password" name="password" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button className="btn" type="submit" disabled={busy}>
            <LockKeyhole size={15} /> {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className="muted" style={{ marginTop: 22, marginBottom: 0, fontSize: 11 }}>
          Access is managed by your ERP administrator.
        </p>
      </section>
    </main>
  );
}
