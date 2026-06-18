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

@router.get("/table1")
def table1(
    session_id: str   = Query(...),
    software:   str   = Query(...),
    annual:     float = Query(None),
):
    session  = get_session(session_id)
    sw_list  = [s.strip() for s in software.split(",")]
    annual_v = annual if annual is not None else session.user_inputs["annual"]

    data = build_table1(
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = annual_v,
    )

    # Save to Excel immediately
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
    advent_v  = advent  if advent  is not None else session.user_inputs["advent"]
    onshore_v = onshore if onshore is not None else session.user_inputs["onshore"]

    data = build_table2(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        advent        = advent_v,
        onshore       = onshore_v,
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
    annual_v  = annual  if annual  is not None else session.user_inputs["annual"]
    advent_v  = advent  if advent  is not None else session.user_inputs["advent"]
    onshore_v = onshore if onshore is not None else session.user_inputs["onshore"]

    data = build_table3(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = annual_v,
        advent        = advent_v,
        onshore       = onshore_v,
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
    )

    save_sheet(
        file_path  = session.file_path,
        sheet_name = "ISL",
        data       = data,
    )

    return {"success": True, "data": data}