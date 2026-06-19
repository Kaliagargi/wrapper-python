# routers/upload.py

import os
# routers/upload.py

import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.parser import parse_excel
from core.session import create_session, cleanup_expired_sessions
from core.errors import InvalidFileError, SheetNotFoundError

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    try:
        project_layout, records, sw_agg = parse_excel(file_path)
    except (InvalidFileError, SheetNotFoundError) as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=422, detail=e.message)

    cleanup_expired_sessions()

    session_id = create_session(
        file_path      = file_path,
        project_layout = project_layout,
        records        = records,
        sw_agg         = sw_agg,
    )

    return {
        "success":        True,
        "session_id":     session_id,
        "message":        "File parsed successfully.",
        "projects_found": len(project_layout),
        "projects":       [p["name"] for p in project_layout],
        "locations":      list({p["location"] for p in project_layout}),
        "software_found": len(sw_agg),
        "software":       list(sw_agg.keys()),
        "records_found":  len(records),
    }