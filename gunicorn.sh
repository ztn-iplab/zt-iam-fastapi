#!/bin/bash
source s_venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:8000 main:app
