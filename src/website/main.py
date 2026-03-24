import os
from typing import Any

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from website.auth import verify_password
from website.database import engine, get_db
from website.models import Base, User

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Secret key for signing session cookies — change this to a long random string in production
app.add_middleware(
    SessionMiddleware,  # type: ignore[arg-type]
    secret_key=os.environ.get("SECRET_KEY", "change-me-in-production"),
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SIDEBAR_ITEMS: list[dict[str, str]] = [
    {"name": "Home / News", "route": "/news", "page": "news"},
    {"name": "Results", "route": "/results", "page": "results"},
    {"name": "Entries", "route": "/entries", "page": "entries"},
    {"name": "History", "route": "/history", "page": "history"},
    {"name": "Documentation", "route": "/documentation", "page": "documentation"},
    {"name": "Fixtures", "route": "/fixtures", "page": "fixtures"},
    {"name": "Events", "route": "/events", "page": "events"},
]


def get_current_user(request: Request) -> dict[str, Any] | None:
    user_id = request.session.get("user_id")
    username = request.session.get("username")
    if user_id and username:
        return {"id": user_id, "username": username}
    return None


def _page_context(request: Request, current_page: str, **extra: Any) -> dict[str, Any]:
    """Build the common template context shared by all page routes."""
    return {
        "request": request,
        "current_user": get_current_user(request),
        "current_page": current_page,
        "sidebar_items": SIDEBAR_ITEMS,
        **extra,
    }


@app.get("/")
def home() -> RedirectResponse:
    return RedirectResponse(url="/news", status_code=302)


@app.get("/news", response_class=HTMLResponse)
def news(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("news.html", _page_context(request, "news"))


@app.get("/results", response_class=HTMLResponse)
def results(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("results.html", _page_context(request, "results"))


@app.get("/entries", response_class=HTMLResponse)
def entries(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("entries.html", _page_context(request, "entries"))


@app.get("/history", response_class=HTMLResponse)
def history(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("history.html", _page_context(request, "history"))


@app.get("/documentation", response_class=HTMLResponse)
def documentation(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "documentation.html", _page_context(request, "documentation")
    )


@app.get("/fixtures", response_class=HTMLResponse)
def fixtures(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "fixtures.html", _page_context(request, "fixtures")
    )


@app.get("/events", response_class=HTMLResponse)
def events(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("events.html", _page_context(request, "events"))


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> Response:
    if get_current_user(request):
        return RedirectResponse(url="/news", status_code=302)
    return templates.TemplateResponse(
        "login.html", _page_context(request, "login", error=None)
    )


@app.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> Response:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, str(user.hashed_password)):
        return templates.TemplateResponse(
            "login.html",
            _page_context(request, "login", error="Invalid username or password."),
            status_code=401,
        )

    request.session["user_id"] = user.id
    request.session["username"] = user.username
    return RedirectResponse(url="/news", status_code=302)


@app.post("/logout")
def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/news", status_code=302)
