#!/bin/bash
source s_venv/bin/activate
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 fastapi_app:app

