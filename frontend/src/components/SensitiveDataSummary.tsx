import type { PiiSummary } from "../lib/types";

export function SensitiveDataSummary({ summary }: { summary: PiiSummary }) {
  const items = [["Person names", summary.name_findings, "NM"], ["Email addresses", summary.email_findings, "@"], ["Phone numbers", summary.phone_findings, "PH"], ["SSNs", summary.ssn_findings, "ID"], ["IP addresses", summary.ip_findings, "IP"]] as const;
  return (
    <section className="panel" aria-labelledby="sensitive-heading"><div className="section-heading"><div><span className="eyebrow">Privacy</span><h2 id="sensitive-heading">Sensitive Data Detected</h2></div><span className="finding-total">{summary.total_findings} findings</span></div><div className="pii-grid">{items.map(([label, count, icon]) => <div className="pii-item" key={label}><span className="pii-icon">{icon}</span><span><strong>{count}</strong><small>{label}</small></span></div>)}</div><p className="section-note">Detection is deterministic and based on configured column classifications and validated value patterns.</p></section>
  );
}
