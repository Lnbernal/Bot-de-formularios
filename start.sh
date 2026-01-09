#!/usr/bin/env bash

playwright install chromium
gunicorn api:app --bind 0.0.0.0:$PORT
chmod +x start.sh
