#!/usr/bin/env bash
python3 server/api/app.py &
python3 server/event_worker/app.py &