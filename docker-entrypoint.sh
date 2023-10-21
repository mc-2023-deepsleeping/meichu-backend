#!/bin/bash
cd /opt/app

# Start server
echo "Starting server"
python app.py
exec "$@"