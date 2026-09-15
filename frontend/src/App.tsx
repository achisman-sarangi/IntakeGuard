import { useState } from "react";
import { DatasetSelector, type DatasetChoice } from "./components/DatasetSelector";
import { DatasetSummary } from "./components/DatasetSummary";
import { Header } from "./components/Header";
import { ManifestPanel } from "./components/ManifestPanel";
import { PipelineStrip } from "./components/PipelineStrip";
import { RedactionPreview } from "./components/RedactionPreview";
import { SensitiveDataSummary } from "./components/SensitiveDataSummary";
import { StatusBanner } from "./components/StatusBanner";
import { ValidationPanel } from "./components/ValidationPanel";
import { loadSampleFile, validateDataset } from "./lib/api";
import type { IntakeResult } from "./lib/types";

const samples: Record<Exclude<DatasetChoice, "upload">, string> = { dirty: "manufacturing_work_orders.csv", clean: "manufacturing_work_orders_clean.csv" };
function createRunId(): string { const bytes = new Uint8Array(3); crypto.getRandomValues(bytes); return `IG-${Array.from(bytes, (value) => value.toString(16).padStart(2, "0")).join("").toUpperCase()}`; }

export default function App() {
  const [choice, setChoice] = useState<DatasetChoice>("dirty");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<IntakeResult | null>(null);
  const [runId, setRunId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runIntake() {
    const nextRunId = createRunId();
    setRunId(nextRunId); setLoading(true); setError(null);
    try {
      const selected = choice === "upload" ? file : await loadSampleFile(samples[choice]);
      if (!selected) throw new Error("Choose a CSV file before running IntakeGuard.");
      if (!selected.name.toLowerCase().endsWith(".csv")) throw new Error("Only .csv files are supported.");
      if (selected.size === 0) throw new Error("The selected CSV file is empty.");
      setResult(await validateDataset(selected));
    } catch (caught: unknown) { setResult(null); setError(caught instanceof Error ? caught.message : "An unexpected error occurred."); }
    finally { setLoading(false); }
  }

  return (
    <div className="app-shell"><Header /><PipelineStrip completed={result !== null} /><main><DatasetSelector choice={choice} file={file} loading={loading} onChoiceChange={(next) => { setChoice(next); setError(null); }} onFileChange={setFile} onRun={runIntake} />{error && <div className="error-alert" role="alert"><strong>Unable to process dataset.</strong><span>{error}</span></div>}{!result && !loading && !error && <section className="empty-state"><span className="eyebrow">Deterministic intake control</span><h2>Enterprise data enters here.</h2><p>IntakeGuard profiles the dataset, identifies sensitive values, applies deterministic transformations, rescans the output, validates data integrity and decides whether downstream release is permitted.</p><div className="empty-workflow">Inspect <span>→</span> Detect <span>→</span> Redact <span>→</span> Rescan <span>→</span> Validate <span>→</span> Gate</div></section>}{result && <div className="results"><StatusBanner result={result} runId={runId} /><DatasetSummary result={result} /><SensitiveDataSummary summary={result.pii_summary} /><RedactionPreview preview={result.preview} /><ValidationPanel findings={result.validation.findings} /><ManifestPanel manifest={result.manifest} runId={runId} /></div>}</main><footer><span>IntakeGuard / Enterprise Intake Control</span><span>Deterministic processing / No data persistence</span></footer></div>
  );
}
