export const VALUE_UNRESOLVED = "UNRESOLVED";
export const VALUE_SAMPLE = "INPUT_SAMPLE";
export const VALUE_LATER_SELECTED = "LATER_SELECTED";
export const UNRESOLVED_VALUES = new Set([VALUE_UNRESOLVED, VALUE_SAMPLE, VALUE_LATER_SELECTED]);
export const DIRECT_COLUMN_REGEX = /^[A-Za-z_][\w]*\.[A-Za-z_][\w]*$/;
export const COLUMN_REF_REGEX = /(?:"|`|\[)?([A-Za-z_][\w]*)(?:"|`|\])?\.\s*(?:"|`|\[)?([A-Za-z_][\w]*)(?:"|`|\])?/g;
export const LEGACY_WRAPPER_REGEX = /DERIVED\s*:|TABLE_COLUMNS\s*\[/i;

export const REPORT_DATE_PREFIXES = new Set([
  "from", "to", "start", "end", "begin", "finish", "through", "thru",
]);
export const REPORT_DATE_KEYWORDS = new Set([
  "date", "dt", "day", "period", "range", "time", "timestamp", "window", "month", "year",
]);
export const REPORT_SELECTED_EXACT = new Set([
  "page_info", "page_number", "page_no", "page_num", "page_count",
  "page_total", "page_total_count",
]);
export const REPORT_SELECTED_KEYWORDS = new Set(["page", "sheet"]);
export const REPORT_SELECTED_SUFFIXES = new Set(["info", "number", "no", "num", "count", "total"]);

export const SAMPLE_ALIAS = "To Be Selected in report generator";
export const SAMPLE_STATUS_SAMPLE = "Input sample";
export const SAMPLE_STATUS_LATER = "Later Selected";

export const APPROVE_STAGE_LABELS = {
  "mapping.save": "Saving your column selections",
  "mapping.prepare_template": "Preparing the template preview",
  "contract_build_v2": "Drafting the narrative package",
  "generator_assets_v1": "Refreshing generator assets",
  "mapping.thumbnail": "Capturing updated preview",
  "approve.result": "Approval complete",
};
