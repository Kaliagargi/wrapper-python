# routers/download.py

import os
from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from core.session import get_session
from services.excel_writer import get_output_path, generate_report
from services.table_builder import (
    build_table1,
    build_table2,
    build_table3,
    build_table4,
    build_table_keystore,
)

router = APIRouter(prefix="/download", tags=["Download"])


@router.get("/")
def download(
    session_id: str   = Query(...),
    software:   str   = Query(...),
    annual:     float = Query(None),
    advent:     float = Query(None),
    onshore:    float = Query(None),
):
    """
    Builds all 5 tables and pushes Excel file to outputs/ folder.
    Returns the file as download.
    """
    session   = get_session(session_id)
    sw_list   = [s.strip() for s in software.split(",")]
    annual_v  = annual  if annual  is not None else session.user_inputs["annual"]
    advent_v  = advent  if advent  is not None else session.user_inputs["advent"]
    onshore_v = onshore if onshore is not None else session.user_inputs["onshore"]

    # Build all tables
    table1_data = build_table1(
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = annual_v,
    )
    table2_data = build_table2(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        advent        = advent_v,
        onshore       = onshore_v,
    )
    table3_data = build_table3(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = annual_v,
        advent        = advent_v,
        onshore       = onshore_v,
    )
    table4_data = build_table4(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
    )
    keystore_data = build_table_keystore(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual_v  = annual  or 0,
        advent_v  = advent  or 0,
        onshore_v = onshore or 0,
     )

    # Generate and save Excel
    output_path = generate_report(
        file_path     = session.file_path,
        table1_data   = table1_data,
        table2_data   = table2_data,
        table3_data   = table3_data,
        table4_data   = table4_data,
        keystore_data = keystore_data,
    )

    return FileResponse(
        path       = output_path,
        filename   = os.path.basename(output_path),
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )