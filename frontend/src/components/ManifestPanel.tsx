import type { TransformationManifest } from "../lib/types";

export function ManifestPanel({ manifest, runId }: { manifest: TransformationManifest; runId: string }) {
  const fields = [["Dataset", manifest.dataset], ["Rows received", manifest.rows_received], ["Rows released", manifest.rows_output], ["Columns", manifest.columns_received], ["Sensitive findings", manifest.sensitive_findings_detected], ["Transformations applied", manifest.redactions_applied], ["Residual PII", manifest.residual_pii_findings], ["Validation errors", manifest.validation_errors], ["Validation warnings", manifest.validation_warnings], ["Final gate", manifest.status]];
  return (
    <section className="panel manifest-panel" aria-labelledby="manifest-heading">
      <div className="section-heading"><div><span className="eyebrow">Audit record / Run {runId}</span><h2 id="manifest-heading">Audit &amp; Transformation Record</h2><p>A deterministic record of what IntakeGuard inspected, transformed and validated during this run.</p></div><span className={`status-pill ${manifest.status.toLowerCase()}`}>{manifest.status}</span></div>
      <div className="manifest-layout"><dl className="manifest-grid">{fields.map(([name, value]) => <div key={name}><dt>{name}</dt><dd>{value}</dd></div>)}</dl><div className="operations"><h3>Transformation operations</h3><table className="transformation-table"><tbody>{manifest.transformations.map((item) => <tr key={item.type}><td>{item.type}</td><td>{item.count}</td></tr>)}</tbody></table></div></div>
      <details className="raw-manifest"><summary>View raw manifest</summary><pre>{JSON.stringify(manifest, null, 2)}</pre></details>
    </section>
  );
}
