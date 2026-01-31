"""
Configuration settings and constants for the course scheduler application.

This module defines default values and global configuration options used throughout
the application.
"""

# Default scheduler parameters
DEFAULT_MAX_ECTS = 31
DEFAULT_ALLOW_CONFLICT = 1
DEFAULT_MAX_RESULTS = 5
DEFAULT_PRIORITY = "lecture,ps,lab"
DEFAULT_REPLACEMENT_TARGET = "sections"  # or "course"

# Schedule visualization settings
PERIOD_TIMES = {
    1: "08:30-09:20",
    2: "09:30-10:20",
    3: "10:30-11:20",
    4: "11:30-12:20",
    5: "12:30-13:20",
    6: "13:30-14:20",
    7: "14:30-15:20",
    8: "15:30-16:20",
    9: "16:30-17:20",
    10: "17:30-18:20",
    11: "18:30-19:20",
    12: "19:30-20:20"
}

# Schedule grid days
DAYS = ["M", "T", "W", "Th", "F", "Sa", "Su"]
DAY_FULL_NAMES = {
    "M": "Monday",
    "T": "Tuesday",
    "W": "Wednesday",
    "Th": "Thursday",
    "F": "Friday",
    "Sa": "Saturday",
    "Su": "Sunday"
}

# Course types and their display colors
COURSE_COLORS = {
    "lecture": "#FFE5E5",  # Light red
    "ps": "#E5FFE5",       # Light green
    "lab": "#E5E5FF"       # Light blue
}

# Frequency preference options
FREQUENCY_OPTIONS = {
    0: "Never",
    1: "Rarely",
    2: "Often",
    3: "Always"
}

# File paths
DEFAULT_PDF_FILENAME = "final_selection_matrices.pdf"
DEFAULT_JPEG_FILENAME_PATTERN = "program{}.jpg"
DEFAULT_REPORT_FILENAME = "conflict_report.txt"

# SQLite database settings
DATABASE_PATH = "course_scheduler.db"
DATABASE_ENABLED = False  # Set to True to enable SQLite integration

# Chart settings
CHART_UPDATE_INTERVAL_MS = 2000
CHART_DIMENSIONS = (6, 4)
BAR_WIDTH = 0.35
