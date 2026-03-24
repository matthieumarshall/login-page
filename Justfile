# Keep command behavior consistent on Windows.
set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# Sync Python and Node dependencies used by this project.
sync:
    uv sync --extra dev --extra test
    npm install
    uv run python -m pre_commit install

# Run pre-commit hooks on all files.
lint:
    uv run python -m pre_commit run --all-files

# Start the development server with auto-reload.
serve:
    uv run uvicorn website.main:app --reload
