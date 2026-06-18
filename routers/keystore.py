# routers/keystore.py

from fastapi import APIRouter, Query
from core.session import get_session
from core.keystore import toggle_key, add_key
from services.table_builder import build_table_keystore

router = APIRouter(prefix="/keystore", tags=["Keystore"])


@router.get("/table")
def get_keystore_table(
    session_id: str   = Query(...),
    software:   str   = Query(...),
    annual:     float = Query(0),
    advent:     float = Query(0),
    onshore:    float = Query(0),
):
    session = get_session(session_id)
    sw_list = [s.strip() for s in software.split(",")]

    data = build_table_keystore(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        annual        = annual,
        advent        = advent,
        onshore       = onshore,
    )

    return {"success": True, "data": data}

# ─────────────────────────────────────────────
# TOGGLE KEY ACTIVE STATUS
# ─────────────────────────────────────────────

@router.post("/keys/toggle")
def toggle_key_endpoint(
    software: str = Query(...),
    dept:     str = Query(...),
    key_id:   str = Query(...),
):
    success = toggle_key(software, dept, key_id)
    return {
        "success": success,
        "message": f"Toggled '{key_id}'" if success
                   else f"Key '{key_id}' not found for {software}/{dept}",
    }


# ─────────────────────────────────────────────
# ADD NEW KEY
# ─────────────────────────────────────────────

@router.post("/keys/add")
def add_key_endpoint(
    session_id: str  = Query(...),
    software:   str  = Query(...),
    dept:       str  = Query(...),
    key_id:     str  = Query(...),
    active:     bool = Query(True),
):
    session = get_session(session_id)

    if software not in session.sw_agg:
        return {
            "success": False,
            "message": f"Software '{software}' not found in Excel data.",
            "available_software": list(session.sw_agg.keys()),
        }

    sw_records  = [r for r in session.records if r["software"] == software]
    valid_depts = {r["dept"].lower() for r in sw_records}

    if dept.strip().lower() not in valid_depts:
        return {
            "success": False,
            "message": f"Dept '{dept}' not found for software '{software}'.",
            "available_depts": list(valid_depts),
        }

    success = add_key(software, dept, key_id, active)

    return {
        "success": success,
        "message": f"Key '{key_id}' added" if success
                   else f"Key '{key_id}' already exists for {software}/{dept}",
    }