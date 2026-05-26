"""
app/services/excel_export.py
─────────────────────────────────────────────────────────────────────────────
Builds a fully-formatted .xlsx workbook and returns it as a BytesIO buffer.

WHY SERVER-SIDE EXPORT?
  The browser-based SheetJS approach (from the earlier dashboard widget) is
  convenient for prototyping but has real limitations:
    - No support for real Excel formulas (only static values).
    - No merged cells, no frozen panes, no font colours in shortfall cells.
    - Styles are applied using an undocumented compatibility layer.

  By generating the file on the server with openpyxl, we get:
    - Full Excel feature support (freeze panes, merged cells, colour coding).
    - Consistent output regardless of browser or OS.
    - A single code path for both the API download and any future
      scheduled exports (e.g. emailing a weekly report).

ARCHITECTURE:
  build_workbook() is the only public function.  It delegates to private
  _build_*() functions, one per sheet.  Each sheet builder follows the same
  pattern: write headers, write data rows, write total row, set column widths.

  None of these functions make HTTP calls or touch the database — they only
  transform data objects (NotToBuyResponse, etc.) into Excel cells.  This
  makes them independently testable and easy to extend.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.schemas import (
    AllocatedResponse,
    ISLResponse,
    KeystoreRow,
    NotToBuyResponse,
    RequiredResponse,
)

# ── Style constants ───────────────────────────────────────────────────────────
# Defined once at module level so every sheet uses the same visual language.
# Changing HDR_FILL here updates the header colour in all 5 sheets at once.

# Dark navy header row — high contrast with white text
HDR_FILL = PatternFill("solid", fgColor="1F4E79")
HDR_FONT = Font(bold=True, color="FFFFFF", name="Arial", size=10)

# Slightly lighter blue for sub-header rows (location headers, etc.)
SUB_FILL = PatternFill("solid", fgColor="2E75B6")

# Light blue alternating row fill — improves readability in wide tables
ALT_FILL = PatternFill("solid", fgColor="D9E2F3")

# Plain white for even-numbered rows
WHT_FILL = PatternFill("solid", fgColor="FFFFFF")

# Gold/yellow for totals and subtotals rows
TOT_FILL = PatternFill("solid", fgColor="FFF2CC")
TOT_FONT = Font(bold=True, name="Arial", size=10)

# Normal body text — consistent font across all cells
NRM_FONT = Font(name="Arial", size=10)

# Thin border on all four sides — applied to every cell so the table
# looks clean even when printed
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)


# ── Low-level cell helpers ────────────────────────────────────────────────────

def _hdr(ws, row: int, col: int, value, fill=None, font=None):
    """
    Write a styled header cell.

    Accepts optional fill/font overrides so sub-headers can use a
    different colour while keeping all other header styles the same.
    """
    c = ws.cell(row, col, value)
    c.font      = font  or HDR_FONT
    c.fill      = fill  or HDR_FILL
    c.border    = THIN_BORDER
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    return c


def _val(ws, row: int, col: int, value, alt: bool = False, bold: bool = False):
    """
    Write a standard data cell with alternating row fill.

    alt=True uses the light blue ALT_FILL; alt=False uses plain white.
    This creates the zebra-stripe pattern that makes wide tables readable.
    bold=True is used for totals within a row (e.g. LTC Total column).
    """
    c = ws.cell(row, col, value)
    c.font      = Font(name="Arial", size=10, bold=bold)
    c.fill      = ALT_FILL if alt else WHT_FILL
    c.border    = THIN_BORDER
    c.alignment = Alignment(horizontal="center", vertical="center")
    return c


def _total_row(ws, row: int, ncols: int, label: str = "TOTAL"):
    """
    Write a gold-coloured total row spanning ncols columns.

    The first cell gets the label (e.g. "TOTAL").
    Remaining cells are styled but left empty — the caller fills in the values.
    """
    c = ws.cell(row, 1, label)
    c.font      = TOT_FONT
    c.fill      = TOT_FILL
    c.border    = THIN_BORDER
    c.alignment = Alignment(horizontal="left", vertical="center")

    for col in range(2, ncols + 1):
        c2 = ws.cell(row, col)
        c2.font      = TOT_FONT
        c2.fill      = TOT_FILL
        c2.border    = THIN_BORDER
        c2.alignment = Alignment(horizontal="center", vertical="center")


def _set_col_widths(ws, widths: list[int]):
    """
    Set column widths in one call.  widths[0] → column A, widths[1] → B, etc.

    Excel column width units are approximately equal to the width of one
    character in the default font.  Width 14 ≈ 14 characters wide.
    """
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ── Sheet builders ────────────────────────────────────────────────────────────

def _build_not_to_buy(wb: Workbook, data: NotToBuyResponse) -> None:
    """
    Sheet 1: Not_To_Buy
    Shows each software with its total, own, lease licences and coverage %.
    One row per software (aggregated across all departments).
    """
    ws = wb.create_sheet("Not_To_Buy")

    # Header row
    _hdr(ws, 1, 1, "Developer / Software")
    _hdr(ws, 1, 2, "Total Licences")
    _hdr(ws, 1, 3, "Own Licences")
    _hdr(ws, 1, 4, "Lease Licences")
    _hdr(ws, 1, 5, "Coverage %")

    # Data rows — alternating fill (alt = True for even-indexed rows)
    for i, r in enumerate(data.rows):
        alt = i % 2 == 0
        # Developer/software cell is left-aligned (text, not a number)
        c = _val(ws, i + 2, 1, f"{r.developer} / {r.software}", alt=alt)
        c.alignment = Alignment(horizontal="left", vertical="center")
        _val(ws, i + 2, 2, r.total_lic,          alt=alt)
        _val(ws, i + 2, 3, r.own_lic,             alt=alt)
        _val(ws, i + 2, 4, r.lease_lic,           alt=alt)
        _val(ws, i + 2, 5, f"{r.coverage_pct}%",  alt=alt)

    # Total row — placed immediately after the last data row
    tr = len(data.rows) + 2
    _total_row(ws, tr, 5)
    ws.cell(tr, 2, data.total_lic).font  = TOT_FONT
    ws.cell(tr, 3, data.total_own).font  = TOT_FONT
    ws.cell(tr, 4, data.total_lease).font = TOT_FONT

    _set_col_widths(ws, [32, 16, 16, 16, 14])

    # Freeze row 1 so the header stays visible when scrolling
    ws.freeze_panes = "A2"


def _build_allocated(wb: Workbook, data: AllocatedResponse) -> None:
    """
    Sheet 2: Allocated
    Dept × Project matrix showing LTC allocated per project.
    Includes software subtotals after each software group.
    """
    ws = wb.create_sheet("Allocated")
    projects = data.projects

    # Dynamic number of columns depends on how many projects exist
    ncols = 3 + len(projects) + 2  # dev + sw + dept + [projects] + LTC total + grand total

    # Static header columns
    _hdr(ws, 1, 1, "Developer")
    _hdr(ws, 1, 2, "Software")
    _hdr(ws, 1, 3, "Dept")

    # One header column per project (dynamic)
    for pi, p in enumerate(projects):
        _hdr(ws, 1, 4 + pi, p.upper())

    # Aggregate header columns
    _hdr(ws, 1, 4 + len(projects),     "LTC Total")
    _hdr(ws, 1, 4 + len(projects) + 1, "Grand Total")

    row = 2
    for i, r in enumerate(data.rows):
        alt = i % 2 == 0
        _val(ws, row, 1, r.developer, alt=alt)
        _val(ws, row, 2, r.software,  alt=alt)
        c = _val(ws, row, 3, r.dept, alt=alt)
        c.alignment = Alignment(horizontal="left", vertical="center")

        # Fill in the per-project LTC count — 0 if the project isn't in this record
        for pi, p in enumerate(projects):
            _val(ws, row, 4 + pi, r.project_ltc.get(p, 0), alt=alt)

        # LTC total and grand total for the row
        _val(ws, row, 4 + len(projects),     r.ltc_total,   alt=alt, bold=True)
        _val(ws, row, 4 + len(projects) + 1, r.grand_total, alt=alt)
        row += 1

    # Subtotal rows — one per software, rendered in gold after each group's data rows
    for sw, st in data.software_subtotals.items():
        c = ws.cell(row, 1, f"{sw} — Subtotal")
        c.font      = TOT_FONT
        c.fill      = TOT_FILL
        c.border    = THIN_BORDER
        c.alignment = Alignment(horizontal="left", vertical="center")
        # Merge the developer/software/dept label cells for a cleaner look
        ws.merge_cells(
            start_row=row, start_column=1,
            end_row=row,   end_column=3,
        )
        for pi, p in enumerate(projects):
            _val(ws, row, 4 + pi, st["project_ltc"].get(p, 0))
        _val(ws, row, 4 + len(projects),     st["ltc_total"],   bold=True)
        _val(ws, row, 4 + len(projects) + 1, st["grand_total"])
        row += 1

    # Dynamic column widths: fixed for first 3, 12 for each project, then 2 more
    _set_col_widths(ws, [14, 14, 10] + [12] * len(projects) + [12, 14])

    # Freeze columns A-C and row 1 so headers and labels stay visible on scroll
    ws.freeze_panes = "D2"


def _build_required(wb: Workbook, data: RequiredResponse) -> None:
    """
    Sheet 3: Required
    Shows the gap between total licences needed and LTC currently allocated.
    Shortfall cells are rendered in red; surplus cells in green.
    """
    ws = wb.create_sheet("Required")

    headers = ["Developer", "Software", "Dept", "Total Lic", "Allocated LTC", "Required", "Status"]
    for ci, h in enumerate(headers, 1):
        _hdr(ws, 1, ci, h)

    for i, r in enumerate(data.rows):
        alt = i % 2 == 0
        _val(ws, i + 2, 1, r.developer,     alt=alt)
        _val(ws, i + 2, 2, r.software,      alt=alt)
        c = _val(ws, i + 2, 3, r.dept,      alt=alt)
        c.alignment = Alignment(horizontal="left", vertical="center")
        _val(ws, i + 2, 4, r.total_lic,     alt=alt)
        _val(ws, i + 2, 5, r.allocated_ltc, alt=alt)

        # Colour-code the Required cell based on status:
        # Red + bold for shortfall (attention needed), green for surplus/ok
        req_cell = _val(ws, i + 2, 6, r.required, alt=alt)
        if r.required > 0:
            req_cell.font = Font(name="Arial", size=10, color="C00000", bold=True)  # dark red
        elif r.required < 0:
            req_cell.font = Font(name="Arial", size=10, color="375623")             # dark green

        _val(ws, i + 2, 7, r.status.upper(), alt=alt)

    tr = len(data.rows) + 2
    _total_row(ws, tr, 7)
    ws.cell(tr, 4, data.total_lic).font        = TOT_FONT
    ws.cell(tr, 5, data.total_allocated).font  = TOT_FONT
    ws.cell(tr, 6, data.total_required).font   = TOT_FONT

    _set_col_widths(ws, [14, 14, 10, 14, 16, 12, 12])
    ws.freeze_panes = "A2"


def _build_isl(wb: Workbook, data: ISLResponse) -> None:
    """
    Sheet 4: ISL (In-Stock Licences)
    Shows own + lease licences held per department, total in-stock.
    """
    ws = wb.create_sheet("ISL")

    headers = ["Developer", "Software", "Dept", "Own Lic", "Lease Lic", "Total In-Stock"]
    for ci, h in enumerate(headers, 1):
        _hdr(ws, 1, ci, h)

    for i, r in enumerate(data.rows):
        alt = i % 2 == 0
        _val(ws, i + 2, 1, r.developer,      alt=alt)
        _val(ws, i + 2, 2, r.software,       alt=alt)
        c = _val(ws, i + 2, 3, r.dept,       alt=alt)
        c.alignment = Alignment(horizontal="left", vertical="center")
        _val(ws, i + 2, 4, r.own_lic,        alt=alt)
        _val(ws, i + 2, 5, r.lease_lic,      alt=alt)
        # Total in-stock is bold to make it easy to scan down the column
        _val(ws, i + 2, 6, r.total_in_stock, alt=alt, bold=True)

    tr = len(data.rows) + 2
    _total_row(ws, tr, 6)
    ws.cell(tr, 4, data.total_own).font        = TOT_FONT
    ws.cell(tr, 5, data.total_lease).font      = TOT_FONT
    ws.cell(tr, 6, data.total_in_stock).font   = TOT_FONT

    _set_col_widths(ws, [14, 14, 10, 14, 14, 16])
    ws.freeze_panes = "A2"


def _build_keystore(wb: Workbook, rows: list[KeystoreRow]) -> None:
    """
    Sheet 5: Keystore
    Shows all registered licence keys with their linked projects.
    If no keys have been registered yet, shows a placeholder message.
    """
    ws = wb.create_sheet("Keystore")

    headers = ["Developer", "Software", "Dept", "Key ID", "Linked Project", "Lic in Key", "Notes"]
    for ci, h in enumerate(headers, 1):
        _hdr(ws, 1, ci, h)

    if not rows:
        # Placeholder row so the sheet isn't confusingly empty
        c = ws.cell(2, 1, "No keys registered yet — use POST /keystore to add entries")
        c.font = Font(name="Arial", size=10, italic=True, color="595959")
    else:
        for i, r in enumerate(rows):
            alt = i % 2 == 0
            _val(ws, i + 2, 1, r.developer, alt=alt)
            _val(ws, i + 2, 2, r.software,  alt=alt)
            _val(ws, i + 2, 3, r.dept,      alt=alt)

            # Key ID is left-aligned — it's a string identifier, not a number
            c = _val(ws, i + 2, 4, r.key_id, alt=alt)
            c.alignment = Alignment(horizontal="left", vertical="center")

            _val(ws, i + 2, 5, r.project,   alt=alt)
            _val(ws, i + 2, 6, r.lic_count, alt=alt, bold=True)

            # Notes field is left-aligned for readability
            c2 = _val(ws, i + 2, 7, r.notes or "", alt=alt)
            c2.alignment = Alignment(horizontal="left", vertical="center")

        # Total row shows the sum of licences across all registered keys
        tr = len(rows) + 2
        _total_row(ws, tr, 7)
        ws.cell(tr, 6, sum(r.lic_count for r in rows)).font = TOT_FONT

    _set_col_widths(ws, [14, 14, 10, 24, 18, 14, 28])
    ws.freeze_panes = "A2"


# ── Public entry point ────────────────────────────────────────────────────────

def build_workbook(
    sheets:        list[str],
    not_to_buy:    NotToBuyResponse,
    allocated:     AllocatedResponse,
    required:      RequiredResponse,
    isl:           ISLResponse,
    keystore_rows: list[KeystoreRow],
) -> io.BytesIO:
    """
    Build the complete workbook and return it as a BytesIO buffer.

    WHY BytesIO?
      We never write to disk.  BytesIO is an in-memory file object.
      openpyxl writes to it exactly like it would to a real file.
      FastAPI's StreamingResponse reads from it and sends the bytes directly
      to the client.

      Disk-based approach would require: write file → read file → delete file.
      That's three disk operations and a race condition if two exports happen
      simultaneously.  BytesIO is faster, simpler, and safe under concurrency.

    sheets parameter:
      The caller specifies which sheets to include.  Unknown sheet names
      are silently ignored.  This allows partial exports (e.g. keystore only).
    """
    wb = Workbook()
    # Remove the default empty "Sheet" that openpyxl creates automatically.
    # Our sheets have specific names; keeping the empty one is confusing.
    wb.remove(wb.active)

    # Map sheet name → builder function.
    # This pattern means adding a new sheet requires only:
    #   1. Writing a _build_newsheet() function
    #   2. Adding one line here
    builders = {
        "not_to_buy": lambda: _build_not_to_buy(wb, not_to_buy),
        "allocated":  lambda: _build_allocated(wb, allocated),
        "required":   lambda: _build_required(wb, required),
        "isl":        lambda: _build_isl(wb, isl),
        "keystore":   lambda: _build_keystore(wb, keystore_rows),
    }

    for sheet_name in sheets:
        if sheet_name in builders:
            builders[sheet_name]()
        # Unknown sheet names are silently ignored — no error, no crash.
        # This is intentional: the client might send an outdated sheet list.

    # Write the workbook to an in-memory buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    # Reset the read position so the streaming response reads from the start
    buffer.seek(0)
    return buffer