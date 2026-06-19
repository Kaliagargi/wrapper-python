from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from core.errors import register_error_handlers
from core.session import cleanup_expired_sessions
from routers import upload, tables, download, keystore

app = FastAPI(title="Licence Manager")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

register_error_handlers(app)

app.include_router(upload.router)
app.include_router(tables.router)
app.include_router(download.router)
app.include_router(keystore.router)


@app.on_event("startup")
async def startup():
    cleanup_expired_sessions()


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="upload.html"
    )


@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )


@app.get("/table1")
def table1_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="table1.html"
    )


@app.get("/table2")
def table2_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="table2.html"
    )


@app.get("/table3")
def table3_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="table3.html"
    )


@app.get("/table4")
def table4_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="table4.html"
    )


@app.get("/keystore-page")
def keystore_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="keystore.html"
    )


@app.get("/download-page")
def download_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="download.html"
    )


@app.get("/health")
def health():
    return {"success": True, "message": "Server is running"}