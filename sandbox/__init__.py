"""Pískoviště: minimální Linux v kontejneru pro nácvik práce s terminálem."""

from .routes import bp as sandbox_bp
from .python_lab import bp as python_lab_bp

__all__ = ["sandbox_bp", "python_lab_bp"]
