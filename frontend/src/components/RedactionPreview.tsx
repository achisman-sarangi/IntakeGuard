import { useEffect, useState } from "react";
import type { RedactionPreview as Preview } from "../lib/types";

const preferredColumns = ["work_order_id", "technician_name", "technician_email", "phone_number", "machine_id", "facility", "failure_notes"];
const labels: Record<string, string> = { work_order_id: "Work order", technician_name: "Technician", technician_email: "Email", phone_number: "Phone", machine_id: "Machine", facility: "Facility", failure_notes: "Failure notes" };

function RecordView({ row, original }: { row: Record<string, string>; original?: Record<string, string> }) {
  const columns = [...preferredColumns.filter((column) => column in row), ...Object.keys(row).filter((column) => !preferredColumns.includes(column))];
  return <dl className="record-fields">{columns.map((column) => {
    const changed = original !== undefined && original[column] !== row[column];
    return <div className={column === "failure_notes" ? "wide-field" : ""} key={column}><dt>{labels[column] ?? column.replaceAll("_", " ")}</dt><dd className={changed ? "transformed-value" : ""}>{row[column] || <span className="empty-value">Empty</span>}</dd></div>;
  })}</dl>;
}

export function RedactionPreview({ preview }: { preview: Preview }) {
  const [index, setIndex] = useState(0);
  useEffect(() => setIndex(0), [preview]);
  const total = Math.min(preview.before.length, preview.after.length);
  if (!total) return null;
  return (
    <section className="panel preview-panel" aria-labelledby="preview-heading">
      <div className="section-heading"><div><span className="eyebrow">Transformation proof</span><h2 id="preview-heading">Redaction Preview</h2><p>Operational context is preserved while configured sensitive values are replaced.</p></div><div className="record-nav"><span>Record {index + 1} of {total}</span><button type="button" onClick={() => setIndex((value) => value - 1)} disabled={index === 0} aria-label="Previous preview record">Previous</button><button type="button" onClick={() => setIndex((value) => value + 1)} disabled={index === total - 1} aria-label="Next preview record">Next</button></div></div>
      <div className="preview-grid"><article className="record-card original"><h3>Original record</h3><RecordView row={preview.before[index]} /></article><article className="record-card transformed"><h3>Transformed record</h3><RecordView row={preview.after[index]} original={preview.before[index]} /></article></div>
    </section>
  );
}
