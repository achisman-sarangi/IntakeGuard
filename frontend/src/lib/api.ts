import type { IntakeResult } from "./types";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/+$/, "")
  ?? "http://127.0.0.1:8000";

interface ErrorBody {
  detail?: unknown;
}

export async function validateDataset(file: File): Promise<IntakeResult> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/intake/validate`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error("The IntakeGuard service is unavailable. Confirm the backend is running.");
  }

  if (!response.ok) {
    let message = `The service returned HTTP ${response.status}.`;
    try {
      const body = await response.json() as ErrorBody;
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // Keep the safe status-based message when the response is not JSON.
    }
    throw new Error(message);
  }

  return await response.json() as IntakeResult;
}

export async function loadSampleFile(filename: string): Promise<File> {
  const response = await fetch(`/samples/${filename}`);
  if (!response.ok) throw new Error("Unable to load the selected sample dataset.");
  return new File([await response.blob()], filename, { type: "text/csv" });
}
