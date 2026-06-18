# main.py
from fastapi import FastAPI
from core.errors import register_error_handlers
from core.session import cleanup_expired_sessions
from routers import upload, tables

app = FastAPI(title="Licence Manager")

register_error_handlers(app)

app.include_router(upload.router)
app.include_router(tables.router)

@app.on_event("startup")
async def startup():
    cleanup_expired_sessions()

@app.get("/health")
def health():
    return {"success": True, "message": "Server is running"}