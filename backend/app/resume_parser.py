"""Compatibility wrapper that re-exports from `backend.utils.resume_parser`.

This keeps existing imports (`from app.resume_parser import ...`) working while the
implementation lives in `backend/utils/resume_parser.py`.
"""
from backend.utils.resume_parser import extract_text_from_pdf, extract_text_from_docx

__all__ = ["extract_text_from_pdf", "extract_text_from_docx"]
