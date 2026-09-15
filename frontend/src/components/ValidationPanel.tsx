import type { ValidationFinding, ValidationSeverity } from "../lib/types";

const priority: Record<ValidationSeverity, number> = { ERROR: 0, WARNING: 1, INFO: 2 };
function label(code: ValidationFinding["code"]): string { return code.toLowerCase().split("_").map((word) => word[0].toUpperCase() + word.slice(1)).join(" "); }

export function ValidationPanel({ findings }: { findings: ValidationFinding[] }) {
  const sorted = [...findings].sort((a, b) => priority[a.severity] - priority[b.severity] || a.row_index - b.row_index);
  const blocking = findings.filter((finding) => finding.severity === "ERROR").length;
  return (
    <section className="panel" aria-labelledby="validation-heading">
      <div className="section-heading"><div><span className="eyebrow">Quality gate</span><h2 id="validation-heading">{blocking ? `${blocking} blocking ${blocking === 1 ? "issue" : "issues"}` : "All integrity checks passed"}</h2></div>{findings.length > 0 && <span className="finding-total">{findings.length} findings</span>}</div>
      {sorted.length === 0 ? <ul className="check-list"><li>Required identifiers present</li><li>Identifier uniqueness verified</li><li>Numeric fields valid</li><li>No blocking structural issues</li></ul> : <div className="finding-list">{sorted.map((finding, index) => <article className={`finding ${finding.severity.toLowerCase()}`} key={`${finding.code}-${finding.row_index}-${index}`}><span className={`severity ${finding.severity.toLowerCase()}`}>{finding.severity}</span><div><h3>{label(finding.code)}</h3><p className="finding-location">{finding.column ?? "Dataset"} / Row {finding.row_index}</p><p>{finding.message}</p>{finding.evidence && <small>{finding.evidence}</small>}</div></article>)}</div>}
    </section>
  );
}
