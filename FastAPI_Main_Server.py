from __future__ import annotations

import base64
import binascii
import secrets
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from api.cleaning_api import router as cleaning_router
from api.insights_api import router as insights_router
from api.ml_api import router as ml_router
from api.summary_api import router as summary_router
from api.upload_api import router as upload_router
from api.visualization_api import router as visualization_router
from config import APP_ENV, APP_PASSWORD, APP_USERNAME, BASE_DIR, CHART_DIR

app = FastAPI(
    title="AI Data Scientist Agent API",
    description="Upload, clean, explore, visualize and model tabular datasets.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url=None,
)

for router in (upload_router, summary_router, cleaning_router, visualization_router, insights_router, ml_router):
    app.include_router(router)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/charts", StaticFiles(directory=CHART_DIR), name="charts")


@app.middleware("http")
async def security_middleware(request, call_next):
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "same-origin",
        "Cache-Control": "no-store",
        "Content-Security-Policy": (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
            "object-src 'none'; frame-ancestors 'none'; form-action 'self'; base-uri 'none'"
        ),
    }
    if APP_USERNAME and APP_PASSWORD and request.url.path != "/health":
        authorization = request.headers.get("Authorization", "")
        authenticated = False
        if authorization.startswith("Basic "):
            try:
                decoded = base64.b64decode(authorization[6:], validate=True).decode("utf-8")
                username, password = decoded.split(":", 1)
                authenticated = secrets.compare_digest(username, APP_USERNAME) and secrets.compare_digest(
                    password, APP_PASSWORD
                )
            except (binascii.Error, UnicodeDecodeError, ValueError):
                authenticated = False
        if not authenticated:
            return Response(
                status_code=401,
                headers={**headers, "WWW-Authenticate": 'Basic realm="Data Scientist Agent"'},
            )
    if APP_ENV == "production" and request.method not in {"GET", "HEAD", "OPTIONS"}:
        origin = request.headers.get("origin", "")
        site = request.headers.get("sec-fetch-site", "")
        host = request.headers.get("host", "")
        if (origin and urlparse(origin).netloc != host) or site == "cross-site" or (not origin and not site):
            return Response(status_code=403, headers=headers)
    response = await call_next(request)
    response.headers.update(headers)
    return response


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy", "version": "2.0.0"}
