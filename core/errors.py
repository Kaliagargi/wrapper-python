# core/errors.py

from fastapi import Request
from fastapi.responses import JSONResponse


# ── Custom Exception Classes ──────────────────────────────

class LicenceManagerError(Exception):
    """Base error for all app errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class FileNotUploadedError(LicenceManagerError):
    """Raised when user calls a table endpoint without uploading first"""
    def __init__(self):
        super().__init__("No file uploaded. Please upload your Excel file first.", 400)


class InvalidFileError(LicenceManagerError):
    """Raised when uploaded file is not a valid Excel or wrong structure"""
    def __init__(self, detail: str = "Invalid file format or structure"):
        super().__init__(detail, 422)


class SheetNotFoundError(LicenceManagerError):
    """Raised when expected sheet name is missing in the Excel file"""
    def __init__(self, sheet_name: str):
        super().__init__(f"Sheet '{sheet_name}' not found in uploaded file.", 404)


class SoftwareNotFoundError(LicenceManagerError):
    """Raised when user requests a software that doesn't exist in data"""
    def __init__(self, software: str):
        super().__init__(f"Software '{software}' not found in the data.", 404)


class SessionNotFoundError(LicenceManagerError):
    """Raised when session ID is invalid or expired"""
    def __init__(self):
        super().__init__("Session expired or invalid. Please re-upload your file.", 401)


# ── Global Exception Handler ──────────────────────────────

def register_error_handlers(app):
    """Call this in main.py to attach handlers to the FastAPI app"""

    @app.exception_handler(LicenceManagerError)
    async def licence_manager_error_handler(request: Request, exc: LicenceManagerError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.message
            }
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "An unexpected error occurred.",
                "detail": str(exc)
            }
        )