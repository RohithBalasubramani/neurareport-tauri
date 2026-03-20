import {
  Box,
  Button,
  Stack,
  Typography,
} from "@mui/material";

export default function MappingFooter({
  headersAll,
  unresolvedCount,
  waiting,
  correctionsComplete,
  saving,
  approveButtonDisabled,
  onResetClick,
  onOpenCorrections,
  onOpenContract,
}) {
  return (
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
            onClick={onResetClick}
            disabled={headersAll.length === 0 || waiting}
            sx={{ width: { xs: "100%", sm: "auto" } }}
          >
            Reset Fields
          </Button>
          <Button
            variant="outlined"
            onClick={onOpenCorrections}
            disabled={waiting}
            sx={{ width: { xs: "100%", sm: "auto" } }}
          >
            Auto-Fix Fields
          </Button>
          <Button
            variant="contained"
            onClick={onOpenContract}
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
  );
}
