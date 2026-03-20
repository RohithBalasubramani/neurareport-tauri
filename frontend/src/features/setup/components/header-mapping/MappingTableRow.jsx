import {
  Box,
  Button,
  Chip,
  Stack,
  Switch,
  TableCell,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { alpha } from "@mui/material/styles";
import { neutral } from "@/app/theme";
import {
  VALUE_UNRESOLVED,
  VALUE_SAMPLE,
  VALUE_LATER_SELECTED,
  DIRECT_COLUMN_REGEX,
} from "./mappingConstants.js";
import { getSampleStatusLabel, getExpressionIssues } from "./mappingUtils.js";
import MappingDropdownCell from "./MappingDropdownCell.jsx";

export default function MappingTableRow({
  header,
  mapping,
  expressionMode,
  expressionOrigin,
  catalogOptionSet,
  groupedCatalog,
  selectedKeysSet,
  waiting,
  parentTbl,
  distinctChildTbl,
  onChangeValue,
  onExpressionChange,
  onConvertToExpression,
  onUseDropdown,
  onToggleKey,
}) {
  const rawValue = mapping?.[header];
  const valueString = rawValue == null ? "" : String(rawValue);
  const normalized = valueString.trim();
  const isSample = normalized === VALUE_SAMPLE;
  const isLaterSelected = normalized === VALUE_LATER_SELECTED;
  const isUnresolved = normalized === VALUE_UNRESOLVED;
  const isSampleChoice = isSample || isLaterSelected;
  const hasValue = normalized.length > 0;
  const sampleStatusLabel = getSampleStatusLabel(header, normalized);
  const directColumn =
    normalized &&
    (catalogOptionSet.has(normalized) || DIRECT_COLUMN_REGEX.test(normalized));
  const expressionActive =
    Boolean(expressionMode[header]) ||
    (hasValue && !isSampleChoice && !isUnresolved && !directColumn);
  const exprIssues = expressionActive
    ? getExpressionIssues(valueString, catalogOptionSet, groupedCatalog)
    : [];
  const currentOrigin = expressionOrigin[header];
  const isAutoSql = expressionActive && currentOrigin === "auto";
  const resolved = hasValue && !isSampleChoice && !isUnresolved;
  const keySelected = selectedKeysSet.has(header);
  const canSelectKey = !expressionActive && (directColumn || normalized === VALUE_UNRESOLVED);

  return (
    <TableRow>
      <TableCell sx={{ fontWeight: 500, width: { xs: '33%', md: '25%' }, minWidth: { xs: 176, md: 220 } }}>
        {header}
      </TableCell>
      <TableCell sx={{ width: { xs: 'auto', md: '43%' }, minWidth: { xs: 248, md: 334 }, maxWidth: { md: 430 } }}>
        {expressionActive ? (
          <Stack spacing={0.75} sx={{ width: '100%' }}>
            <TextField
              size="small" fullWidth multiline minRows={1}
              value={valueString}
              onChange={(e) => onExpressionChange(header, e.target.value)}
              placeholder="Enter a formula (advanced)"
              disabled={waiting}
              error={exprIssues.length > 0}
              helperText={exprIssues.length > 0 ? exprIssues.join(". ") : "Advanced: use formulas with catalog columns or params."}
              FormHelperTextProps={{ sx: { mt: 0.5 } }}
            />
            <Box sx={{ display: "flex", alignItems: "center", justifyContent: "flex-start", gap: 1 }}>
              <Typography variant="caption" color={exprIssues.length > 0 ? "warning.main" : "text.secondary"}>
                {isAutoSql ? "Auto-generated formula" : "Formula (advanced)"}
              </Typography>
              <Button size="small" variant="text" onClick={() => onUseDropdown(header)} disabled={waiting} sx={{ minWidth: 100 }}>
                Use dropdown
              </Button>
            </Box>
          </Stack>
        ) : (
          <MappingDropdownCell
            header={header}
            valueString={valueString}
            waiting={waiting}
            catalogOptionSet={catalogOptionSet}
            groupedCatalog={groupedCatalog}
            parentTbl={parentTbl}
            distinctChildTbl={distinctChildTbl}
            onChangeValue={onChangeValue}
            onConvertToExpression={onConvertToExpression}
          />
        )}
      </TableCell>
      <TableCell sx={{ width: 120, textAlign: 'center' }}>
        <Stack spacing={0.5} alignItems="center">
          <Switch
            size="small" checked={keySelected}
            onChange={(e) => onToggleKey(header, e.target.checked)}
            disabled={waiting || !canSelectKey}
            inputProps={{ 'aria-label': keySelected ? `Unset ${header} as key filter` : `Select ${header} as key filter` }}
          />
          <Typography variant="caption" color={canSelectKey ? "text.secondary" : "text.disabled"}>Select Key</Typography>
        </Stack>
      </TableCell>
      <TableCell sx={{ width: 140 }}>
        {resolved ? (
          expressionActive ? (
            <Stack direction="row" spacing={0.5} alignItems="center">
              <Chip size="small" label="Resolved" sx={{ bgcolor: (t) => t.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white' }} />
              <Chip
                size="small"
                label={exprIssues.length > 0 ? "Check SQL" : isAutoSql ? "Auto (SQL)" : "SQL (manual)"}
                variant={exprIssues.length > 0 || isAutoSql ? "filled" : "outlined"}
                sx={{
                  bgcolor: exprIssues.length > 0 || isAutoSql ? ((t) => t.palette.mode === 'dark' ? alpha(t.palette.text.primary, 0.1) : neutral[200]) : 'transparent',
                  borderColor: (t) => alpha(t.palette.divider, 0.3),
                  color: 'text.secondary',
                }}
              />
            </Stack>
          ) : (
            <Chip size="small" label="Resolved" sx={{ bgcolor: (t) => t.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white' }} />
          )
        ) : isSampleChoice ? (
          <Chip size="small" label={sampleStatusLabel} sx={{ bgcolor: (t) => t.palette.mode === 'dark' ? alpha(t.palette.text.primary, 0.08) : neutral[100], color: 'text.secondary' }} />
        ) : (
          <Chip size="small" label="User Input" sx={{ bgcolor: (t) => t.palette.mode === 'dark' ? alpha(t.palette.text.primary, 0.08) : neutral[100], color: 'text.secondary' }} />
        )}
      </TableCell>
    </TableRow>
  );
}
