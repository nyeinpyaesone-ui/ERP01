export default function Loading({ label = "Loading data…" }) {
  return <div role="status" aria-live="polite"><div className="spinner" /><p className="muted" style={{ textAlign: "center", fontSize: 12 }}>{label}</p></div>;
}
