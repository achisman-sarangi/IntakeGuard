import type { IntakeResult } from "../lib/types";

export function DatasetSummary({ result }: { result: IntakeResult }) {
  return (
    <section aria-labelledby="summary-heading">
      <div className="section-heading"><div><span className="eyebrow">Current run</span><h2 id="summary-heading">Run Overview</h2></div><span className="filename">{result.dataset.filename}</span></div>
      <div className="overview-grid">
        <article className="overview-group"><h3>Dataset</h3><dl><div><dd>{result.dataset.row_count}</dd><dt>Rows received</dt></div><div><dd>{result.dataset.column_count}</dd><dt>Columns inspected</dt></div></dl></article>
        <article className="overview-group privacy"><h3>Privacy</h3><dl><div><dd>{result.pii_summary.total_findings}</dd><dt>Sensitive values detected</dt></div><div><dd>{result.manifest.redactions_applied}</dd><dt>Successfully transformed</dt></div><div className="residual-metric"><dd>{result.manifest.residual_pii_findings}</dd><dt>Remaining after rescan</dt></div></dl></article>
        <article className="overview-group"><h3>Quality</h3><dl><div><dd>{result.validation.error_count}</dd><dt>Blocking errors</dt></div><div><dd>{result.validation.warning_count}</dd><dt>Warnings</dt></div></dl></article>
      </div>
    </section>
  );
}
