# routers/keystore.py

from fastapi import APIRouter, Query
from core.session import get_session
from services.table_builder import build_table_keystore,toggle_key, add_key

router = APIRouter(prefix="/keystore", tags=["Keystore"])


@router.get("/table")
def get_keystore_table(
    session_id: str   = Query(...),
    software:   str   = Query(...),
    user_values:   dict = {},
    
):
    session = get_session(session_id)
    sw_list = [s.strip() for s in software.split(",")]

    data = build_table_keystore(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        
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
   
    success = add_key(software, dept, key_id, active)

    return {
        "success": success,
        "message": f"Key '{key_id}' added" if success
                   else f"Key '{key_id}' already exists for {software}/{dept}",
    }