#!/usr/bin/env bash

playwright install chromium
gunicorn api:app --bind 0.0.0.0:$PORT
xvfb-run python api.py
chmod +x start.sh
