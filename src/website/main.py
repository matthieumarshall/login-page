import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from website.database import engine, get_db
from website.models import Base, User
from website.auth import verify_password

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


def get_current_user(request: Request) -> dict | None:
    user_id = request.session.get("user_id")
    username = request.session.get("username")
    if user_id and username:
        return {"id": user_id, "username": username}
    return None


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    current_user = get_current_user(request)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    # Redirect to home if already logged in
    if get_current_user(request):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": None,
        },
    )


@app.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, str(user.hashed_password)):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password.",
            },
            status_code=401,
        )

    request.session["user_id"] = user.id
    request.session["username"] = user.username
    return RedirectResponse(url="/", status_code=302)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)
