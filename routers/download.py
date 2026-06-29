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
    # flat fallbacks (used only if per_sw_inputs is empty)
    annual:          float = 0
    advent:          float = 0
    onshore:         float = 0
    # per-software inputs sent by the dashboard
    per_sw_inputs:   dict  = {}
    keystore_values: dict  = {}


@router.post("/")
def download(req: DownloadRequest):
    session = get_session(req.session_id)
    sw_list = req.software

    # Build each table per-software so each sw gets its own inputs
    table1_list: list = []
    table2_data: dict = {}
    table3_data: dict = {}
    table4_data: dict = {}

    for sw in sw_list:
        sw_inp  = req.per_sw_inputs.get(sw, {})
        annual  = float(sw_inp.get("annual",  req.annual))
        advent  = float(sw_inp.get("advent",  req.advent))
        onshore = float(sw_inp.get("onshore", req.onshore))

        t1 = build_table1(
            sw_agg        = session.sw_agg,
            software_list = [sw],
            annual        = annual,
            advent        = advent,
            overrides     = session.overrides,
        )
        table1_list.extend(t1)

        t2 = build_table2(
            records       = session.records,
            sw_agg        = session.sw_agg,
            software_list = [sw],
            advent        = advent,
            onshore       = onshore,
            overrides     = session.overrides,
        )
        table2_data.update(t2)

        t3 = build_table3(
            records       = session.records,
            sw_agg        = session.sw_agg,
            software_list = [sw],
            annual        = annual,
            advent        = advent,
            onshore       = onshore,
            overrides     = session.overrides,
        )
        table3_data.update(t3)

        t4 = build_table4(
            records       = session.records,
            sw_agg        = session.sw_agg,
            software_list = [sw],
            overrides     = session.overrides,
        )
        table4_data.update(t4)

    keystore_data = build_table_keystore(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        user_values   = req.keystore_values,
    )

    output_path = generate_report(
        file_path     = session.file_path,
        table1_data   = table1_list,
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