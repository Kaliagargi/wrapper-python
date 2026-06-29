# routers/tables.py

from fastapi import APIRouter, Query
from core.session import get_session
from services.table_builder import (
    get_software_list,
    build_table1,
    build_table2,
    build_table3,
    build_table4,
)

router = APIRouter(prefix="/tables", tags=["Tables"])

# routers/tables.py
from services.excel_writer import save_sheet
from services.table_builder import (
    get_developer_list,
    get_software_list,
    get_software_by_developer,
    build_table1,
    build_table2,
    build_table3,
    build_table4,
)

@router.get("/developer-list")
def developer_list(session_id: str = Query(...)):
    session    = get_session(session_id)
    developers = get_developer_list(session.sw_agg)
    return {"success": True, "count": len(developers), "data": developers}


@router.get("/software-by-developer")
def software_by_developer(
    session_id:  str = Query(...),
    developers:  str = Query(...),
):
    session  = get_session(session_id)
    dev_list = [d.strip() for d in developers.split(",")]
    data     = get_software_by_developer(session.sw_agg, dev_list)
    return {"success": True, "count": len(data), "data": data}

@router.get("/table1")
def table1(
    session_id: str   = Query(...),
    software:   str   = Query(...),
    annual:     float = Query(None),
    advent:     float = Query(None),
):
    session  = get_session(session_id)
    sw_list  = [s.strip() for s in software.split(",")]
    annual_v = annual if annual is not None else 0

    data = build_table1(
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = annual_v,
        advent        = advent,
        overrides     = session.overrides,
    )

    save_sheet(
        file_path  = session.file_path,
        sheet_name = "Licence Summary",
        data       = data,
    )

    return {"success": True, "count": len(data), "data": data}


@router.get("/table2")
def table2(
    session_id: str   = Query(...),
    software:   str   = Query(...),
    advent:     float = Query(None),
    onshore:    float = Query(None),
):
    session   = get_session(session_id)
    sw_list   = [s.strip() for s in software.split(",")]
    advent_v  = advent  or 0
    onshore_v = onshore or 0

    data = build_table2(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        advent        = advent_v,
        onshore       = onshore_v,
        overrides     = session.overrides,
    )

    save_sheet(
        file_path  = session.file_path,
        sheet_name = "Allocated",
        data       = data,
    )

    return {"success": True, "data": data}


@router.get("/table3")
def table3(
    session_id: str   = Query(...),
    software:   str   = Query(...),
    annual:     float = Query(None),
    advent:     float = Query(None),
    onshore:    float = Query(None),
):
    session   = get_session(session_id)
    sw_list   = [s.strip() for s in software.split(",")]
    annual_v  = annual  or 0
    advent_v  = advent  or 0
    onshore_v = onshore or 0

    data = build_table3(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = annual_v,
        advent        = advent_v,
        onshore       = onshore_v,
        overrides     = session.overrides,
    )

    save_sheet(
        file_path  = session.file_path,
        sheet_name = "Required",
        data       = data,
    )

    return {"success": True, "data": data}


@router.get("/table4")
def table4(
    session_id: str = Query(...),
    software:   str = Query(...),
):
    session = get_session(session_id)
    sw_list = [s.strip() for s in software.split(",")]

    data = build_table4(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        overrides     = session.overrides,
    )

    save_sheet(
        file_path  = session.file_path,
        sheet_name = "ISL",
        data       = data,
    )

    return {"success": True, "data": data}


# ─────────────────────────────────────────────
# SAVE OVERRIDES + RECOMPUTE (per software)
# ─────────────────────────────────────────────

from pydantic import BaseModel
from typing import Optional

class DeptEdit(BaseModel):
    grand_ltc: float
    others:    float

class OverrideRequest(BaseModel):
    session_id:  str
    software:    str
    own_lic:     float
    lease_lic:   float
    dept_totals: dict[str, DeptEdit]   # {dept: {grand_ltc, others}}
    # user inputs passed through so tables recompute correctly
    annual:      float = 0
    advent:      float = 0
    onshore:     float = 0

@router.post("/reset-overrides")
def reset_overrides(
    session_id: str = Query(...),
    software:   str = Query(...),
):
    """Clears overrides for one software so next fetch returns original parsed values."""
    session = get_session(session_id)
    if software in session.overrides:
        del session.overrides[software]
    return {"success": True}
    """
    1. Validates ISL dept totals (grand_ltc + others) sum == own_lic + lease_lic
    2. Saves overrides to session
    3. Recomputes all 4 tables for this software
    4. Returns fresh table data so frontend can re-render
    """
    session = get_session(req.session_id)
    sw      = req.software

    # ── Validation ───────────────────────────
    expected_total = req.own_lic + req.lease_lic
    isl_total = sum(
        d.grand_ltc + d.others
        for d in req.dept_totals.values()
    )

    # allow small float tolerance
    if abs(isl_total - expected_total) > 0.01:
        return {
            "success":   False,
            "message":   (
                f"ISL dept totals ({round(isl_total, 4)}) do not match "
                f"Licence total ({round(expected_total, 4)}). "
                f"Difference: {round(isl_total - expected_total, 4)}"
            ),
        }

    # ── Save overrides ────────────────────────
    session.overrides[sw] = {
        "own_lic":    req.own_lic,
        "lease_lic":  req.lease_lic,
        "dept_totals": {
            dept: {"grand_ltc": d.grand_ltc, "others": d.others}
            for dept, d in req.dept_totals.items()
        },
    }

    # ── Recompute all 4 tables ────────────────
    sw_list = [sw]
    ovr     = session.overrides

    t1 = build_table1(
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = req.annual,
        advent        = req.advent,
        overrides     = ovr,
    )
    t2 = build_table2(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        advent        = req.advent,
        onshore       = req.onshore,
        overrides     = ovr,
    )
    t3 = build_table3(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = req.annual,
        advent        = req.advent,
        onshore       = req.onshore,
        overrides     = ovr,
    )
    t4 = build_table4(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        overrides     = ovr,
    )

    return {
        "success": True,
        "data": {
            "t1": t1,
            "t2": t2,
            "t3": t3,
            "t4": t4,
        },
    }