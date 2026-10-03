#!/usr/bin/env sh
set -eu
exec uvicorn FastAPI_Main_Server:app --host 0.0.0.0 --port "${PORT:-8010}" --workers 1
