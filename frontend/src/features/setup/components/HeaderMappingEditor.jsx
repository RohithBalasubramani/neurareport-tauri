import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Box, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle,
  FormControl, MenuItem, List, ListItem, ListSubheader, Select, Stack, Table,
  TableBody, TableCell, TableHead, TableRow, Typography, Alert, CircularProgress,
  LinearProgress, TextField, Switch, Tooltip
} from "@mui/material";
import { alpha } from "@mui/material/styles";
import { neutral } from "@/app/theme";
import { mappingPreview, mappingApprove } from "@/api/client";
import { useStepTimingEstimator, formatDuration } from "@/hooks/useStepTimingEstimator";
import CorrectionsPreviewPanel from "./CorrectionsPreviewPanel.jsx";
import InfoTooltip from "@/components/common/InfoTooltip.jsx";
import TOOLTIP_COPY from "@/content/tooltipCopy.jsx";
import { useToast } from "@/components/ToastProvider.jsx";
import ConfirmModal from "@/components/Modal/ConfirmModal";
import { useInteraction, InteractionType, Reversibility } from "@/components/ux/governance";

const VALUE_UNRESOLVED = "UNRESOLVED";
const VALUE_SAMPLE = "INPUT_SAMPLE";
const VALUE_LATER_SELECTED = "LATER_SELECTED";
const UNRESOLVED_VALUES = new Set([VALUE_UNRESOLVED, VALUE_SAMPLE, VALUE_LATER_SELECTED]);
const DIRECT_COLUMN_REGEX = /^[A-Za-z_][\w]*\.[A-Za-z_][\w]*$/;
const COLUMN_REF_REGEX = /(?:"|`|\[)?([A-Za-z_][\w]*)(?:"|`|\])?\.\s*(?:"|`|\[)?([A-Za-z_][\w]*)(?:"|`|\])?/g;
const LEGACY_WRAPPER_REGEX = /DERIVED\s*:|TABLE_COLUMNS\s*\[/i;
const REPORT_DATE_PREFIXES = new Set([
  "from",
  "to",
  "start",
  "end",
  "begin",
  "finish",
  "through",
  "thru",
]);
const REPORT_DATE_KEYWORDS = new Set([
  "date",
  "dt",
  "day",
  "period",
  "range",
  "time",
  "timestamp",
  "window",
  "month",
  "year",
]);
const REPORT_SELECTED_EXACT = new Set([
  "page_info",
  "page_number",
  "page_no",
  "page_num",
  "page_count",
  "page_total",
  "page_total_count",
]);
const REPORT_SELECTED_KEYWORDS = new Set(["page", "sheet"]);
const REPORT_SELECTED_SUFFIXES = new Set(["info", "number", "no", "num", "count", "total"]);
const SAMPLE_ALIAS = "To Be Selected in report generator";
const SAMPLE_STATUS_SAMPLE = "Input sample";
const SAMPLE_STATUS_LATER = "Later Selected";
const APPROVE_STAGE_LABELS = {
  "mapping.save": "Saving your column selections",
  "mapping.prepare_template": "Preparing the template preview",
  "contract_build_v2": "Drafting the narrative package",
  "generator_assets_v1": "Refreshing generator assets",
  "mapping.thumbnail": "Capturing updated preview",
  "approve.result": "Approval complete",
};

const getFriendlyStageLabel = (stageKey, fallback) => {
  if (!stageKey) return fallback;
  return APPROVE_STAGE_LABELS[stageKey] || fallback;
};

const normalizeTokenParts = (token) => {
  if (!token) return [];
  const normalized = token.toString().toLowerCase().replace(/[^a-z0-9]+/g, "_");
  return normalized.split("_").filter(Boolean);
};

const isReportGeneratorDateToken = (token) => {
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

const normalizeMappingChoiceForToken = (token, value) => {
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

const getSampleStatusLabel = (token, value) => {
  if (value === VALUE_LATER_SELECTED) return SAMPLE_STATUS_LATER;
  return SAMPLE_STATUS_SAMPLE;
};

const formatIssue = (issue, label) => {
  const normalized = (issue ?? "").toString().trim();
  if (normalized === VALUE_SAMPLE || normalized === VALUE_LATER_SELECTED)
    return getSampleStatusLabel(label, normalized);
  if (normalized === VALUE_UNRESOLVED) return "User Input";
  return normalized;
};

const getExpressionIssues = (value, catalogSet, groupedCatalog) => {
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

export default function HeaderMappingEditor({
  templateId,
  connectionId,
  templateKind = "pdf",
  onApproved,                     // callback after successful save (receives server resp with URLs)
  blockApproveUntilResolved,      // preferred name
  disabledApproveWhileUnresolved, // back-compat alias
  onCorrectionsComplete,
}) {
  const [fetching, setFetching] = useState(false);
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [preview, setPreview] = useState(null);   // { mapping, errors, catalog, schema_info, (optional) headers }
  const [mapping, setMapping] = useState({});     // editable mapping (may be sparse)
  const [expressionMode, setExpressionMode] = useState({});
  const [expressionOrigin, setExpressionOrigin] = useState({});
  const [headersAll, setHeadersAll] = useState([]); // stable, full list of headers to render
  const [selectedKeys, setSelectedKeys] = useState([]);
  const [approveStage, setApproveStage] = useState("");
  const [approveLog, setApproveLog] = useState([]);
  const [approveProgress, setApproveProgress] = useState(0);
  const [correctionsComplete, setCorrectionsComplete] = useState(false);
  const [correctionsDialogOpen, setCorrectionsDialogOpen] = useState(false);
  const [contractDialogOpen, setContractDialogOpen] = useState(false);
  const [llm35Instructions, setLlm35Instructions] = useState("");
  const [llm4Instructions, setLlm4Instructions] = useState("");
  const [resetConfirmOpen, setResetConfirmOpen] = useState(false);
  const approveAbortRef = useRef(null);
  const approveRequestRef = useRef(0);
  const resetSnapshotRef = useRef(null);
  const {
    eta: approveEta,
    startRun: beginApproveTiming,
    noteStage: trackApproveStage,
    completeStage: markApproveStageDone,
    finishRun: finishApproveTiming,
  } = useStepTimingEstimator("mapping-approve");
  const toast = useToast();
  const { execute } = useInteraction();

  const handleCorrectionsCompleted = useCallback(
    (payload) => {
      if (typeof onCorrectionsComplete === "function") {
        onCorrectionsComplete(payload);
      }

      setCorrectionsComplete(true);
    },
    [onCorrectionsComplete]
  );


  // normalize the "block approval" flag (support either prop name)
  const blockApproval = Boolean(
    blockApproveUntilResolved ?? disabledApproveWhileUnresolved ?? false
  );

  // group catalog options by table for nicer dropdowns
  const groupedCatalog = useMemo(() => {
    const out = {};
    const list = preview?.catalog || [];
    for (const fq of list) {
      const [tbl, col] = fq.split(".");
      if (!tbl || !col) continue;
      (out[tbl] ||= new Set()).add(fq);
    }
    return Object.fromEntries(
      Object.keys(out)
        .sort()
        .map((tbl) => [tbl, Array.from(out[tbl]).sort()])
    );
  }, [preview?.catalog]);

  const catalogOptionSet = useMemo(() => {
    const set = new Set();
    const list = preview?.catalog || [];
    for (const fq of list) {
      if (typeof fq === "string" && fq.trim()) {
        set.add(fq.trim());
      }
    }
    return set;
  }, [preview?.catalog]);

  // fetch preview on mount/prop change
  useEffect(() => {
    if (!templateId || !connectionId) {
      setPreview(null);
      setMapping({});
      setExpressionMode({});
      setExpressionOrigin({});
      setHeadersAll([]);
      setSelectedKeys([]);
      setApproveStage("");
      setApproveLog([]);
      setApproveProgress(0);
      setCorrectionsDialogOpen(false);
      setContractDialogOpen(false);
      setLlm35Instructions("");
      setLlm4Instructions("");
      setCorrectionsComplete(false);
      return;
    }
    let cancelled = false;
    setFetching(true);
    setErrorMsg("");
    setPreview(null);
    setMapping({});
    setExpressionMode({});
    setExpressionOrigin({});
    setHeadersAll([]);
    setApproveStage("");
    setApproveLog([]);
    setApproveProgress(0);
    setCorrectionsDialogOpen(false);
    setContractDialogOpen(false);
    setLlm35Instructions("");
    setLlm4Instructions("");
    setCorrectionsComplete(false);
    (async () => {
      try {
        const response = await execute({
          type: InteractionType.ANALYZE,
          label: "Load mapping preview",
          reversibility: Reversibility.SYSTEM_MANAGED,
          suppressSuccessToast: true,
          suppressErrorToast: true,
          blocksNavigation: false,
          intent: {
            templateId,
            connectionId,
            templateKind,
            action: "mapping_preview",
          },
          action: async () => mappingPreview(templateId, connectionId, { kind: templateKind }),
        });
        if (!response.success) {
          throw response.error;
        }
        const data = response.result;
        if (cancelled) return;
        const initialMapping = data.mapping || {};
        const catalogSet = new Set(
          (data.catalog || [])
            .filter((item) => typeof item === "string")
            .map((item) => item.trim())
            .filter(Boolean)
        );
        const nextExpressionMode = {};
        const nextExpressionOrigin = {};
        const normalizedMapping = {};
        for (const [token, rawVal] of Object.entries(initialMapping)) {
          const rawString = rawVal == null ? "" : String(rawVal);
          const normalizedChoice = normalizeMappingChoiceForToken(token, rawString);
          normalizedMapping[token] = normalizedChoice;
          const trimmedValue = typeof normalizedChoice === "string" ? normalizedChoice.trim() : "";
          const isExpression =
            trimmedValue &&
            !UNRESOLVED_VALUES.has(trimmedValue) &&
            !catalogSet.has(trimmedValue) &&
            !DIRECT_COLUMN_REGEX.test(trimmedValue);
          if (isExpression) {
            nextExpressionMode[token] = true;
            nextExpressionOrigin[token] = "auto";
          }
        }
        setExpressionMode(nextExpressionMode);
        setExpressionOrigin(nextExpressionOrigin);
        setMapping(normalizedMapping);
        const mappingKeys = Object.keys(normalizedMapping);
        const fallbackHeaders = Array.isArray(data.headers) ? data.headers : [];
        setHeadersAll(mappingKeys.length > 0 ? mappingKeys : fallbackHeaders);
        const initialKeys = Array.isArray(data.keys) ? data.keys : [];
        const normalizedKeys = Array.from(
          new Set(
            initialKeys
              .map((token) => (typeof token === "string" ? token.trim() : ""))
              .filter((token) => token && Object.prototype.hasOwnProperty.call(normalizedMapping, token))
          )
        );
        setSelectedKeys(normalizedKeys);
        setPreview({ ...data, keys: normalizedKeys });
        setCorrectionsComplete(Boolean(data?.artifacts?.page_summary_url));
      } catch (e) {
        if (!cancelled) {
          setErrorMsg(e?.message || "Failed to load mapping preview");
        }
      } finally {
        if (!cancelled) {
          setFetching(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [templateId, connectionId, templateKind, execute]);

  useEffect(() => () => {
    approveAbortRef.current?.abort();
  }, []);

  useEffect(() => {
    setSelectedKeys((prev) => prev.filter((token) => headersAll.includes(token)));
  }, [headersAll]);

  useEffect(() => {
    setSelectedKeys((prev) =>
      prev.filter((token) => {
        const value = mapping?.[token];
        if (typeof value !== "string") return false;
        const trimmed = value.trim();
        if (!trimmed || UNRESOLVED_VALUES.has(trimmed)) return false;
        if (expressionMode[token]) return false;
        return DIRECT_COLUMN_REGEX.test(trimmed);
      })
    );
  }, [mapping, expressionMode]);

  const selectedKeysSet = useMemo(() => new Set(selectedKeys), [selectedKeys]);
  const orderedKeyTokens = useMemo(
    () => headersAll.filter((header) => selectedKeysSet.has(header)),
    [headersAll, selectedKeysSet]
  );

  const handleChange = (header, value) => {
    const normalizedSelection =
      typeof value === "string" ? normalizeMappingChoiceForToken(header, value) : value;
    setMapping((m) => ({ ...m, [header]: normalizedSelection }));
    if (typeof normalizedSelection === "string") {
      const trimmed = normalizedSelection.trim();
      const isDirectColumn =
        trimmed === VALUE_UNRESOLVED ||
        trimmed === VALUE_SAMPLE ||
        trimmed === VALUE_LATER_SELECTED ||
        trimmed === "" ||
        catalogOptionSet.has(trimmed) ||
        DIRECT_COLUMN_REGEX.test(trimmed);
      if (isDirectColumn) {
        setExpressionMode((prev) => {
          if (!prev[header]) return prev;
          const next = { ...prev };
          delete next[header];
          return next;
        });
        setExpressionOrigin((prev) => {
          if (!prev[header]) return prev;
          const next = { ...prev };
          delete next[header];
          return next;
        });
      }
      if (
        trimmed === "" ||
        trimmed === VALUE_UNRESOLVED ||
        trimmed === VALUE_SAMPLE ||
        trimmed === VALUE_LATER_SELECTED
      ) {
        setSelectedKeys((prev) => prev.filter((token) => token !== header));
      }
    }
  };

  const handleExpressionChange = (header, value) => {
    setMapping((m) => ({ ...m, [header]: value }));
    setExpressionMode((prev) => (prev[header] ? prev : { ...prev, [header]: true }));
    setExpressionOrigin((prev) => ({
      ...prev,
      [header]: prev[header] === "auto" ? "manual" : (prev[header] || "manual"),
    }));
  };

  const handleConvertToExpression = (header) => {
    setExpressionMode((prev) => ({ ...prev, [header]: true }));
    setExpressionOrigin((prev) => ({ ...prev, [header]: "manual" }));
    setMapping((m) => {
      const current = (m?.[header] ?? "").toString().trim();
      const seed = current && !UNRESOLVED_VALUES.has(current) ? current : "";
      return { ...m, [header]: seed };
    });
  };

  const handleUseDropdown = (header) => {
    setExpressionMode((prev) => {
      if (!prev[header]) return prev;
      const next = { ...prev };
      delete next[header];
      return next;
    });
    setExpressionOrigin((prev) => {
      if (!prev[header]) return prev;
      const next = { ...prev };
      delete next[header];
      return next;
    });
    setMapping((m) => ({ ...m, [header]: VALUE_UNRESOLVED }));
  };

  const handleToggleKey = useCallback(
    (header, enabled) => {
      setSelectedKeys((prev) => {
        if (!enabled) {
          return prev.filter((token) => token !== header);
        }
        if (prev.includes(header)) {
          return prev;
        }
        const value = mapping?.[header];
        const trimmed = typeof value === "string" ? value.trim() : "";
        if (!trimmed || expressionMode[header]) {
          return prev;
        }
        if (!UNRESOLVED_VALUES.has(trimmed) && !DIRECT_COLUMN_REGEX.test(trimmed)) {
          return prev;
        }
        return [...prev, header];
      });
    },
    [mapping, expressionMode]
  );

  const resetMappingState = useCallback(() => {
    setExpressionMode({});
    setExpressionOrigin({});
    setMapping(Object.fromEntries(headersAll.map((h) => [h, VALUE_UNRESOLVED])));
    setSelectedKeys([]);
    setCorrectionsComplete(false);
  }, [headersAll]);

  const hasCustomMapping = useMemo(() => {
    if (!headersAll.length) return false;
    if (selectedKeys.length > 0) return true;
    if (Object.keys(expressionMode).length > 0) return true;
    return headersAll.some((header) => {
      const value = mapping?.[header];
      if (typeof value !== "string") return false;
      const trimmed = value.trim();
      return Boolean(trimmed && trimmed !== VALUE_UNRESOLVED);
    });
  }, [headersAll, mapping, selectedKeys, expressionMode]);

  const performReset = useCallback(() => {
    resetSnapshotRef.current = {
      mapping,
      expressionMode,
      expressionOrigin,
      selectedKeys,
      correctionsComplete,
    };
    resetMappingState();
    toast.showWithUndo(
      "Fields reset to User Input.",
      () => {
        const snapshot = resetSnapshotRef.current;
        if (!snapshot) return;
        setMapping(snapshot.mapping);
        setExpressionMode(snapshot.expressionMode);
        setExpressionOrigin(snapshot.expressionOrigin);
        setSelectedKeys(snapshot.selectedKeys);
        setCorrectionsComplete(snapshot.correctionsComplete);
      },
      { severity: "info", undoLabel: "Restore" }
    );
  }, [
    correctionsComplete,
    expressionMode,
    expressionOrigin,
    mapping,
    resetMappingState,
    selectedKeys,
    toast,
  ]);

  const handleResetClick = useCallback(() => {
    if (!hasCustomMapping) {
      resetMappingState();
      return;
    }
    setResetConfirmOpen(true);
  }, [hasCustomMapping, resetMappingState]);

  const runApprove = async () => {
    const payload = Object.fromEntries(
      headersAll.map((h) => [h, mapping?.[h] ?? VALUE_UNRESOLVED])
    );

    if (approveAbortRef.current) {
      approveAbortRef.current.abort();
    }
    const controller = new AbortController();
    approveAbortRef.current = controller;

    const requestId = approveRequestRef.current + 1;
    approveRequestRef.current = requestId;

    beginApproveTiming();
    setSaving(true);
    setErrorMsg("");
    const initialStageLabel = getFriendlyStageLabel("mapping.save", "Saving mapping changes");
    setApproveStage(`${initialStageLabel} - in progress...`);
    setApproveLog([{
      key: "mapping.save",
      label: initialStageLabel,
      status: "started",
      startedAt: Date.now(),
      updatedAt: Date.now(),
      elapsedMs: null,
      skipped: false,
      detail: null,
      meta: {},
    }]);
    setApproveProgress(5);

    const handleProgress = (evt) => {
      if (approveRequestRef.current !== requestId) return;
      if (!evt) return;

      if (typeof evt.progress === "number") {
        setApproveProgress(evt.progress);
      }

      const eventType = evt.event || (evt.stage ? "stage" : null);

      if (eventType === "stage") {
        const stageKey = typeof evt.stage === "string" ? evt.stage : String(evt.stage ?? "stage");
        const rawLabel = evt.label || evt.message || stageKey;
        const friendlyLabel = getFriendlyStageLabel(stageKey, rawLabel);
        const rawStatus = typeof evt.status === "string" ? evt.status.toLowerCase() : "";
        let status = "started";
        if (rawStatus === "done" || rawStatus === "complete") status = "complete";
        else if (rawStatus === "error" || rawStatus === "failed") status = "error";
        else if (rawStatus === "skipped") status = "skipped";
        else if (rawStatus) status = rawStatus;
        const skipped = Boolean(evt.skipped);
        const now = Date.now();

        let stageSummary = "";
        if (status === "complete") {
          if (skipped) stageSummary = `${friendlyLabel} - skipped`;
          else if (evt.elapsed_ms != null) stageSummary = `${friendlyLabel} - finished in ${formatDuration(evt.elapsed_ms)}`;
          else stageSummary = `${friendlyLabel} - finished`;
        } else if (status === "error") {
          const detail = evt.detail ? `: ${evt.detail}` : "";
          stageSummary = `${friendlyLabel} - failed${detail}`;
        } else if (status === "skipped") {
          stageSummary = `${friendlyLabel} - skipped`;
        } else {
          stageSummary = `${friendlyLabel} - in progress...`;
        }
        setApproveStage(stageSummary);

        setApproveLog((prev) => {
          const entries = [...prev];
          const idx = entries.findIndex((entry) => entry.key === stageKey);
          const existing = idx === -1 ? null : entries[idx];
          const startedAt = status === "started" ? now : (existing?.startedAt ?? now);
          const elapsedMs = (status === "complete" || status === "error" || status === "skipped")
            ? (evt.elapsed_ms ?? existing?.elapsedMs ?? null)
            : existing?.elapsedMs ?? null;
          const nextEntry = {
            key: stageKey,
            label: friendlyLabel,
            status,
            startedAt,
            updatedAt: now,
            elapsedMs,
            skipped: skipped ?? existing?.skipped ?? false,
            detail: evt.detail ?? existing?.detail ?? null,
            meta: { ...(existing?.meta || {}), ...evt },
          };
          if (idx === -1) entries.push(nextEntry);
          else entries[idx] = nextEntry;
          return entries;
        });

        if (status === "started") {
          trackApproveStage(stageKey);
        } else if (status === "complete" || status === "error" || status === "skipped") {
          markApproveStageDone(stageKey, evt.elapsed_ms);
        }
      } else if (eventType === "result") {
        const resultKey = typeof evt.stage === "string" ? evt.stage : "approve.result";
        const rawLabel = evt.label || evt.message || evt.stage || "Approval complete.";
        const friendlyLabel = getFriendlyStageLabel(resultKey, rawLabel);
        const now = Date.now();
        const summary = evt.elapsed_ms != null
          ? `${friendlyLabel} - finished in ${formatDuration(evt.elapsed_ms)}`
          : friendlyLabel;
        setApproveStage(summary);
        trackApproveStage(resultKey);
        markApproveStageDone(resultKey, evt.elapsed_ms);
        setApproveProgress((p) => {
          if (typeof evt.progress === "number") {
            return evt.progress;
          }
          return p < 100 ? 100 : p;
        });
        setApproveLog((prev) => {
          const entries = [...prev];
          const idx = entries.findIndex((entry) => entry.key === "approve.result");
          const existing = idx === -1 ? null : entries[idx];
          const nextEntry = {
            key: "approve.result",
            label: friendlyLabel,
            status: "complete",
            startedAt: existing?.startedAt ?? now,
            updatedAt: now,
            elapsedMs: evt.elapsed_ms ?? existing?.elapsedMs ?? null,
            skipped: false,
            detail: evt.detail ?? existing?.detail ?? null,
            meta: { ...(existing?.meta || {}), ...evt },
          };
          if (idx === -1) entries.push(nextEntry);
          else entries[idx] = nextEntry;
          return entries;
        });
      } else if (eventType === "error") {
        const errorKey = typeof evt.stage === "string" ? evt.stage : "approve.error";
        const rawLabel = evt.label || evt.message || evt.stage || "Approval failed";
        const friendlyLabel = getFriendlyStageLabel(errorKey, rawLabel);
        const detail = evt.detail || "Unknown error";
        setApproveStage(`${friendlyLabel} - failed: ${detail}`);
        trackApproveStage(errorKey);
        markApproveStageDone(errorKey, evt.elapsed_ms);
        setApproveLog((prev) => [
          ...prev,
          {
            key: `approve.error.${Date.now()}`,
            label: friendlyLabel,
            status: "error",
            startedAt: Date.now(),
            updatedAt: Date.now(),
            elapsedMs: evt.elapsed_ms ?? null,
            skipped: false,
            detail,
            meta: { ...evt },
          },
        ]);
      }
    };
    let outcome = "pending";
    try {
      const resp = await mappingApprove(templateId, payload, {
        connectionId,
        userInstructions: llm4Instructions,
        keys: Array.from(selectedKeysSet),
        onProgress: handleProgress,
        signal: controller.signal,
        kind: templateKind,
      });
      if (approveRequestRef.current !== requestId) {
        outcome = "aborted";
        return;
      }
      if (Array.isArray(resp?.keys)) {
        const normalizedRespKeys = Array.from(
          new Set(
            resp.keys
              .map((token) => (typeof token === "string" ? token.trim() : ""))
              .filter(Boolean)
          )
        );
        setSelectedKeys(normalizedRespKeys);
        setPreview((prev) => (prev ? { ...prev, keys: normalizedRespKeys } : prev));
      }
      setApproveProgress((p) => (p < 100 ? 100 : p));
      setApproveStage((prev) => prev || `${getFriendlyStageLabel("approve.result", "Approval complete")}.`);
      outcome = "success";
      const maybe = onApproved?.({ ...resp, requestId });
      if (maybe && typeof maybe.then === "function") {
        await maybe;
      }
    } catch (e) {
      if (e?.name === "AbortError") {
        outcome = "aborted";
      } else {
        outcome = "error";
        const msg = e?.message || "Failed to save mapping";
        setErrorMsg(msg);
        setApproveStage(`Error: ${msg}`);
        setApproveLog((prev) => [
          ...prev,
          {
            key: `approve.error.${Date.now()}`,
            label: "Approval failed",
            status: "error",
            startedAt: Date.now(),
            updatedAt: Date.now(),
            elapsedMs: null,
            skipped: false,
            detail: msg,
            meta: { error: e?.toString?.() ?? msg },
          },
        ]);
        setApproveProgress(100);
      }
    } finally {
      if (approveAbortRef.current === controller) {
        approveAbortRef.current = null;
      }
      if (approveRequestRef.current === requestId && outcome !== "aborted") {
        finishApproveTiming();
        setSaving(false);
      }
    }
    return outcome;
  };

  const handleApprove = async () => {
    const response = await execute({
      type: InteractionType.UPDATE,
      label: "Approve mapping",
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId,
        connectionId,
        templateKind,
        action: "mapping_approve",
      },
      action: async () => {
        const outcome = await runApprove();
        if (outcome === "error") {
          throw new Error("Mapping approval failed");
        }
        return outcome;
      },
    });
    if (!response.success) return "error";
    return response.result;
  };

  // unresolved = empty or "UNRESOLVED", computed against headersAll
  const unresolvedCount = useMemo(
    () =>
      headersAll.reduce((acc, h) => {
        const v = (mapping?.[h] ?? VALUE_UNRESOLVED).trim();
        return acc + (v === VALUE_UNRESOLVED ? 1 : 0);
      }, 0),
    [headersAll, mapping]
  );

  const unresolvedOnly = useMemo(
    () =>
      headersAll.filter((h) => (mapping?.[h] ?? VALUE_UNRESOLVED).trim() === VALUE_UNRESOLVED),
    [headersAll, mapping]
  );

  const hasUnresolved = unresolvedOnly.length > 0;

  const sampleTokens = useMemo(
    () =>
      Object.entries(mapping || {})
        .filter(([, value]) => {
          const normalized = (value ?? "").trim();
          return normalized === VALUE_SAMPLE || normalized === VALUE_LATER_SELECTED;
        })
        .map(([token]) => token),
    [mapping]
  );

  const expressionSummary = useMemo(() => {
    const summary = { hasAuto: false, issues: {} };
    for (const header of headersAll) {
      const rawValue = mapping?.[header];
      const valueString = rawValue == null ? "" : String(rawValue);
      const normalized = valueString.trim();
      const isSample = normalized === VALUE_SAMPLE;
      const isLaterSelected = normalized === VALUE_LATER_SELECTED;
      const isUnresolved = normalized === VALUE_UNRESOLVED;
      const isSampleChoice = isSample || isLaterSelected;
      const hasValue = normalized.length > 0;
      const directColumn =
        normalized &&
        (catalogOptionSet.has(normalized) || DIRECT_COLUMN_REGEX.test(normalized));
      const expressionActive =
        Boolean(expressionMode[header]) ||
        (hasValue && !isSampleChoice && !isUnresolved && !directColumn);
      if (expressionActive) {
        if (expressionOrigin[header] === "auto") {
          summary.hasAuto = true;
        }
        const issues = getExpressionIssues(valueString, catalogOptionSet, groupedCatalog);
        if (issues.length > 0) {
          summary.issues[header] = issues;
        }
      }
    }
    return summary;
  }, [headersAll, mapping, expressionMode, expressionOrigin, catalogOptionSet]);

  const hasAutoExpressions = expressionSummary.hasAuto;
  const expressionIssues = expressionSummary.issues;
  const hasExpressionIssues = Object.keys(expressionIssues).length > 0;

  // early UI states
  if (!templateId || !connectionId) {
    return (
      <Alert severity="info">
        Verify a template and ensure a DB connection is selected to generate mapping.
      </Alert>
    );
  }
  if (fetching && !preview) return <Typography>Loading mapping...</Typography>;
  if (errorMsg && !preview) return <Alert severity="error">{errorMsg}</Alert>;
  if (!preview) return null;

  const parentTbl = preview?.schema_info?.["parent table"];
  const childTbl  = preview?.schema_info?.["child table"];
  const distinctChildTbl = childTbl && childTbl !== parentTbl ? childTbl : null;

  // request/approval gating
  const waiting = fetching || saving;
  const approvalBlocked =
    headersAll.length === 0 ||
    !correctionsComplete ||
    (blockApproval && unresolvedCount > 0);
  const approveActionDisabled = waiting || approvalBlocked;
  const approveButtonDisabled = waiting || !correctionsComplete;

  const handleApproveFromDialog = async () => {
    if (approveActionDisabled) return;
    const outcome = await handleApprove();
    if (outcome === "success") {
      setContractDialogOpen(false);
    }
  };

  return (
    <>
    <Stack spacing={2}>
      <Stack direction="row" alignItems="center" spacing={0.75}>
        <Typography variant="h6">Field Mapping</Typography>
        <InfoTooltip
          content={TOOLTIP_COPY.headerMappings}
          ariaLabel="Header mappings guidance"
        />
      </Stack>

      <Alert severity="info">
        Match each design field to a data column. Formulas are optional for advanced cases.
        Auto-Fix uses AI to suggest corrections; review before approving. Approving saves the mapping and makes the design available for report runs.
      </Alert>

      {!!errorMsg && <Alert severity="error">{errorMsg}</Alert>}

      {hasAutoExpressions && (
        <Alert severity="info">
          Auto-mapped formulas are shown below. Review or edit them before approval.
        </Alert>
      )}
      {hasExpressionIssues && (
        <Alert severity="warning">
          Formula check: {Object.keys(expressionIssues).join(", ")} {Object.keys(expressionIssues).length === 1 ? "needs" : "need"} attention.
        </Alert>
      )}

      {!!preview.errors?.length && (
        <Box
          sx={{
            p: 1,
            border: "1px solid",
            borderRadius: 1,
            borderColor: (theme) => alpha(theme.palette.divider, 0.4),
            bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
            color: "text.secondary",
          }}
        >
          <Typography variant="subtitle2" color="warning.dark">Auto-mapping items to review</Typography>
          <List
            dense
            disablePadding
            sx={{ listStyleType: 'disc', pl: 3, color: 'inherit' }}
          >
            {preview.errors.map((e, i) => (
              <ListItem key={i} disableGutters sx={{ display: 'list-item', py: 0, color: 'inherit' }}>
                <Typography variant="body2" color="inherit">
                  {formatIssue(e.issue, e.label)}: {e.label}
                </Typography>
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      <Box sx={{ mt: 1 }}>
        <Typography variant="subtitle2">Selected Key Tokens</Typography>
        {orderedKeyTokens.length ? (
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mt: 0.75 }}>
            {orderedKeyTokens.map((token) => (
              <Chip
                key={`key-token-${token}`}
                label={token}
                size="small"
                onDelete={waiting ? undefined : () => handleToggleKey(token, false)}
                sx={{
                  bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                  color: 'common.white',
                  '& .MuiChip-deleteIcon': { color: 'common.white', opacity: 0.7 },
                }}
              />
            ))}
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Toggle rows below to mark required key filters.
          </Typography>
        )}
      </Box>

      {/* Always render the table so users can edit even when all resolved */}
      <Box sx={{ mt: 1, overflowX: 'auto' }}>
        <Table
          size="small"
          sx={{
            minWidth: 640,
            width: '100%',
            tableLayout: { xs: 'auto', md: 'fixed' },
            '& th, & td': {
              whiteSpace: 'normal',
              wordBreak: 'break-word',
              verticalAlign: 'top',
            },
          }}
        >
          <TableHead>
            <TableRow>
              <TableCell
                sx={{
                  width: { xs: '33%', md: '25%' },
                  minWidth: { xs: 176, md: 220 },
                  fontWeight: 600,
                }}
              >
                Header
              </TableCell>
              <TableCell
                sx={{
                  width: { xs: 'auto', md: '43%' },
                  minWidth: { xs: 248, md: 334 },
                  maxWidth: { md: 430 },
                  fontWeight: 600,
                }}
              >
                Map to column
              </TableCell>
              <TableCell sx={{ width: '10%', fontWeight: 600, textAlign: 'center' }}>Key</TableCell>
              <TableCell sx={{ width: '15%', fontWeight: 600 }}>Status</TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {headersAll.map(header => {
              const rawValue = mapping?.[header];
              const valueString = rawValue == null ? "" : String(rawValue);
              const normalized = valueString.trim();
              const isSample = normalized === VALUE_SAMPLE;
              const isLaterSelected = normalized === VALUE_LATER_SELECTED;
              const isUnresolved = normalized === VALUE_UNRESOLVED;
              const isSampleChoice = isSample || isLaterSelected;
              const hasValue = normalized.length > 0;
              const sampleStatusLabel = getSampleStatusLabel(header, normalized);
              const sampleOptions = isReportGeneratorDateToken(header)
                ? [
                    { value: VALUE_LATER_SELECTED, label: SAMPLE_STATUS_LATER },
                    { value: VALUE_SAMPLE, label: SAMPLE_STATUS_SAMPLE },
                  ]
                : [
                    { value: VALUE_SAMPLE, label: SAMPLE_STATUS_SAMPLE },
                    { value: VALUE_LATER_SELECTED, label: SAMPLE_STATUS_LATER },
                  ];
              const directColumn =
                normalized &&
                (catalogOptionSet.has(normalized) || DIRECT_COLUMN_REGEX.test(normalized));
              const expressionActive =
                Boolean(expressionMode[header]) ||
                (hasValue && !isSampleChoice && !isUnresolved && !directColumn);
              const exprIssues = expressionActive ? getExpressionIssues(valueString, catalogOptionSet, groupedCatalog) : [];
              const currentOrigin = expressionOrigin[header];
              const isAutoSql = expressionActive && currentOrigin === "auto";
              const resolved = hasValue && !isSampleChoice && !isUnresolved;
              const keySelected = selectedKeysSet.has(header);
              const canSelectKey =
                !expressionActive &&
                (directColumn || normalized === VALUE_UNRESOLVED);
              return (
                <TableRow key={header}>
                  <TableCell
                    sx={{
                      fontWeight: 500,
                      width: { xs: '33%', md: '25%' },
                      minWidth: { xs: 176, md: 220 },
                    }}
                  >
                    {header}
                  </TableCell>
                  <TableCell
                    sx={{
                      width: { xs: 'auto', md: '43%' },
                      minWidth: { xs: 248, md: 334 },
                      maxWidth: { md: 430 },
                    }}
                  >
                    {expressionActive ? (
                      <Stack spacing={0.75} sx={{ width: '100%' }}>
                        <TextField
                          size="small"
                          fullWidth
                          multiline
                          minRows={1}
                          value={valueString}
                          onChange={(e) => handleExpressionChange(header, e.target.value)}
                          placeholder="Enter a formula (advanced)"
                          disabled={waiting}
                          error={exprIssues.length > 0}
                          helperText={
                            exprIssues.length > 0
                              ? exprIssues.join(". ")
                              : "Advanced: use formulas with catalog columns or params."
                          }
                          FormHelperTextProps={{ sx: { mt: 0.5 } }}
                        />
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "flex-start",
                            gap: 1,
                          }}
                        >
                          <Typography
                            variant="caption"
                            color={exprIssues.length > 0 ? "warning.main" : "text.secondary"}
                          >
                            {isAutoSql ? "Auto-generated formula" : "Formula (advanced)"}
                          </Typography>
                          <Button
                            size="small"
                            variant="text"
                            onClick={() => handleUseDropdown(header)}
                            disabled={waiting}
                            sx={{ minWidth: 100 }}
                          >
                            Use dropdown
                          </Button>
                        </Box>
                      </Stack>
                    ) : (
                      <Stack spacing={0.5} sx={{ width: '100%' }}>
                        <FormControl fullWidth size="small" disabled={waiting}>
                          <Select
                            value={valueString || VALUE_UNRESOLVED}
                            onChange={(e) => handleChange(header, e.target.value)}
                            renderValue={(selected) => {
                              const resolvedSelected = selected || VALUE_UNRESOLVED;
                              const sampleMatch = sampleOptions.find((option) => option.value === resolvedSelected);
                              const displayValue =
                                resolvedSelected === VALUE_UNRESOLVED
                                  ? "User Input"
                                  : sampleMatch?.label || resolvedSelected;
                              return (
                                <Tooltip title={displayValue}>
                                  <Typography
                                    component="span"
                                    sx={{
                                      display: 'block',
                                      maxWidth: '100%',
                                      whiteSpace: 'nowrap',
                                      overflow: 'hidden',
                                      textOverflow: 'ellipsis',
                                    }}
                                  >
                                    {displayValue}
                                  </Typography>
                                </Tooltip>
                              );
                            }}
                            sx={{
                              '& .MuiSelect-select': {
                                display: 'block',
                                whiteSpace: 'nowrap',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                              },
                            }}
                            MenuProps={{ PaperProps: { style: { maxHeight: 320 } } }}
                          >
                            <ListSubheader disableSticky>Choose column</ListSubheader>
                            <MenuItem value={VALUE_UNRESOLVED}>User Input</MenuItem>
                            {sampleOptions.map((option) => (
                              <MenuItem key={option.value} value={option.value}>
                                {option.label}
                              </MenuItem>
                            ))}

                            {/* Parent group first (if present) */}
                            {parentTbl && (
                              <ListSubheader disableSticky>{parentTbl}</ListSubheader>
                            )}
                            {Object.entries(groupedCatalog)
                              .filter(([tbl]) => tbl === parentTbl)
                              .flatMap(([, cols]) =>
                                cols.map(fq => <MenuItem key={fq} value={fq}>{fq}</MenuItem>)
                              )
                            }

                            {/* Child group next (if present) */}
                            {distinctChildTbl && (
                              <ListSubheader disableSticky>{distinctChildTbl}</ListSubheader>
                            )}
                            {Object.entries(groupedCatalog)
                              .filter(([tbl]) => tbl === distinctChildTbl)
                              .flatMap(([, cols]) =>
                                cols.map(fq => <MenuItem key={fq} value={fq}>{fq}</MenuItem>)
                              )
                            }

                            {/* Any other tables (edge case) */}
                            {Object.entries(groupedCatalog)
                              .filter(([tbl]) => tbl !== parentTbl && tbl !== distinctChildTbl)
                              .flatMap(([tbl, cols]) => ([
                                <ListSubheader key={`lh-${tbl}`} disableSticky>{tbl}</ListSubheader>,
                                ...cols.map(fq => <MenuItem key={fq} value={fq}>{fq}</MenuItem>)
                              ]))
                            }
                          </Select>
                        </FormControl>
                        <Button
                          size="small"
                          variant="text"
                          onClick={() => handleConvertToExpression(header)}
                          disabled={waiting}
                        >
                          Use formula
                        </Button>
                      </Stack>
                    )}
                  </TableCell>
                  <TableCell sx={{ width: 120, textAlign: 'center' }}>
                    <Stack spacing={0.5} alignItems="center">
                      <Switch
                        size="small"
                        checked={keySelected}
                        onChange={(e) => handleToggleKey(header, e.target.checked)}
                        disabled={waiting || !canSelectKey}
                        inputProps={{
                          'aria-label': keySelected
                            ? `Unset ${header} as key filter`
                            : `Select ${header} as key filter`,
                        }}
                      />
                      <Typography
                        variant="caption"
                        color={canSelectKey ? "text.secondary" : "text.disabled"}
                      >
                        Select Key
                      </Typography>
                    </Stack>
                  </TableCell>
                  <TableCell sx={{ width: 140 }}>
                    {resolved ? (
                      expressionActive ? (
                        <Stack direction="row" spacing={0.5} alignItems="center">
                          <Chip size="small" label="Resolved" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white' }} />
                          <Chip
                            size="small"
                            label={
                              exprIssues.length > 0
                                ? "Check SQL"
                                : isAutoSql
                                ? "Auto (SQL)"
                                : "SQL (manual)"
                            }
                            variant={exprIssues.length > 0 || isAutoSql ? "filled" : "outlined"}
                            sx={{
                              bgcolor: exprIssues.length > 0 || isAutoSql ? ((theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200]) : 'transparent',
                              borderColor: (theme) => alpha(theme.palette.divider, 0.3),
                              color: 'text.secondary',
                            }}
                          />
                        </Stack>
                      ) : (
                        <Chip size="small" label="Resolved" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white' }} />
                      )
                    ) : isSampleChoice ? (
                      <Chip
                        size="small"
                        label={sampleStatusLabel}
                        sx={{
                          bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                          color: 'text.secondary',
                        }}
                      />
                    ) : (
                      <Chip size="small" label="User Input" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100], color: 'text.secondary' }} />
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Box>

      


      {/* Footer bar with disabled overlay while waiting */}
      <Box position="relative">
        <Stack
          direction={{ xs: "column", sm: "row" }}
          justifyContent={{ xs: "flex-start", sm: "space-between" }}
          alignItems={{ xs: "flex-start", sm: "center" }}
          spacing={{ xs: 1, sm: 1.5 }}
          sx={{
            opacity: waiting ? 0.8 : 1,
            transition: "opacity 120ms cubic-bezier(0.22, 1, 0.36, 1)",
          }}
        >
          <Stack spacing={0.5} sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography variant="body2" color="text.secondary">
              {headersAll.length === 0
                ? "No headers detected in template"
                : (unresolvedCount ? `${unresolvedCount} unresolved` : "All resolved")}
            </Typography>
          </Stack>

          <Stack
            direction={{ xs: "column", sm: "row" }}
            spacing={1}
            sx={{ width: { xs: "100%", sm: "auto" } }}
          >
            <Button
              variant="outlined"
              onClick={handleResetClick}
              disabled={headersAll.length === 0 || waiting}
              sx={{ width: { xs: "100%", sm: "auto" } }}
            >
              Reset Fields
            </Button>
            <Button
              variant="outlined"
              onClick={() => setCorrectionsDialogOpen(true)}
              disabled={waiting}
              sx={{ width: { xs: "100%", sm: "auto" } }}
            >
              Auto-Fix Fields
            </Button>
            <Button
              variant="contained"
              onClick={() => setContractDialogOpen(true)}
              disabled={approveButtonDisabled}
              sx={{ width: { xs: "100%", sm: "auto" } }}
            >
              {saving ? "Saving..." : "Approve Design"}
            </Button>
          </Stack>
        </Stack>

        {!correctionsComplete && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 0.75, maxWidth: { xs: "100%", sm: 420 } }}
          >
            Run Auto-Fix Fields and save the preview before approving.
          </Typography>
        )}

        {/* subtle overlay to indicate busy state */}
        {waiting && (
          <Box
            aria-hidden
            position="absolute"
            inset={-4}
            bgcolor="rgba(255,255,255,0.5)"
            sx={{ borderRadius: 1, pointerEvents: "none" }}
          />
        )}
      </Box>
    </Stack>

    <Dialog
      open={correctionsDialogOpen}
      onClose={() => setCorrectionsDialogOpen(false)}
      maxWidth="md"
      fullWidth
    >
      <DialogContent sx={{ p: 0 }}>
        <CorrectionsPreviewPanel
          templateId={templateId}
          templateKind={templateKind}
          disabled={waiting}
          onCompleted={handleCorrectionsCompleted}
          onInstructionsChange={setLlm35Instructions}
          initialInstructions={llm35Instructions}
          mappingOverride={mapping}
          sampleTokens={sampleTokens}
          onSaveAndClose={() => setCorrectionsDialogOpen(false)}
        />
      </DialogContent>
    </Dialog>

    <Dialog
      open={contractDialogOpen}
      onClose={(_event, _reason) => {
        if (saving) return;
        setContractDialogOpen(false);
      }}
      maxWidth="sm"
      fullWidth
      disableEscapeKeyDown={saving}
    >
    <DialogTitle sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        Report Instructions
        <InfoTooltip
          content={TOOLTIP_COPY.llm4Narrative}
          ariaLabel="Narrative guidance"
          placement="bottom-start"
        />
      </DialogTitle>
      <DialogContent dividers sx={{ pt: 1.5 }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
          Describe any custom logic, calculations, or layout rules you want in the report. These instructions guide the narrative output.
        </Typography>
        {hasUnresolved && (
          <Box sx={{ mb: 2, p: 1.5, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Unresolved placeholders
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              These headers are still marked as User Input. Mention how they should be populated when describing the desired report output.
            </Typography>
            <List dense disablePadding sx={{ listStyleType: 'disc', pl: 3 }}>
              {unresolvedOnly.map((label) => (
                <ListItem key={`llm4-unresolved-${label}`} disableGutters sx={{ display: 'list-item', py: 0.25 }}>
                  <Typography variant="body2">{label}</Typography>
                </ListItem>
              ))}
            </List>
          </Box>
        )}
        <TextField
          label="Report instructions"
          placeholder="Example: Summarize daily totals by material and include variance columns."
          multiline
          minRows={4}
          fullWidth
          value={llm4Instructions}
          onChange={(e) => setLlm4Instructions(e.target.value)}
          disabled={waiting}
        />
        {(saving || approveLog.length > 0) && (
          <Box
            sx={{
              mt: 3,
              p: 2,
              borderRadius: 1,  // Figma spec: 8px
              border: "1px solid",
              borderColor: (theme) => alpha(theme.palette.divider, 0.2),
              bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
            }}
          >
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Approval progress
            </Typography>
            {approveStage && (
              <Typography variant="body2" sx={{ mb: 1 }}>
                {approveStage}
              </Typography>
            )}
            <LinearProgress
              variant="determinate"
              value={approveProgress}
              sx={{ height: 6, borderRadius: 999, bgcolor: (theme) => alpha(theme.palette.text.primary, 0.1), '& .MuiLinearProgress-bar': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
            />
            <Box sx={{ mt: 1.5, display: "grid", gap: 0.5 }}>
              {approveLog.map((entry, idx) => {
                const baseLabel = entry?.label || entry?.key || `Step ${idx + 1}`;
                let suffix = "";
                if (entry?.status === "complete") {
                  if (entry?.skipped) suffix = " - skipped";
                  else if (entry?.elapsedMs != null) suffix = ` - finished in ${formatDuration(entry.elapsedMs)}`;
                  else suffix = " - finished";
                } else if (entry?.status === "error") {
                  suffix = ` - failed${entry?.detail ? `: ${entry.detail}` : ""}`;
                } else if (entry?.status === "started") {
                  suffix = " - in progress";
                } else if (entry?.status === "skipped") {
                  suffix = " - skipped";
                }
                const text = `${baseLabel}${suffix}`;
                const isActive = Boolean(saving && entry?.status === "started");
                const isError = entry?.status === "error";
                return (
                  <Typography
                    key={`${entry?.key || baseLabel}-${idx}`}
                    variant="caption"
                    color="text.secondary"
                    sx={{ fontWeight: isActive ? 600 : 400 }}
                  >
                    {idx + 1}. {text}
                  </Typography>
                );
              })}
            </Box>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
              Estimated time remaining:{" "}
              {approveEta.ms == null
                ? "Learning step timings..."
                : `${approveEta.reliable ? "" : "~ "}${formatDuration(approveEta.ms)}${approveEta.reliable ? "" : " (learning)"}`}
            </Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ justifyContent: "space-between" }}>
        <Button
          onClick={() => setLlm4Instructions("")}
          disabled={saving || !llm4Instructions.trim()}
          sx={{ color: 'text.secondary' }}
        >
          Clear
        </Button>
        <Stack direction="row" spacing={1}>
          <Button onClick={() => setContractDialogOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleApproveFromDialog}
            disabled={approveActionDisabled}
            startIcon={saving ? <CircularProgress size={18} sx={{ color: 'text.secondary' }} /> : null}
          >
            {saving ? "Saving..." : "Approve Design"}
          </Button>
        </Stack>
      </DialogActions>
    </Dialog>

    <ConfirmModal
      open={resetConfirmOpen}
      onClose={() => setResetConfirmOpen(false)}
      onConfirm={() => {
        setResetConfirmOpen(false);
        performReset();
      }}
      title="Reset Fields"
      message="Resetting will clear all column selections, keys, and corrections status. You can restore immediately after reset."
      confirmLabel="Reset Fields"
      severity="warning"
    />
    </>
  );
}






