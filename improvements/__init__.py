"""
Project-specific improvements and extensions for CEO research.

This module contains bank CEO project-specific implementations,
data models, and utilities that extend the core research functionality.
"""

from .bank_ceo_profile import BankCEOProfile
from .data_utils import load_project_dataset

__all__ = [
    'BankCEOProfile',
    'load_project_dataset',
]
