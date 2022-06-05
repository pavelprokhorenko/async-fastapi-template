#!/bin/bash

# Set local server config
APP_UVICORN_OPTIONS="${APP_UVICORN_OPTIONS:---host 0.0.0.0 --port=8080}"

# Run migrations
alembic -n postgres upgrade head

# Create initial data in DB
python app/initial_data.py

# Run local server
uvicorn ${APP_UVICORN_OPTIONS} app.fastapi_app:app
