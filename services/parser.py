# services/parser.py

import openpyxl
import os
from collections import defaultdict


# ─────────────────────────────────────────────
# STEP 1 — Unmerge all merged cells
# ─────────────────────────────────────────────

def unmerge_and_fill(file_path: str) -> tuple:
    """
    Finds the sheet with 'project' in its name.
    Unmerges all merged cells and fills each cell
    with the top-left value of its merged range.
    Saves to a temp file so original is never touched.
    """
    wb = openpyxl.load_workbook(file_path)

    # Find sheet flexibly — works even if name changes slightly
    sheet_name = None
    for name in wb.sheetnames:
        if "project" in name.lower():
            sheet_name = name
            break

    if not sheet_name:
        raise ValueError(
            f"No sheet with 'project' in name found. "
            f"Available: {wb.sheetnames}"
        )

    ws = wb[sheet_name]

    # Convert to list first — cannot modify while iterating
    for merge_range in list(ws.merged_cells.ranges):
        top_left_value = ws.cell(
            merge_range.min_row,
            merge_range.min_col
        ).value

        ws.unmerge_cells(str(merge_range))

        for row in ws.iter_rows(
            min_row=merge_range.min_row,
            max_row=merge_range.max_row,
            min_col=merge_range.min_col,
            max_col=merge_range.max_col,
        ):
            for cell in row:
                cell.value = top_left_value

    temp_path = file_path.replace(".xlsx", "_temp_unmerged.xlsx")
    wb.save(temp_path)
    return temp_path, sheet_name


# ─────────────────────────────────────────────
# STEP 2 — Detect header row dynamically
# ─────────────────────────────────────────────

def detect_header_row(ws) -> int:
    """
    Scans rows to find the one containing 'Developer'
    in column 1 — that's our true header row.
    This way it works even if rows are added above.
    """
    for row_idx in range(1, 20):
        val = ws.cell(row_idx, 1).value
        if val and str(val).strip().lower() == "developer":
            return row_idx

    raise ValueError(
        "Could not find header row with 'Developer' in column 1. "
        "Check your Excel structure."
    )


# ─────────────────────────────────────────────
# STEP 3 — Detect project columns dynamically
# ─────────────────────────────────────────────

def detect_project_layout(ws, header_row: int) -> list:
    """
    Scans header row for 'LTC' — each LTC marks
    the start of a new project column group.

    Each project group is either:
      Case 1: LTC | Others | Total(P)   → has_others = True
      Case 2: LTC only                  → has_others = False

    Project metadata is read from rows above header row:
      header_row - 5 → Location
      header_row - 4 → Project name
      header_row - 3 → Project manager
      header_row - 2 → Status
      header_row - 1 → Approval date
    """
    project_layout = []
    seen_projects  = set()

    location_row      = header_row - 5
    project_row       = header_row - 4
    manager_row       = header_row - 3
    status_row        = header_row - 2
    approval_date_row = header_row - 1

    for col in range(1, ws.max_column + 1):
        header_val = ws.cell(header_row, col).value
        if not header_val:
            continue

        if str(header_val).strip().upper() != "LTC":
            continue

        # Read project metadata from rows above
        project_name  = ws.cell(project_row,       col).value
        location      = ws.cell(location_row,      col).value
        manager       = ws.cell(manager_row,        col).value
        status        = ws.cell(status_row,         col).value
        approval_date = ws.cell(approval_date_row,  col).value

        # Skip blank or duplicate projects
        if not project_name:
            continue
        project_name_clean = str(project_name).strip()
        if project_name_clean in seen_projects:
            continue

        # Skip summary columns misread as projects
        SKIP_KEYWORDS = {"ltc", "total", "others", "valdel", "grand"}
        if project_name_clean.lower() in SKIP_KEYWORDS:
            continue

        # Skip if location equals name (header being misread)
        location_clean = str(location).strip().lower() if location else ""
        if location_clean == project_name_clean.lower():
            continue

        seen_projects.add(project_name_clean)

        # Check if Others/Valdel column exists
        next_header = str(
            ws.cell(header_row, col + 1).value or ""
        ).strip().upper()

        has_others = next_header not in ("LTC", "TOTAL", "")

        project_layout.append({
            "name":          project_name_clean,
            "location":      str(location).strip() if location else "",
            "manager":       str(manager).strip()  if manager  else "",
            "status":        str(status).strip()   if status   else "",
            "approval_date": approval_date,
            "ltc_col":       col,
            "valdel_col":    col + 1 if has_others else None,
            "total_p_col":   col + 2 if has_others else None,
        })

    return project_layout


# ─────────────────────────────────────────────
# STEP 4 — Detect summary columns dynamically
# ─────────────────────────────────────────────

def detect_summary_columns(ws, header_row: int) -> dict:
    """
    Scans header row for summary columns on the right side.
    Looks for: Own Lic, Lease Lic, Total
    Uses keyword matching so column names can vary slightly.
    """
    summary = {}

    for col in range(1, ws.max_column + 1):
        val = ws.cell(header_row, col).value
        if not val:
            continue
        val_clean = str(val).strip().lower()

        if "own" in val_clean:
            summary["own_lic_col"] = col
        elif "lease" in val_clean:
            summary["lease_lic_col"] = col
        elif val_clean == "total":
            summary["total_col"] = col
        elif "loc" in val_clean and "1" in val_clean and "ltc" in val_clean:
            summary["loc1_ltc_col"] = col
        elif "loc" in val_clean and "2" in val_clean and "ltc" in val_clean:
            summary["loc2_ltc_col"] = col

    return summary


# ─────────────────────────────────────────────
# STEP 5 — Parse all data rows
# ─────────────────────────────────────────────

def parse_source(
    ws,
    header_row:     int,
    project_layout: list,
    summary_cols:   dict
) -> list:
    """
    Reads every row after header_row as a data record.
    Uses ffill for Developer and Software columns.
    Skips rows where dept is None or 'total'.
    Safely handles missing valdel/total_p columns.
    """
    records     = []
    current_dev = None
    current_sw  = None

    for row_idx in range(header_row + 1, ws.max_row + 1):
        dev  = ws.cell(row_idx, 1).value
        sw   = ws.cell(row_idx, 2).value
        dept = ws.cell(row_idx, 3).value

        # Skip total/subtotal rows
        if dept and str(dept).strip().lower() == "total":
            continue

        # Skip fully empty rows
        if dev is None and sw is None and dept is None:
            continue

        # ffill developer and software
        if dev: current_dev = str(dev).strip()
        if sw:  current_sw  = str(sw).strip()

        # Skip rows with no dept
        if dept is None:
            continue

        # Read per-project licence values safely
        proj_data = {}
        grand_ltc = 0

        for p in project_layout:
            def safe_num(value):
                try:
                    return float(value) if value is not None else 0
                except (ValueError, TypeError):
                    return 0

            ltc_v    = safe_num(ws.cell(row_idx, p["ltc_col"]).value)
            
            valdel_v = 0
            if p["valdel_col"] is not None:
                valdel_v = safe_num(ws.cell(row_idx, p["valdel_col"]).value)
            
            total_p = 0
            if p["total_p_col"] is not None:
                total_p = safe_num(ws.cell(row_idx, p["total_p_col"]).value)
                grand_ltc += ltc_v

            proj_data[p["name"]] = {
                "ltc":     ltc_v,
                "valdel":  valdel_v,
                "total_p": total_p,
            }

        # Read summary columns safely
        own_lic   = ws.cell(
            row_idx, summary_cols.get("own_lic_col", 0)
        ).value or 0 if summary_cols.get("own_lic_col") else 0

        lease_lic = ws.cell(
            row_idx, summary_cols.get("lease_lic_col", 0)
        ).value or 0 if summary_cols.get("lease_lic_col") else 0

        others    = ws.cell(
            row_idx, summary_cols.get("loc1_ltc_col", 0)
        ).value or 0 if summary_cols.get("loc1_ltc_col") else 0

        records.append({
            "developer": current_dev,
            "software":  current_sw,
            "dept":      str(dept).strip(),
            "projects":  proj_data,
            "grand_ltc": grand_ltc,
            "others":    others,
            "total_lic": grand_ltc + others,
            "own_lic":   own_lic,
            "lease_lic": lease_lic,
        })

    return records


# ─────────────────────────────────────────────
# STEP 6 — Aggregate by software
# ─────────────────────────────────────────────

def aggregate_by_software(records: list) -> dict:
    """
    Groups dept-level records by software.
    Skips software where own_lic = 0
    (these don't need to be purchased).
    """
    agg = defaultdict(lambda: {
        "developer": "",
        "total_lic": 0,
        "lease_lic": 0,
        "own_lic":   0,
        "depts":     [],
    })

    for r in records:
        sw = r["software"]
        if not sw:
            continue

        agg[sw]["developer"]  = r["developer"]
        agg[sw]["total_lic"] += r["total_lic"]
        agg[sw]["lease_lic"] += r["lease_lic"]
        agg[sw]["own_lic"]   += r["own_lic"]
        agg[sw]["depts"].append(r)

    return dict(agg)


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────

def parse_excel(file_path: str) -> tuple:
    """
    Full pipeline:
      1. Unmerge cells         → clean temp file
      2. Detect header row     → flexible row detection
      3. Detect project cols   → dynamic, handles missing Others
      4. Detect summary cols   → dynamic, keyword matching
      5. Parse all rows        → ffill, skip blanks/totals
      6. Aggregate by software → grouped summary

    Returns:
      (project_layout, records, sw_agg)

    Cleans up temp file whether it succeeds or fails.
    """
    from core.errors import InvalidFileError, SheetNotFoundError

    temp_path = None

    try:
        temp_path, sheet_name = unmerge_and_fill(file_path)

        wb         = openpyxl.load_workbook(temp_path)
        ws         = wb[sheet_name]
        header_row = detect_header_row(ws)

        project_layout = detect_project_layout(ws, header_row)

        if not project_layout:
            raise InvalidFileError(
                "No project columns found. "
                "Check that row 8 contains 'LTC' headers."
            )

        summary_cols = detect_summary_columns(ws, header_row)
        records      = parse_source(ws, header_row, project_layout, summary_cols)

        if not records:
            raise InvalidFileError(
                "No data rows found after header row. "
                "Check your Excel has data from row 9 onwards."
            )

        sw_agg = aggregate_by_software(records)

        return project_layout, records, sw_agg

    except (InvalidFileError, SheetNotFoundError):
        # Re-raise our custom errors as-is
        raise

    except ValueError as e:
        raise SheetNotFoundError(str(e))

    except Exception as e:
        raise InvalidFileError(f"Unexpected error parsing file: {str(e)}")

    finally:
        # Always clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


