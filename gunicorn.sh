#!/bin/bash
source s_venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:8000 main:app


