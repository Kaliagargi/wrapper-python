# routers/keystore.py

from fastapi import APIRouter, Query
from core.keystore import get_keys, get_all_keys_for_software, add_key, hide_key
from core.session import get_session
from services.table_builder import build_table2, build_table4

router = APIRouter(prefix="/keystore", tags=["Keystore"])


# ─────────────────────────────────────────────
# GET KEYSTORE TABLE
# ─────────────────────────────────────────────

@router.get("/table")
def get_keystore_table(
    session_id: str = Query(...),
    software:   str = Query(..., description="Comma separated software names"),
    advent:     float = Query(0),
    onshore:    float = Query(0),
):
    """
    Returns full keystore table for selected software.
    Each row has:
    Software | Dept | ISL Value | Key ID | Allocated Value
    """
    session = get_session(session_id)
    sw_list = [s.strip() for s in software.split(",")]

    # Get allocated and ISL values
    allocated_data = build_table2(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
        advent        = advent,
        onshore       = onshore,
    )
    isl_data = build_table4(
        records       = session.records,
        sw_agg        = session.sw_agg,
        software_list = sw_list,
    )

    result = []

    for sw in sw_list:
        if sw not in allocated_data:
            continue

        # Build lookup for allocated values by dept
        alloc_lookup = {}
        for row in allocated_data[sw]["rows"]:
            if row["label"] != "Total":
                alloc_lookup[row["label"].lower()] = row["value"]

        # Build lookup for ISL values by dept
        isl_lookup = {}
        if sw in isl_data:
            for row in isl_data[sw]["rows"]:
                if row["dept"] != "TOTAL":
                    isl_lookup[row["dept"].lower()] = row["total"]

        # Get all keys for this software
        sw_keys = get_all_keys_for_software(sw)

        for dept, keys in sw_keys.items():
            isl_value   = isl_lookup.get(dept.lower(), 0)
            alloc_value = alloc_lookup.get(dept.lower(), None)

            for key_id in keys:
                result.append({
                    "software":        sw,
                    "dept":            dept,
                    "isl_value":       isl_value,       # Col 3 - pre-filled editable
                    "key_id":          key_id,           # Col 4
                    "allocated_value": alloc_value,      # Col 5 - from allocated or user input
                    "is_user_input":   alloc_value is None,
                })

    return {
        "success": True,
        "count":   len(result),
        "data":    result,
    }


# ─────────────────────────────────────────────
# GET KEYS FOR SOFTWARE + DEPT
# ─────────────────────────────────────────────

@router.get("/keys")
def get_keys_endpoint(
    software: str = Query(...),
    dept:     str = Query(...),
):
    """
    Returns active Key IDs for software + dept combination.
    Used to populate Key ID dropdown.
    """
    keys = get_keys(software, dept)
    return {
        "success":  True,
        "software": software,
        "dept":     dept,
        "keys":     keys,
    }


# ─────────────────────────────────────────────
# ADD NEW KEY
# ─────────────────────────────────────────────

@router.post("/keys/add")
def add_key_endpoint(
    software: str = Query(...),
    dept:     str = Query(...),
    key_id:   str = Query(...),
):
    """
    Adds a new Key ID for software + dept.
    Persists to JSON — survives server restarts.
    """
    success = add_key(software, dept, key_id)

    if not success:
        return {
            "success": False,
            "message": f"Key '{key_id}' already exists for {software}/{dept}",
        }

    return {
        "success": True,
        "message": f"Key '{key_id}' added for {software}/{dept}",
    }


# ─────────────────────────────────────────────
# HIDE KEY
# ─────────────────────────────────────────────

@router.post("/keys/hide")
def hide_key_endpoint(
    software: str = Query(...),
    dept:     str = Query(...),
    key_id:   str = Query(...),
):
    """
    Hides a Key ID (soft delete).
    Key stays in JSON but won't show in dropdowns.
    """
    success = hide_key(software, dept, key_id)

    return {
        "success": success,
        "message": f"Key '{key_id}' hidden for {software}/{dept}" if success
                   else f"Key '{key_id}' not found",
    }
    @router.post("/keys/add")
def add_key_endpoint(
    session_id: str = Query(...),
    software:   str = Query(...),
    dept:       str = Query(...),
    key_id:     str = Query(...),
):
    """
    Adds a new Key ID for software + dept.
    Validates software and dept exist in Excel data.
    Persists to JSON — survives server restarts.
    """
    session = get_session(session_id)

    # Validate software exists in Excel data
    if software not in session.sw_agg:
        return {
            "success": False,
            "message": f"Software '{software}' not found in Excel data.",
            "available_software": list(session.sw_agg.keys()),
        }

    # Validate dept exists for that software in Excel data
    sw_records  = [r for r in session.records if r["software"] == software]
    valid_depts = {r["dept"].lower() for r in sw_records}

    if dept.lower() not in valid_depts:
        return {
            "success": False,
            "message": f"Dept '{dept}' not found for software '{software}' in Excel data.",
            "available_depts": list(valid_depts),
        }

    # All good — add the key
    success = add_key(software, dept, key_id)

    if not success:
        return {
            "success": False,
            "message": f"Key '{key_id}' already exists for {software}/{dept}",
        }

    return {
        "success": True,
        "message": f"Key '{key_id}' added for {software}/{dept}",
    }
    
@router.get("/valid-combinations")
def valid_combinations(session_id: str = Query(...)):
    """
    Returns all valid software + dept combinations
    from Excel data. Use this to populate dropdowns
    when adding new keys.
    """
    session = get_session(session_id)

    result = {}
    for sw in session.sw_agg.keys():
        sw_records    = [r for r in session.records if r["software"] == sw]
        result[sw]    = list({r["dept"] for r in sw_records})

    return {
        "success": True,
        "data":    result,
    }