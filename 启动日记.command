#!/bin/bash
cd "$(dirname "$0")"
nohup python3 diary_app.py >/dev/null 2>&1 &

