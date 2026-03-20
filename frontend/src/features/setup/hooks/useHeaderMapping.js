import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { mappingPreview, mappingApprove } from "@/api/client";
import { useStepTimingEstimator, formatDuration } from "@/hooks/useStepTimingEstimator";
import { useToast } from "@/components/ToastProvider.jsx";
import { useInteraction, InteractionType, Reversibility } from "@/components/ux/governance";
import {
  VALUE_UNRESOLVED,
  VALUE_SAMPLE,
  VALUE_LATER_SELECTED,
  UNRESOLVED_VALUES,
  DIRECT_COLUMN_REGEX,
} from "../components/header-mapping/mappingConstants.js";
import {
  normalizeMappingChoiceForToken,
  getFriendlyStageLabel,
  getExpressionIssues,
  isReportGeneratorDateToken,
} from "../components/header-mapping/mappingUtils.js";

export function useHeaderMapping({
  templateId,
  connectionId,
  templateKind = "pdf",
  onApproved,
  blockApproveUntilResolved,
  disabledApproveWhileUnresolved,
  onCorrectionsComplete,
}) {
  const [fetching, setFetching] = useState(false);
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [preview, setPreview] = useState(null);
  const [mapping, setMapping] = useState({});
  const [expressionMode, setExpressionMode] = useState({});
  const [expressionOrigin, setExpressionOrigin] = useState({});
  const [headersAll, setHeadersAll] = useState([]);
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

  const blockApproval = Boolean(
    blockApproveUntilResolved ?? disabledApproveWhileUnresolved ?? false
  );

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

  const parentTbl = preview?.schema_info?.["parent table"];
  const childTbl = preview?.schema_info?.["child table"];
  const distinctChildTbl = childTbl && childTbl !== parentTbl ? childTbl : null;

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

  return {
    fetching,
    saving,
    errorMsg,
    preview,
    mapping,
    expressionMode,
    expressionOrigin,
    headersAll,
    selectedKeys,
    approveStage,
    approveLog,
    approveProgress,
    correctionsComplete,
    correctionsDialogOpen,
    setCorrectionsDialogOpen,
    contractDialogOpen,
    setContractDialogOpen,
    llm35Instructions,
    setLlm35Instructions,
    llm4Instructions,
    setLlm4Instructions,
    resetConfirmOpen,
    setResetConfirmOpen,
    approveEta,
    handleCorrectionsCompleted,
    blockApproval,
    groupedCatalog,
    catalogOptionSet,
    selectedKeysSet,
    orderedKeyTokens,
    handleChange,
    handleExpressionChange,
    handleConvertToExpression,
    handleUseDropdown,
    handleToggleKey,
    resetMappingState,
    hasCustomMapping,
    performReset,
    handleResetClick,
    handleApprove,
    handleApproveFromDialog,
    unresolvedCount,
    unresolvedOnly,
    hasUnresolved,
    sampleTokens,
    hasAutoExpressions,
    expressionIssues,
    hasExpressionIssues,
    parentTbl,
    distinctChildTbl,
    waiting,
    approvalBlocked,
    approveActionDisabled,
    approveButtonDisabled,
  };
}
