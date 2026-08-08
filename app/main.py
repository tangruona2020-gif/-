from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select

from app.api.routes import router
from app.database import SessionLocal, create_schema
from app.logging_config import configure_logging
from app.models import Event, IpTitle, ScanRun, Source

WEB = Path(__file__).parent / "web"
templates = Jinja2Templates(directory=WEB / "templates")
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_schema()
    yield


app = FastAPI(title="Goods Popup Monitor", lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory=WEB / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    with SessionLocal() as db:
        stats = {
            "sources": db.scalar(select(func.count()).select_from(Source).where(Source.enabled)),
            "ips": db.scalar(select(func.count()).select_from(IpTitle).where(IpTitle.enabled)),
            "events": db.scalar(select(func.count()).select_from(Event)),
        }
        scans = db.scalars(select(ScanRun).order_by(ScanRun.started_at.desc()).limit(10)).all()
    return templates.TemplateResponse(request, "dashboard.html", {"stats": stats, "scans": scans})
