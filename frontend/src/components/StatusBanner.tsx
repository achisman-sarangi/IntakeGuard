import type { IntakeResult } from "../lib/types";

export function StatusBanner({ result, runId }: { result: IntakeResult; runId: string }) {
  const ready = result.status === "READY";
  return (
    <section className={`status-banner ${ready ? "ready" : "blocked"}`} aria-live="polite">
      <div className="status-icon" aria-hidden="true">{ready ? "✓" : "!"}</div>
      <div className="status-copy"><div className="decision-meta"><span className="eyebrow">Ingestion decision</span><span>Run {runId}</span></div><h2>{ready ? "READY FOR INGESTION" : "INGESTION BLOCKED"}</h2><p>{ready ? "All configured privacy and integrity guardrails passed." : "This dataset failed configured integrity guardrails and cannot proceed downstream."}</p><strong className="release-state">Downstream release {ready ? "permitted" : "denied"}</strong></div>
      <dl className="status-counts"><div><dt>Blocking issues</dt><dd>{result.validation.error_count}</dd></div><div><dt>{result.validation.warning_count === 1 ? "Warning" : "Warnings"}</dt><dd>{result.validation.warning_count}</dd></div><div><dt>Residual PII</dt><dd>{result.manifest.residual_pii_findings}</dd></div></dl>
    </section>
  );
}
