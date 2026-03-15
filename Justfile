# Keep command behavior consistent on Windows.
set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# Sync Python and Node dependencies used by this project.
sync:
    uv sync --extra dev
    npm install
