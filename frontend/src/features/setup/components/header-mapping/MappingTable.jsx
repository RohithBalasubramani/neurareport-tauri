import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@mui/material";
import MappingTableRow from "./MappingTableRow.jsx";

export default function MappingTable({
  headersAll,
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
  return (
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
            <TableCell sx={{ width: { xs: '33%', md: '25%' }, minWidth: { xs: 176, md: 220 }, fontWeight: 600 }}>
              Header
            </TableCell>
            <TableCell sx={{ width: { xs: 'auto', md: '43%' }, minWidth: { xs: 248, md: 334 }, maxWidth: { md: 430 }, fontWeight: 600 }}>
              Map to column
            </TableCell>
            <TableCell sx={{ width: '10%', fontWeight: 600, textAlign: 'center' }}>Key</TableCell>
            <TableCell sx={{ width: '15%', fontWeight: 600 }}>Status</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {headersAll.map((header) => (
            <MappingTableRow
              key={header}
              header={header}
              mapping={mapping}
              expressionMode={expressionMode}
              expressionOrigin={expressionOrigin}
              catalogOptionSet={catalogOptionSet}
              groupedCatalog={groupedCatalog}
              selectedKeysSet={selectedKeysSet}
              waiting={waiting}
              parentTbl={parentTbl}
              distinctChildTbl={distinctChildTbl}
              onChangeValue={onChangeValue}
              onExpressionChange={onExpressionChange}
              onConvertToExpression={onConvertToExpression}
              onUseDropdown={onUseDropdown}
              onToggleKey={onToggleKey}
            />
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
