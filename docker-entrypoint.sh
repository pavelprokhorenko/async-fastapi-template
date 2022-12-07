#!/bin/bash

# Run migrations
alembic upgrade head

# Create initial data in DB
python app/initial_data.py

# Run local server
uvicorn app.fastapi_app:app "${APP_UVICORN_OPTIONS}"
