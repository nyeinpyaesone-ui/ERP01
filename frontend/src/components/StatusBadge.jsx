export default function StatusBadge({ value }) {
  const status = String(value || "UNKNOWN").toUpperCase();
  return <span className={"status " + status}>{status.replaceAll("_", " ")}</span>;
}
