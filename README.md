# Website

A simple website with FastAPI backend, SQLite user storage, and Bootstrap 5 styling.

## Stack

- **Backend:** FastAPI (Python)
- **Database:** SQLite via SQLAlchemy
- **Auth:** Session cookies (Starlette SessionMiddleware + passlib/bcrypt)
- **Templating:** Jinja2 (server-side rendered)
- **Styling:** Bootstrap 5 (CDN)

## Setup

1. **Install dependencies** ([uv](https://docs.astral.sh/uv/) required)
   ```
   uv sync
   ```

2. **Add a user** (run once per user you want to create)
   ```
   uv run python seed_user.py <username> <password>
   ```
   Example:
   ```
   uv run python seed_user.py alice mysecretpassword
   ```

3. **Run the server**
   ```
   uv run uvicorn main:app --reload
   ```

4. **Open your browser** at [http://localhost:8000](http://localhost:8000)

## Project Structure

```
website/
├── main.py           # FastAPI app and all routes
├── database.py       # SQLAlchemy engine and session setup
├── models.py         # User database model
├── auth.py           # Password hashing utilities
├── seed_user.py      # CLI tool to manually add users
├── requirements.txt
├── templates/
│   ├── base.html     # Shared layout with navbar
│   ├── index.html    # Home page
│   └── login.html    # Login form
└── static/
    └── style.css     # Custom CSS overrides

```

## Routes

| Method | Path      | Description                          |
|--------|-----------|--------------------------------------|
| GET    | `/`       | Home page                            |
| GET    | `/login`  | Login form                           |
| POST   | `/login`  | Submit login credentials             |
| POST   | `/logout` | Clear session and redirect to home   |

## Contributing

Contributions are welcome! Please follow the project guidelines.

## License

Add license information here.
