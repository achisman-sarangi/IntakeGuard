const stages = ["Inspect", "Detect", "Redact", "Rescan", "Validate", "Gate"];

export function PipelineStrip({ completed }: { completed: boolean }) {
  return (
    <section className={`pipeline ${completed ? "completed" : ""}`} aria-label="IntakeGuard processing pipeline">
      <div className="pipeline-inner">
        <div className="pipeline-stages">{stages.map((stage, index) => <div className="pipeline-stage" key={stage}><span>{String(index + 1).padStart(2, "0")}</span><strong>{stage}</strong></div>)}</div>
        <p>Customer dataset <span aria-hidden="true">→</span> deterministic guardrails <span aria-hidden="true">→</span> downstream-ready data</p>
      </div>
    </section>
  );
}
