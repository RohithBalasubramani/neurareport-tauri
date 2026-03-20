import {
  Alert,
  Dialog,
  DialogContent,
  Stack,
  Typography,
} from "@mui/material";

import InfoTooltip from "@/components/common/InfoTooltip.jsx";
import TOOLTIP_COPY from "@/content/tooltipCopy.jsx";
import ConfirmModal from "@/components/modal/ConfirmModal";
import CorrectionsPreviewPanel from "./CorrectionsPreviewPanel.jsx";

import { useHeaderMapping } from "../hooks/useHeaderMapping.js";
import MappingAlerts from "./header-mapping/MappingAlerts.jsx";
import SelectedKeyTokens from "./header-mapping/SelectedKeyTokens.jsx";
import MappingTable from "./header-mapping/MappingTable.jsx";
import MappingFooter from "./header-mapping/MappingFooter.jsx";
import ApproveDialog from "./header-mapping/ApproveDialog.jsx";

export default function HeaderMappingEditor({
  templateId,
  connectionId,
  templateKind = "pdf",
  onApproved,
  blockApproveUntilResolved,
  disabledApproveWhileUnresolved,
  onCorrectionsComplete,
}) {
  const h = useHeaderMapping({
    templateId,
    connectionId,
    templateKind,
    onApproved,
    blockApproveUntilResolved,
    disabledApproveWhileUnresolved,
    onCorrectionsComplete,
  });

  if (!templateId || !connectionId) {
    return (
      <Alert severity="info">
        Verify a template and ensure a DB connection is selected to generate mapping.
      </Alert>
    );
  }
  if (h.fetching && !h.preview) return <Typography>Loading mapping...</Typography>;
  if (h.errorMsg && !h.preview) return <Alert severity="error">{h.errorMsg}</Alert>;
  if (!h.preview) return null;

  return (
    <>
    <Stack spacing={2}>
      <Stack direction="row" alignItems="center" spacing={0.75}>
        <Typography variant="h6">Field Mapping</Typography>
        <InfoTooltip content={TOOLTIP_COPY.headerMappings} ariaLabel="Header mappings guidance" />
      </Stack>

      <Alert severity="info">
        Match each design field to a data column. Formulas are optional for advanced cases.
        Auto-Fix uses AI to suggest corrections; review before approving. Approving saves the mapping and makes the design available for report runs.
      </Alert>

      <MappingAlerts
        errorMsg={h.errorMsg}
        hasAutoExpressions={h.hasAutoExpressions}
        hasExpressionIssues={h.hasExpressionIssues}
        expressionIssues={h.expressionIssues}
        preview={h.preview}
      />

      <SelectedKeyTokens
        orderedKeyTokens={h.orderedKeyTokens}
        waiting={h.waiting}
        onToggleKey={h.handleToggleKey}
      />

      <MappingTable
        headersAll={h.headersAll}
        mapping={h.mapping}
        expressionMode={h.expressionMode}
        expressionOrigin={h.expressionOrigin}
        catalogOptionSet={h.catalogOptionSet}
        groupedCatalog={h.groupedCatalog}
        selectedKeysSet={h.selectedKeysSet}
        waiting={h.waiting}
        parentTbl={h.parentTbl}
        distinctChildTbl={h.distinctChildTbl}
        onChangeValue={h.handleChange}
        onExpressionChange={h.handleExpressionChange}
        onConvertToExpression={h.handleConvertToExpression}
        onUseDropdown={h.handleUseDropdown}
        onToggleKey={h.handleToggleKey}
      />

      <MappingFooter
        headersAll={h.headersAll}
        unresolvedCount={h.unresolvedCount}
        waiting={h.waiting}
        correctionsComplete={h.correctionsComplete}
        saving={h.saving}
        approveButtonDisabled={h.approveButtonDisabled}
        onResetClick={h.handleResetClick}
        onOpenCorrections={() => h.setCorrectionsDialogOpen(true)}
        onOpenContract={() => h.setContractDialogOpen(true)}
      />
    </Stack>

    <Dialog
      open={h.correctionsDialogOpen}
      onClose={() => h.setCorrectionsDialogOpen(false)}
      maxWidth="md"
      fullWidth
    >
      <DialogContent sx={{ p: 0 }}>
        <CorrectionsPreviewPanel
          templateId={templateId}
          templateKind={templateKind}
          disabled={h.waiting}
          onCompleted={h.handleCorrectionsCompleted}
          onInstructionsChange={h.setLlm35Instructions}
          initialInstructions={h.llm35Instructions}
          mappingOverride={h.mapping}
          sampleTokens={h.sampleTokens}
          onSaveAndClose={() => h.setCorrectionsDialogOpen(false)}
        />
      </DialogContent>
    </Dialog>

    <ApproveDialog
      open={h.contractDialogOpen}
      onClose={() => h.setContractDialogOpen(false)}
      saving={h.saving}
      waiting={h.waiting}
      hasUnresolved={h.hasUnresolved}
      unresolvedOnly={h.unresolvedOnly}
      llm4Instructions={h.llm4Instructions}
      setLlm4Instructions={h.setLlm4Instructions}
      approveStage={h.approveStage}
      approveLog={h.approveLog}
      approveProgress={h.approveProgress}
      approveEta={h.approveEta}
      approveActionDisabled={h.approveActionDisabled}
      onApprove={h.handleApproveFromDialog}
    />

    <ConfirmModal
      open={h.resetConfirmOpen}
      onClose={() => h.setResetConfirmOpen(false)}
      onConfirm={() => {
        h.setResetConfirmOpen(false);
        h.performReset();
      }}
      title="Reset Fields"
      message="Resetting will clear all column selections, keys, and corrections status. You can restore immediately after reset."
      confirmLabel="Reset Fields"
      severity="warning"
    />
    </>
  );
}
