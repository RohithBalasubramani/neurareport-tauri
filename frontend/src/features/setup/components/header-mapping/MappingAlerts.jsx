import {
  Alert,
  Box,
  List,
  ListItem,
  Typography,
} from "@mui/material";
import { alpha } from "@mui/material/styles";
import { neutral } from "@/app/theme";
import { formatIssue } from "./mappingUtils.js";

export default function MappingAlerts({
  errorMsg,
  hasAutoExpressions,
  hasExpressionIssues,
  expressionIssues,
  preview,
}) {
  return (
    <>
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
    </>
  );
}
