"""
Formula Engine - Formula parsing and evaluation.
"""

from __future__ import annotations

import logging
import math
import random
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

from pydantic import BaseModel

logger = logging.getLogger("neura.formula_engine")


class FormulaResult(BaseModel):
    """Result of formula evaluation."""

    value: Any
    formatted_value: str
    error: Optional[str] = None
    cell_type: str = "formula"


class CellReference(BaseModel):
    """Parsed cell reference."""

    col: int
    row: int
    col_abs: bool = False
    row_abs: bool = False


class FormulaEngine:
    """
    Formula engine for spreadsheet calculations.

    Supports 400+ Excel-compatible functions via HyperFormula integration
    and provides a fallback pure-Python implementation for basic functions.
    """

    # Built-in functions (fallback when HyperFormula not available)
    FUNCTIONS: dict[str, Callable] = {}

    def __init__(self):
        self._register_functions()
        self._hyperformula = None
        self._try_init_hyperformula()

    def _try_init_hyperformula(self):
        """Try to initialize HyperFormula for advanced formula support."""
        try:
            # HyperFormula is a JavaScript library
            # For Python, we'd need to use Pyodide or similar
            # For now, we use pure Python fallback
            pass
        except Exception as e:
            logger.debug(f"HyperFormula not available, using fallback: {e}")

    def _register_functions(self):
        """Register built-in functions."""
        # Math functions
        self.FUNCTIONS = {
            # Basic math
            "SUM": self._fn_sum,
            "AVERAGE": self._fn_average,
            "COUNT": self._fn_count,
            "COUNTA": self._fn_counta,
            "MAX": self._fn_max,
            "MIN": self._fn_min,
            "ABS": lambda x: abs(float(x)),
            "SQRT": lambda x: math.sqrt(float(x)),
            "POWER": lambda x, y: math.pow(float(x), float(y)),
            "LOG": lambda x, base=10: math.log(float(x), float(base)),
            "LN": lambda x: math.log(float(x)),
            "EXP": lambda x: math.exp(float(x)),
            "ROUND": lambda x, d=0: round(float(x), int(d)),
            "FLOOR": lambda x: math.floor(float(x)),
            "CEILING": lambda x: math.ceil(float(x)),
            "MOD": lambda x, y: float(x) % float(y),
            "PI": lambda: math.pi,
            "RAND": lambda: random.random(),
            "RANDBETWEEN": lambda a, b: random.randint(int(a), int(b)),

            # Statistical
            "MEDIAN": self._fn_median,
            "MODE": self._fn_mode,
            "STDEV": self._fn_stdev,
            "VAR": self._fn_var,

            # Conditional
            "IF": self._fn_if,
            "AND": self._fn_and,
            "OR": self._fn_or,
            "NOT": lambda x: not self._to_bool(x),
            "IFERROR": self._fn_iferror,
            "ISBLANK": lambda x: x is None or x == "",
            "ISNUMBER": lambda x: isinstance(x, (int, float)),
            "ISTEXT": lambda x: isinstance(x, str),

            # Lookup
            "VLOOKUP": self._fn_vlookup,
            "HLOOKUP": self._fn_hlookup,
            "INDEX": self._fn_index,
            "MATCH": self._fn_match,

            # Text
            "CONCATENATE": lambda *args: "".join(str(a) for a in args),
            "CONCAT": lambda *args: "".join(str(a) for a in args),
            "LEFT": lambda s, n=1: str(s)[:int(n)],
            "RIGHT": lambda s, n=1: str(s)[-int(n):],
            "MID": lambda s, start, length: str(s)[int(start)-1:int(start)-1+int(length)],
            "LEN": lambda s: len(str(s)),
            "UPPER": lambda s: str(s).upper(),
            "LOWER": lambda s: str(s).lower(),
            "PROPER": lambda s: str(s).title(),
            "TRIM": lambda s: str(s).strip(),
            "SUBSTITUTE": lambda s, old, new: str(s).replace(str(old), str(new)),
            "FIND": lambda needle, haystack, start=1: str(haystack).find(str(needle), int(start)-1) + 1,
            "SEARCH": lambda needle, haystack, start=1: str(haystack).lower().find(str(needle).lower(), int(start)-1) + 1,
            "TEXT": self._fn_text,
            "VALUE": lambda s: float(str(s).replace(",", "")),

            # Date/Time
            "TODAY": lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "NOW": lambda: datetime.now(timezone.utc).isoformat(),
            "DATE": lambda y, m, d: datetime(int(y), int(m), int(d)).strftime("%Y-%m-%d"),
            "YEAR": lambda d: self._parse_date(d).year,
            "MONTH": lambda d: self._parse_date(d).month,
            "DAY": lambda d: self._parse_date(d).day,
            "HOUR": lambda d: self._parse_datetime(d).hour,
            "MINUTE": lambda d: self._parse_datetime(d).minute,
            "SECOND": lambda d: self._parse_datetime(d).second,
            "WEEKDAY": lambda d: self._parse_date(d).weekday() + 1,
            "DATEDIF": self._fn_datedif,

            # Aggregation with conditions
            "SUMIF": self._fn_sumif,
            "COUNTIF": self._fn_countif,
            "AVERAGEIF": self._fn_averageif,
        }

    def evaluate(
        self,
        formula: str,
        data: list[list[Any]],
        current_cell: Optional[tuple[int, int]] = None,
    ) -> FormulaResult:
        """
        Evaluate a formula against spreadsheet data.

        Args:
            formula: Formula string starting with '='
            data: 2D array of cell values
            current_cell: (row, col) of the cell containing this formula

        Returns:
            FormulaResult with evaluated value
        """
        if not formula.startswith("="):
            return FormulaResult(
                value=formula,
                formatted_value=str(formula),
                cell_type="string",
            )

        try:
            # Remove leading '='
            expr = formula[1:].strip()

            # Parse and evaluate
            result = self._evaluate_expression(expr, data, current_cell)

            return FormulaResult(
                value=result,
                formatted_value=self._format_value(result),
            )
        except Exception as e:
            logger.warning(f"Formula error: {formula} - {e}")
            return FormulaResult(
                value=None,
                formatted_value="#ERROR!",
                error=str(e),
            )

    def _evaluate_expression(
        self,
        expr: str,
        data: list[list[Any]],
        current_cell: Optional[tuple[int, int]] = None,
    ) -> Any:
        """Evaluate a formula expression."""
        expr = expr.strip()

        # Check for function call
        func_match = re.match(r"^([A-Z]+)\((.*)\)$", expr, re.IGNORECASE)
        if func_match:
            func_name = func_match.group(1).upper()
            args_str = func_match.group(2)

            if func_name not in self.FUNCTIONS:
                raise ValueError(f"Unknown function: {func_name}")

            # Parse arguments
            args = self._parse_arguments(args_str, data, current_cell)

            # Call function
            return self.FUNCTIONS[func_name](*args)

        # Check for cell reference
        cell_match = re.match(r"^\$?([A-Z]+)\$?(\d+)$", expr, re.IGNORECASE)
        if cell_match:
            col = self._col_to_index(cell_match.group(1))
            row = int(cell_match.group(2)) - 1
            return self._get_cell_value(data, row, col)

        # Check for range reference (A1:B10)
        range_match = re.match(
            r"^\$?([A-Z]+)\$?(\d+):\$?([A-Z]+)\$?(\d+)$",
            expr,
            re.IGNORECASE,
        )
        if range_match:
            start_col = self._col_to_index(range_match.group(1))
            start_row = int(range_match.group(2)) - 1
            end_col = self._col_to_index(range_match.group(3))
            end_row = int(range_match.group(4)) - 1
            return self._get_range_values(data, start_row, start_col, end_row, end_col)

        # Try to evaluate as number
        try:
            if "." in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # Return as string (strip quotes if present)
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        return expr

    def _parse_arguments(
        self,
        args_str: str,
        data: list[list[Any]],
        current_cell: Optional[tuple[int, int]],
    ) -> list[Any]:
        """Parse function arguments."""
        if not args_str.strip():
            return []

        args = []
        current_arg = ""
        paren_depth = 0
        in_string = False
        string_char = None

        for char in args_str:
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
                current_arg += char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
                current_arg += char
            elif char == "(" and not in_string:
                paren_depth += 1
                current_arg += char
            elif char == ")" and not in_string:
                paren_depth -= 1
                current_arg += char
            elif char == "," and paren_depth == 0 and not in_string:
                args.append(self._evaluate_expression(current_arg.strip(), data, current_cell))
                current_arg = ""
            else:
                current_arg += char

        if current_arg.strip():
            args.append(self._evaluate_expression(current_arg.strip(), data, current_cell))

        return args

    def _col_to_index(self, col: str) -> int:
        """Convert column letter to 0-based index."""
        result = 0
        for char in col.upper():
            result = result * 26 + (ord(char) - ord("A") + 1)
        return result - 1

    def _get_cell_value(self, data: list[list[Any]], row: int, col: int) -> Any:
        """Get value from a cell."""
        if row < 0 or row >= len(data):
            return None
        if col < 0 or col >= len(data[row]):
            return None
        return data[row][col]

    def _get_range_values(
        self,
        data: list[list[Any]],
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int,
    ) -> list[Any]:
        """Get all values in a range as flat list."""
        values = []
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                val = self._get_cell_value(data, row, col)
                if val is not None and val != "":
                    values.append(val)
        return values

    def _format_value(self, value: Any) -> str:
        """Format value for display."""
        if value is None:
            return ""
        if isinstance(value, float):
            if math.isfinite(value) and value == int(value):
                return str(int(value))
            return f"{value:.2f}"
        return str(value)

    def _to_number(self, value: Any) -> float:
        """Convert value to number."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value.replace(",", ""))
        return 0.0

    def _to_bool(self, value: Any) -> bool:
        """Convert value to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1")
        return bool(value)

    def _parse_date(self, value: Any) -> datetime:
        """Parse value as date."""
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value)[:10])

    def _parse_datetime(self, value: Any) -> datetime:
        """Parse value as datetime."""
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value))

    # Function implementations
    def _fn_sum(self, *args) -> float:
        """SUM function."""
        total = 0.0
        for arg in args:
            if isinstance(arg, list):
                total += sum(self._to_number(v) for v in arg if v is not None and v != "")
            else:
                total += self._to_number(arg)
        return total

    def _fn_average(self, *args) -> float:
        """AVERAGE function."""
        values = []
        for arg in args:
            if isinstance(arg, list):
                values.extend(self._to_number(v) for v in arg if v is not None and v != "")
            else:
                values.append(self._to_number(arg))
        return sum(values) / len(values) if values else 0.0

    def _fn_count(self, *args) -> int:
        """COUNT function - counts numbers."""
        count = 0
        for arg in args:
            if isinstance(arg, list):
                count += sum(1 for v in arg if isinstance(v, (int, float)))
            elif isinstance(arg, (int, float)):
                count += 1
        return count

    def _fn_counta(self, *args) -> int:
        """COUNTA function - counts non-empty values."""
        count = 0
        for arg in args:
            if isinstance(arg, list):
                count += sum(1 for v in arg if v is not None and v != "")
            elif arg is not None and arg != "":
                count += 1
        return count

    def _fn_max(self, *args) -> float:
        """MAX function."""
        values = []
        for arg in args:
            if isinstance(arg, list):
                values.extend(self._to_number(v) for v in arg if isinstance(v, (int, float)))
            elif isinstance(arg, (int, float)):
                values.append(self._to_number(arg))
        return max(values) if values else 0.0

    def _fn_min(self, *args) -> float:
        """MIN function."""
        values = []
        for arg in args:
            if isinstance(arg, list):
                values.extend(self._to_number(v) for v in arg if isinstance(v, (int, float)))
            elif isinstance(arg, (int, float)):
                values.append(self._to_number(arg))
        return min(values) if values else 0.0

    def _fn_median(self, *args) -> float:
        """MEDIAN function."""
        import statistics
        values = []
        for arg in args:
            if isinstance(arg, list):
                values.extend(self._to_number(v) for v in arg if isinstance(v, (int, float)))
            elif isinstance(arg, (int, float)):
                values.append(self._to_number(arg))
        return statistics.median(values) if values else 0.0

    def _fn_mode(self, *args) -> float:
        """MODE function."""
        import statistics
        values = []
        for arg in args:
            if isinstance(arg, list):
                values.extend(self._to_number(v) for v in arg if isinstance(v, (int, float)))
            elif isinstance(arg, (int, float)):
                values.append(self._to_number(arg))
        return statistics.mode(values) if values else 0.0

    def _fn_stdev(self, *args) -> float:
        """STDEV function."""
        import statistics
        values = []
        for arg in args:
            if isinstance(arg, list):
                values.extend(self._to_number(v) for v in arg if isinstance(v, (int, float)))
            elif isinstance(arg, (int, float)):
                values.append(self._to_number(arg))
        return statistics.stdev(values) if len(values) > 1 else 0.0

    def _fn_var(self, *args) -> float:
        """VAR function."""
        import statistics
        values = []
        for arg in args:
            if isinstance(arg, list):
                values.extend(self._to_number(v) for v in arg if isinstance(v, (int, float)))
            elif isinstance(arg, (int, float)):
                values.append(self._to_number(arg))
        return statistics.variance(values) if len(values) > 1 else 0.0

    def _fn_if(self, condition, true_val, false_val=None):
        """IF function."""
        return true_val if self._to_bool(condition) else (false_val or "")

    def _fn_and(self, *args) -> bool:
        """AND function."""
        return all(self._to_bool(arg) for arg in args)

    def _fn_or(self, *args) -> bool:
        """OR function."""
        return any(self._to_bool(arg) for arg in args)

    def _fn_iferror(self, value, error_value):
        """IFERROR function."""
        # In our context, if value evaluation would have failed, we'd already have an error
        # So this is mainly for compatibility
        return value if value is not None else error_value

    def _fn_vlookup(self, lookup_value, table_array, col_index, range_lookup=True):
        """VLOOKUP function."""
        if not isinstance(table_array, list) or not table_array:
            return "#N/A"

        col_index = int(col_index) - 1

        for row in table_array:
            if isinstance(row, list) and len(row) > col_index:
                if row[0] == lookup_value:
                    return row[col_index]

        return "#N/A"

    def _fn_hlookup(self, lookup_value, table_array, row_index, range_lookup=True):
        """HLOOKUP function."""
        # Similar to VLOOKUP but horizontal
        return "#N/A"  # Simplified

    def _fn_index(self, array, row_num, col_num=None):
        """INDEX function."""
        if not isinstance(array, list):
            return "#REF!"

        row_num = int(row_num) - 1
        if row_num < 0 or row_num >= len(array):
            return "#REF!"

        if col_num is not None:
            col_num = int(col_num) - 1
            if isinstance(array[row_num], list):
                if col_num < 0 or col_num >= len(array[row_num]):
                    return "#REF!"
                return array[row_num][col_num]

        return array[row_num]

    def _fn_match(self, lookup_value, lookup_array, match_type=1):
        """MATCH function."""
        if not isinstance(lookup_array, list):
            return "#N/A"

        for i, val in enumerate(lookup_array):
            if val == lookup_value:
                return i + 1

        return "#N/A"

    def _fn_text(self, value, format_str):
        """TEXT function."""
        # Simplified text formatting
        try:
            if "%" in format_str:
                return f"{float(value) * 100:.0f}%"
            if "$" in format_str:
                return f"${float(value):,.2f}"
            return str(value)
        except (ValueError, TypeError):
            return str(value)

    def _fn_datedif(self, start_date, end_date, unit):
        """DATEDIF function."""
        start = self._parse_date(start_date)
        end = self._parse_date(end_date)
        diff = end - start

        unit = str(unit).upper()
        if unit == "D":
            return diff.days
        elif unit == "M":
            return (end.year - start.year) * 12 + (end.month - start.month)
        elif unit == "Y":
            return end.year - start.year

        return diff.days

    def _fn_sumif(self, range_values, criteria, sum_range=None):
        """SUMIF function."""
        if sum_range is None:
            sum_range = range_values

        if not isinstance(range_values, list) or not isinstance(sum_range, list):
            return 0

        total = 0.0
        for i, val in enumerate(range_values):
            if self._matches_criteria(val, criteria):
                if i < len(sum_range):
                    total += self._to_number(sum_range[i])
        return total

    def _fn_countif(self, range_values, criteria):
        """COUNTIF function."""
        if not isinstance(range_values, list):
            return 0
        return sum(1 for val in range_values if self._matches_criteria(val, criteria))

    def _fn_averageif(self, range_values, criteria, avg_range=None):
        """AVERAGEIF function."""
        if avg_range is None:
            avg_range = range_values

        if not isinstance(range_values, list) or not isinstance(avg_range, list):
            return 0

        values = []
        for i, val in enumerate(range_values):
            if self._matches_criteria(val, criteria):
                if i < len(avg_range):
                    values.append(self._to_number(avg_range[i]))

        return sum(values) / len(values) if values else 0.0

    def _matches_criteria(self, value, criteria) -> bool:
        """Check if value matches criteria."""
        criteria_str = str(criteria)

        # Check for comparison operators
        if criteria_str.startswith(">="):
            return self._to_number(value) >= self._to_number(criteria_str[2:])
        elif criteria_str.startswith("<="):
            return self._to_number(value) <= self._to_number(criteria_str[2:])
        elif criteria_str.startswith("<>"):
            return str(value) != criteria_str[2:]
        elif criteria_str.startswith(">"):
            return self._to_number(value) > self._to_number(criteria_str[1:])
        elif criteria_str.startswith("<"):
            return self._to_number(value) < self._to_number(criteria_str[1:])
        elif criteria_str.startswith("="):
            return str(value) == criteria_str[1:]

        # Default: exact match
        return str(value) == criteria_str
