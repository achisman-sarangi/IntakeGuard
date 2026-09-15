export type DatasetChoice = "dirty" | "clean" | "upload";

interface Props {
  choice: DatasetChoice;
  file: File | null;
  loading: boolean;
  onChoiceChange: (choice: DatasetChoice) => void;
  onFileChange: (file: File | null) => void;
  onRun: () => void;
}

const demos = [
  { value: "dirty" as const, title: "Dirty Manufacturing Dataset", records: "26 records", detail: "Synthetic manufacturing operations data. Contains integrity failures.", outcome: "BLOCKED" },
  { value: "clean" as const, title: "Clean Manufacturing Dataset", records: "10 records", detail: "Validated manufacturing operations data with synthetic sensitive values.", outcome: "READY" },
];

export function DatasetSelector({ choice, file, loading, onChoiceChange, onFileChange, onRun }: Props) {
  return (
    <section className="control-panel" aria-labelledby="dataset-heading">
      <div className="section-heading"><div><span className="eyebrow">Dataset source</span><h2 id="dataset-heading">Dataset Intake</h2></div><span className="limit-note">CSV / 5 MB limit</span></div>
      <div className="dataset-options">{demos.map((item) => (
        <label className={`dataset-option ${choice === item.value ? "selected" : ""}`} key={item.value}>
          <input type="radio" name="dataset" checked={choice === item.value} onChange={() => onChoiceChange(item.value)} disabled={loading} />
          <span className="dataset-copy"><strong>{item.title}</strong><span className="record-count">{item.records}</span><small>{item.detail}</small></span>
          <span className={`expected-badge ${item.outcome.toLowerCase()}`}>{item.outcome}</span>
        </label>
      ))}</div>
      <div className="upload-row">
        <label className={`upload-choice ${choice === "upload" ? "selected" : ""}`}><input type="radio" name="dataset" checked={choice === "upload"} onChange={() => onChoiceChange("upload")} disabled={loading} /><span><strong>Upload CSV</strong><small>Use your own dataset (maximum 5 MB)</small></span></label>
        {choice === "upload" && <div className="file-control"><label className="file-button" htmlFor="csv-upload">Choose file</label><input id="csv-upload" type="file" accept=".csv,text/csv" disabled={loading} onChange={(event) => onFileChange(event.target.files?.[0] ?? null)} /><span>{file ? `${file.name} / ${(file.size / 1024).toFixed(1)} KB` : "No file selected"}</span></div>}
      </div>
      <div className="run-row"><div><strong>Ready to process</strong><p>Profile, de-identify, validate and gate this dataset.</p></div><button className="primary-button" type="button" onClick={onRun} disabled={loading || (choice === "upload" && !file)}>{loading ? <><span className="spinner" aria-hidden="true" />Inspecting dataset...</> : "Run Guardrail"}</button></div>
      {loading && <p className="processing-note" role="status">Detecting sensitive data / Applying deterministic redaction / Validating transformed output</p>}
    </section>
  );
}
