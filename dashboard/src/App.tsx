import { useEffect, useState } from "react";

type Alert = {
  id: number;
  timestamp: string;
  signature: string;
  severity: number;
  src_ip: string | null;
  dest_ip: string | null;
  status: string;
  incident_id: number | null;
};

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function App() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [report, setReport] = useState("");
  const [busy, setBusy] = useState<number | null>(null);

  const load = () =>
    fetch(`${API}/alerts`).then((r) => r.json()).then(setAlerts).catch(() => {});

  useEffect(() => {
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  const generate = async (id: number) => {
    setBusy(id);
    try {
      const r = await fetch(`${API}/alerts/${id}/report`, { method: "POST" });
      const data = await r.json();
      setReport(data.report);
    } finally {
      setBusy(null);
      load();
    }
  };

  return (
    <div style={{ maxWidth: 1000, margin: "2rem auto", fontFamily: "system-ui" }}>
      <h1>Threat Intel Dashboard</h1>
      <table width="100%" cellPadding={8} style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "2px solid #ccc" }}>
            <th>Time</th><th>Signature</th><th>Sev</th><th>Source</th><th>Dest</th><th></th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((a) => (
            <tr key={a.id} style={{ borderBottom: "1px solid #eee" }}>
              <td>{new Date(a.timestamp).toLocaleString()}</td>
              <td>{a.signature}</td>
              <td>{a.severity}</td>
              <td>{a.src_ip}</td>
              <td>{a.dest_ip}</td>
              <td>
                <button onClick={() => generate(a.id)} disabled={busy === a.id}>
                  {busy === a.id ? "Generating..." : "AI report"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {report && (
        <>
          <h2>Incident report</h2>
          <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", color: "#222", padding: 16 }}>
            {report}
          </pre>
        </>
      )}
    </div>
  );
}
