#!/usr/bin/env python3
"""
PersonaSay Backend - Main Entry Point
Run with: python main.py or uvicorn main:app
"""

from app.server import app
from app.models import AppSettings

if __name__ == "__main__":
    import uvicorn
    settings = AppSettings()
    uvicorn.run(app, host=settings.host, port=settings.port)

