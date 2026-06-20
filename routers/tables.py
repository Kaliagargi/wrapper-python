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
    annual_v = annual if annual is not None else session.user_inputs["annual"]

    data = build_table1(
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = annual_v,
        advent        = advent,
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
    advent_v  = advent  or 0
    onshore_v = onshore or 0
    

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