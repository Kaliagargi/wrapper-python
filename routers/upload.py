# routers/upload.py

import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.parser import parse_excel
from core.session import create_session, cleanup_expired_sessions
from core.errors import InvalidFileError, SheetNotFoundError

router = APIRouter(prefix="/upload", tags=["Upload"])

# Where uploaded files are saved
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts Excel file, parses it, creates session.
    Returns session_id and summary of what was found.
    """

    # Step 1 — validate file extensionw
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are supported."
        )

    # Step 2 — save file to uploads/ folder
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )

    # Step 3 — parse the Excel file
    try:
        project_layout, records, sw_agg = parse_excel(file_path)
    except (InvalidFileError, SheetNotFoundError) as e:
        # Clean up saved file if parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=422,
            detail=e.message
        )

    # Step 4 — clean up expired sessions before creating new one
    cleanup_expired_sessions()

    # Step 5 — create session with parsed data
    session_id = create_session(
        file_path      = file_path,
        project_layout = project_layout,
        records        = records,
        sw_agg         = sw_agg,
    )

    # Step 6 — build summary response
    locations = list({p["location"] for p in project_layout})
    software_list = list(sw_agg.keys())

    return {
        "success":        True,
        "session_id":     session_id,
        "message":        f"File parsed successfully.",
        "projects_found": len(project_layout),
        "projects":       [p["name"] for p in project_layout],
        "locations":      locations,
        "software_found": len(software_list),
        "software":       software_list,
        "records_found":  len(records),
    }