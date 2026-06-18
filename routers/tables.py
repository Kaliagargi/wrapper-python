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


# ─────────────────────────────────────────────
# SOFTWARE LIST
# ─────────────────────────────────────────────

@router.get("/software-list")
def software_list(session_id: str = Query(...)):
    """
    Returns software where lease_lic > 0.
    Use this to populate dropdowns in your UI.
    """
    session  = get_session(session_id)
    software = get_software_list(session.sw_agg)

    return {
        "success": True,
        "count":   len(software),
        "data":    software,
    }


# ─────────────────────────────────────────────
# TABLE 1 — Licence Summary
# ─────────────────────────────────────────────

@router.get("/table1")
def table1(session_id: str = Query(...)):
    """
    All software with Total Lic and Lease Lic.
    No software filter needed.
    """
    session = get_session(session_id)
    data    = build_table1(session.sw_agg)

    return {
        "success": True,
        "count":   len(data),
        "data":    data,
    }


# ─────────────────────────────────────────────
# TABLE 2 — Allocated
# ─────────────────────────────────────────────

@router.get("/table2")
def table2(
    session_id: str = Query(...),
    software:   str = Query(..., description="Software name to filter by"),
):
    """
    Allocated licences per dept per project for selected software.
    """
    session = get_session(session_id)
    data    = build_table2(
        session.records,
        session.sw_agg,
        software,
        session.project_layout,
    )

    return {
        "success":  True,
        "software": software,
        "count":    len(data),
        "data":     data,
    }


# ─────────────────────────────────────────────
# TABLE 3 — Required
# ─────────────────────────────────────────────

@router.get("/table3")
def table3(
    session_id: str = Query(...),
    software:   str = Query(..., description="Software name to filter by"),
):
    """
    Required licences (deficit) for selected software.
    """
    session = get_session(session_id)
    data    = build_table3(
        session.records,
        session.sw_agg,
        software,
    )

    return {
        "success":  True,
        "software": software,
        "count":    len(data),
        "data":     data,
    }


# ─────────────────────────────────────────────
# TABLE 4 — ISL
# ─────────────────────────────────────────────

@router.get("/table4")
def table4(
    session_id: str = Query(...),
    software:   str = Query(..., description="Software name to filter by"),
):
    """
    In-stock licences (own + lease) for selected software.
    """
    session = get_session(session_id)
    data    = build_table4(
        session.records,
        session.sw_agg,
        software,
    )

    return {
        "success":  True,
        "software": software,
        "count":    len(data),
        "data":     data,
    }