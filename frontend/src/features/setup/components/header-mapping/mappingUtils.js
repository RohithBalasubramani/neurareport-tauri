import {
  VALUE_UNRESOLVED,
  VALUE_SAMPLE,
  VALUE_LATER_SELECTED,
  UNRESOLVED_VALUES,
  COLUMN_REF_REGEX,
  LEGACY_WRAPPER_REGEX,
  REPORT_DATE_PREFIXES,
  REPORT_DATE_KEYWORDS,
  REPORT_SELECTED_EXACT,
  REPORT_SELECTED_KEYWORDS,
  REPORT_SELECTED_SUFFIXES,
  SAMPLE_ALIAS,
  SAMPLE_STATUS_SAMPLE,
  SAMPLE_STATUS_LATER,
  APPROVE_STAGE_LABELS,
} from "./mappingConstants.js";

export const getFriendlyStageLabel = (stageKey, fallback) => {
  if (!stageKey) return fallback;
  return APPROVE_STAGE_LABELS[stageKey] || fallback;
};

export const normalizeTokenParts = (token) => {
  if (!token) return [];
  const normalized = token.toString().toLowerCase().replace(/[^a-z0-9]+/g, "_");
  return normalized.split("_").filter(Boolean);
};

export const isReportGeneratorDateToken = (token) => {
  const parts = normalizeTokenParts(token);
  if (!parts.length) return false;
  if (token && REPORT_SELECTED_EXACT.has(token.toLowerCase())) return true;
  if (
    parts.some((part) => REPORT_SELECTED_KEYWORDS.has(part)) &&
    parts.some((part) => REPORT_SELECTED_SUFFIXES.has(part))
  ) {
    return true;
  }
  const hasPrefix = parts.some((part) => REPORT_DATE_PREFIXES.has(part));
  const hasKeyword = parts.some((part) => REPORT_DATE_KEYWORDS.has(part));
  if (hasPrefix && hasKeyword) return true;
  const [first, ...rest] = parts;
  if (REPORT_DATE_KEYWORDS.has(first) && rest.some((part) => REPORT_DATE_PREFIXES.has(part))) return true;
  const last = parts[parts.length - 1];
  if (REPORT_DATE_KEYWORDS.has(last) && parts.slice(0, -1).some((part) => REPORT_DATE_PREFIXES.has(part))) return true;
  return false;
};

export const normalizeMappingChoiceForToken = (token, value) => {
  if (typeof value !== "string") return value;
  const trimmed = value.trim();
  if (!trimmed) return trimmed;
  const lowered = trimmed.toLowerCase();
  const isDateToken = isReportGeneratorDateToken(token);
  if (!isDateToken) {
    if (lowered.startsWith("params.")) return VALUE_SAMPLE;
    return trimmed;
  }
  if (lowered.startsWith("params.")) return VALUE_LATER_SELECTED;
  if (lowered === VALUE_SAMPLE.toLowerCase()) return VALUE_SAMPLE;
  if (lowered === VALUE_LATER_SELECTED.toLowerCase()) return VALUE_LATER_SELECTED;
  if (lowered === SAMPLE_ALIAS.toLowerCase()) return VALUE_LATER_SELECTED;
  if (lowered.startsWith("to be selected")) return VALUE_LATER_SELECTED;
  return trimmed;
};

export const getSampleStatusLabel = (token, value) => {
  if (value === VALUE_LATER_SELECTED) return SAMPLE_STATUS_LATER;
  return SAMPLE_STATUS_SAMPLE;
};

export const formatIssue = (issue, label) => {
  const normalized = (issue ?? "").toString().trim();
  if (normalized === VALUE_SAMPLE || normalized === VALUE_LATER_SELECTED)
    return getSampleStatusLabel(label, normalized);
  if (normalized === VALUE_UNRESOLVED) return "User Input";
  return normalized;
};

export const getExpressionIssues = (value, catalogSet, groupedCatalog) => {
  const text = (value ?? "").toString().trim();
  if (!text) return [];
  const issues = [];
  const open = (text.match(/\(/g) || []).length;
  const close = (text.match(/\)/g) || []).length;
  if (open !== close) {
    issues.push("Unmatched parentheses");
  }
  if (LEGACY_WRAPPER_REGEX.test(text)) {
    issues.push("Remove legacy wrapper");
  }
  if (text.includes(";")) {
    issues.push("Remove semicolons");
  }
  if (catalogSet && catalogSet.size > 0) {
    const unknown = new Set();
    const knownTables = groupedCatalog
      ? new Set(Object.keys(groupedCatalog))
      : null;
    COLUMN_REF_REGEX.lastIndex = 0;
    let match;
    while ((match = COLUMN_REF_REGEX.exec(text)) !== null) {
      const table = match[1];
      const column = match[2];
      const fq = `${table}.${column}`;
      if (table.toLowerCase() === "params") {
        continue;
      }
      if (catalogSet.has(fq)) {
        continue;
      }
      if (!knownTables || knownTables.has(table)) {
        unknown.add(fq);
      }
    }
    if (unknown.size > 0) {
      issues.push(`Unknown catalog columns: ${Array.from(unknown).join(", ")}`);
    }
  }
  return issues;
};
