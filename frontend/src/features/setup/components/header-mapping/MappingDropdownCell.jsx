import {
  Button,
  FormControl,
  ListSubheader,
  MenuItem,
  Select,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import {
  VALUE_UNRESOLVED,
  VALUE_LATER_SELECTED,
  VALUE_SAMPLE,
} from "./mappingConstants.js";
import { isReportGeneratorDateToken } from "./mappingUtils.js";

const SAMPLE_STATUS_SAMPLE = "Input sample";
const SAMPLE_STATUS_LATER = "Later Selected";

export default function MappingDropdownCell({
  header,
  valueString,
  waiting,
  catalogOptionSet,
  groupedCatalog,
  parentTbl,
  distinctChildTbl,
  onChangeValue,
  onConvertToExpression,
}) {
  const sampleOptions = isReportGeneratorDateToken(header)
    ? [
        { value: VALUE_LATER_SELECTED, label: SAMPLE_STATUS_LATER },
        { value: VALUE_SAMPLE, label: SAMPLE_STATUS_SAMPLE },
      ]
    : [
        { value: VALUE_SAMPLE, label: SAMPLE_STATUS_SAMPLE },
        { value: VALUE_LATER_SELECTED, label: SAMPLE_STATUS_LATER },
      ];

  return (
    <Stack spacing={0.5} sx={{ width: '100%' }}>
      <FormControl fullWidth size="small" disabled={waiting}>
        <Select
          value={valueString || VALUE_UNRESOLVED}
          onChange={(e) => onChangeValue(header, e.target.value)}
          renderValue={(selected) => {
            const resolvedSelected = selected || VALUE_UNRESOLVED;
            const sampleMatch = sampleOptions.find((o) => o.value === resolvedSelected);
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
          {sampleOptions.map((o) => (
            <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>
          ))}
          {parentTbl && (
            <ListSubheader disableSticky>{parentTbl}</ListSubheader>
          )}
          {Object.entries(groupedCatalog)
            .filter(([tbl]) => tbl === parentTbl)
            .flatMap(([, cols]) =>
              cols.map(fq => <MenuItem key={fq} value={fq}>{fq}</MenuItem>)
            )
          }
          {distinctChildTbl && (
            <ListSubheader disableSticky>{distinctChildTbl}</ListSubheader>
          )}
          {Object.entries(groupedCatalog)
            .filter(([tbl]) => tbl === distinctChildTbl)
            .flatMap(([, cols]) =>
              cols.map(fq => <MenuItem key={fq} value={fq}>{fq}</MenuItem>)
            )
          }
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
        onClick={() => onConvertToExpression(header)}
        disabled={waiting}
      >
        Use formula
      </Button>
    </Stack>
  );
}
