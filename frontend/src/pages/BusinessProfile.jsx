import { useEffect, useState } from "react";
import { Building2, Save } from "lucide-react";
import api from "../api";
import Loading from "../components/Loading";
import { useAuth } from "../context/AuthContext";
import { errorMessage } from "../utils";

const empty = {
  business_name: "", legal_name: "", email: "", phone: "", address: "",
  tax_number: "", currency: "MMK", timezone: "Asia/Yangon", locale: "my-MM",
};

export default function BusinessProfile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(empty);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let active = true;
    api.get("/business-profile/")
      .then(({ data }) => { if (active) setProfile(data); })
      .catch((err) => { if (active) setError(errorMessage(err, "Business profile could not be loaded.")); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  async function save(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const { data } = await api.patch("/business-profile/", profile);
      setProfile(data);
      setNotice("Business profile saved.");
    } catch (err) {
      setError(errorMessage(err, "Profile changes could not be saved."));
    } finally {
      setBusy(false);
    }
  }

  const canEdit = Boolean(user?.is_staff || user?.is_superuser);

  return (
    <>
      <div className="page-heading">
        <div><h1>Business profile</h1><p>Company identity, currency and locale settings for this ERP deployment.</p></div>
        <span className="status">{canEdit ? "ADMIN ACCESS" : "READ ONLY"}</span>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      {notice && <div className="alert alert-success" role="status">{notice}</div>}
      {loading ? <Loading /> : (
        <section className="panel" style={{ maxWidth: 850 }}>
          <h2><Building2 size={16} style={{ verticalAlign: "middle", marginRight: 7 }} /> Company details</h2>
          {!canEdit && <p className="muted" style={{ fontSize: 11 }}>Only staff users can change these settings. Contact your ERP administrator to request an update.</p>}
          <form onSubmit={save}>
            <div className="form-grid">
              <div className="field"><label htmlFor="business-name">Business name</label><input id="business-name" value={profile.business_name} onChange={(e) => setProfile({ ...profile, business_name: e.target.value })} required maxLength="200" disabled={!canEdit} /></div>
              <div className="field"><label htmlFor="legal-name">Legal name</label><input id="legal-name" value={profile.legal_name || ""} onChange={(e) => setProfile({ ...profile, legal_name: e.target.value })} maxLength="200" disabled={!canEdit} /></div>
              <div className="field"><label htmlFor="business-email">Email</label><input id="business-email" type="email" value={profile.email || ""} onChange={(e) => setProfile({ ...profile, email: e.target.value })} disabled={!canEdit} /></div>
              <div className="field"><label htmlFor="business-phone">Phone</label><input id="business-phone" value={profile.phone || ""} onChange={(e) => setProfile({ ...profile, phone: e.target.value })} maxLength="30" disabled={!canEdit} /></div>
              <div className="field"><label htmlFor="tax-number">Tax number</label><input id="tax-number" value={profile.tax_number || ""} onChange={(e) => setProfile({ ...profile, tax_number: e.target.value })} maxLength="80" disabled={!canEdit} /></div>
              <div className="field"><label htmlFor="currency">Currency code</label><input id="currency" value={profile.currency} onChange={(e) => setProfile({ ...profile, currency: e.target.value.toUpperCase() })} minLength="3" maxLength="3" pattern="[A-Z]{3}" disabled={!canEdit} required /></div>
              <div className="field"><label htmlFor="timezone">Time zone</label><input id="timezone" value={profile.timezone} onChange={(e) => setProfile({ ...profile, timezone: e.target.value })} maxLength="64" disabled={!canEdit} required /></div>
              <div className="field"><label htmlFor="locale">Locale</label><input id="locale" value={profile.locale} onChange={(e) => setProfile({ ...profile, locale: e.target.value })} maxLength="10" disabled={!canEdit} required /></div>
            </div>
            <div className="field" style={{ marginTop: 13 }}><label htmlFor="business-address">Business address</label><textarea id="business-address" rows="3" value={profile.address || ""} onChange={(e) => setProfile({ ...profile, address: e.target.value })} disabled={!canEdit} /></div>
            {canEdit && <div className="form-actions"><button className="btn" type="submit" disabled={busy}><Save size={14} /> {busy ? "Saving…" : "Save profile"}</button></div>}
          </form>
          <p className="muted" style={{ fontSize: 10, marginTop: 16 }}>Last updated: {profile.updated_at ? new Date(profile.updated_at).toLocaleString() : "Not yet saved"} · {profile.updated_by || "System default"}</p>
        </section>
      )}
    </>
  );
}
