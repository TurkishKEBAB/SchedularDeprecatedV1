"""
Course Scheduler Application
A comprehensive course scheduling system with filter-first workflow and SQLite persistence.
"""

__version__ = "2.0.0"
__author__ = "Course Scheduler Team"
__description__ = "Advanced course scheduler with Turkish/English Excel support and filter-first workflow"

# Main application entry point
from .ui import SchedulerApplication

__all__ = ['SchedulerApplication']
