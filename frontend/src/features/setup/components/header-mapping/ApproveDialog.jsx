import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  LinearProgress,
  List,
  ListItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { alpha } from "@mui/material/styles";
import { neutral } from "@/app/theme";
import InfoTooltip from "@/components/common/InfoTooltip.jsx";
import TOOLTIP_COPY from "@/content/tooltipCopy.jsx";
import { formatDuration } from "@/hooks/useStepTimingEstimator";

export default function ApproveDialog({
  open,
  onClose,
  saving,
  waiting,
  hasUnresolved,
  unresolvedOnly,
  llm4Instructions,
  setLlm4Instructions,
  approveStage,
  approveLog,
  approveProgress,
  approveEta,
  approveActionDisabled,
  onApprove,
}) {
  return (
    <Dialog
      open={open}
      onClose={(_event, _reason) => {
        if (saving) return;
        onClose();
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
              borderRadius: 1,
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
          <Button onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={onApprove}
            disabled={approveActionDisabled}
            startIcon={saving ? <CircularProgress size={18} sx={{ color: 'text.secondary' }} /> : null}
          >
            {saving ? "Saving..." : "Approve Design"}
          </Button>
        </Stack>
      </DialogActions>
    </Dialog>
  );
}
