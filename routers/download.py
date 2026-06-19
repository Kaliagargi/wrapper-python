# routers/download.py

import os
from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from core.session import get_session
from services.excel_writer import generate_report
from services.table_builder import (
    build_table1, build_table2, build_table3,
    build_table4, build_table_keystore,
)

router = APIRouter(prefix="/download", tags=["Download"])


class DownloadRequest(BaseModel):
    session_id:      str
    software:        list
    annual:          float = 0
    advent:          float = 0
    onshore:         float = 0
    keystore_values: dict  = {}


@router.post("/")
def download(req: DownloadRequest):
    session = get_session(req.session_id)
    sw_list = req.software

    table1_data = build_table1(
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = req.annual,
    )
    table2_data = build_table2(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        advent        = req.advent,
        onshore       = req.onshore,
    )
    table3_data = build_table3(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = req.annual,
        advent        = req.advent,
        onshore       = req.onshore,
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
        annual        = req.annual,
        advent        = req.advent,
        onshore       = req.onshore,
        user_values   = req.keystore_values,
    )

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