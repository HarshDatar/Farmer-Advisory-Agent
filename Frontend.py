"""
Frontend.py — Alternate entry point for Kisan Saathi.

Run with:
    streamlit run Frontend.py

This simply re-exports everything from app.py so that the
application can be launched using either filename.
"""
from app import *  # noqa: F401,F403
