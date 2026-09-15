export type IngestionStatus = "READY" | "BLOCKED";
export type ValidationSeverity = "ERROR" | "WARNING" | "INFO";
export type PiiType = "EMAIL" | "PHONE" | "SSN" | "IP_ADDRESS" | "PERSON_NAME";

export interface DatasetSummary {
  filename: string;
  row_count: number;
  column_count: number;
}

export interface PiiSummary {
  total_findings: number;
  email_findings: number;
  phone_findings: number;
  ssn_findings: number;
  ip_findings: number;
  name_findings: number;
  rows_affected: number;
}

export interface ValidationFinding {
  code: "RESIDUAL_PII" | "MISSING_REQUIRED_VALUE" | "DUPLICATE_IDENTIFIER" | "DUPLICATE_ROW" | "INVALID_NUMBER";
  severity: ValidationSeverity;
  row_index: number;
  column: string | null;
  message: string;
  sensitive_type: PiiType | null;
  evidence: string | null;
}

export interface ValidationResult {
  error_count: number;
  warning_count: number;
  findings: ValidationFinding[];
  status: IngestionStatus;
}

export interface TransformationCount {
  type: string;
  count: number;
}

export interface TransformationManifest {
  dataset: string;
  rows_received: number;
  rows_output: number;
  columns_received: number;
  sensitive_findings_detected: number;
  redactions_applied: number;
  residual_pii_findings: number;
  validation_errors: number;
  validation_warnings: number;
  transformations: TransformationCount[];
  status: IngestionStatus;
}

export interface RedactionPreview {
  before: Record<string, string>[];
  after: Record<string, string>[];
}

export interface IntakeResult {
  dataset: DatasetSummary;
  pii_summary: PiiSummary;
  validation: ValidationResult;
  manifest: TransformationManifest;
  preview: RedactionPreview;
  status: IngestionStatus;
}
