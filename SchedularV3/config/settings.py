"""
Configuration settings and constants for SchedularV3.

This module defines default values and global configuration options used throughout
the application. Migrated and enhanced from SchedularV2.

Environment Variables:
    SECRET_KEY: JWT secret key (required when JWT auth is enabled)
    JWT_EXPIRATION_MINUTES: JWT token expiration time (default: 30)
    JWT_ALGORITHM: JWT signing algorithm (default: HS256)
    ENVIRONMENT: Application environment (default: development)
    DEBUG: Enable debug mode (default: False)
    LOG_LEVEL: Logging level (default: INFO)
"""
import os
import sys
from pathlib import Path
from typing import Optional
import warnings

# Application metadata
APP_NAME = "SchedularV3"
APP_VERSION = "3.0.0"
APP_AUTHOR = "Course Scheduler Team"

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
RESOURCES_DIR = BASE_DIR / "resources"
LOGS_DIR = BASE_DIR / "logs"
DOCS_DIR = BASE_DIR / "docs"

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

# Course types and their display colors (PyQt6 compatible)
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

# File paths and patterns
DEFAULT_PDF_FILENAME = "final_selection_matrices.pdf"
DEFAULT_JPEG_FILENAME_PATTERN = "program{}.jpg"
DEFAULT_REPORT_FILENAME = "conflict_report.txt"

# SQLite database settings
DATABASE_PATH = BASE_DIR / "course_scheduler.db"
DATABASE_ENABLED = True  # V3 uses SQLite by default

# Chart settings (for matplotlib integration)
CHART_UPDATE_INTERVAL_MS = 2000
CHART_DIMENSIONS = (6, 4)
BAR_WIDTH = 0.35

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_LEVEL = 'INFO'
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_FILE_BACKUP_COUNT = 5

# GUI settings
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 768
THEME = "Light"  # Light or Dark

# Algorithm timeout settings (in seconds)
ALGORITHM_TIMEOUT = {
    'dfs': 30,
    'a_star': 60,
    'genetic': 120,
    'simulated_annealing': 120,
}

# =============================================================================
# Environment Variable Loading
# =============================================================================

def _load_env_file() -> None:
    """
    Load environment variables from .env file if it exists.
    
    This function attempts to load a .env file from the BASE_DIR.
    If python-dotenv is not installed, it will skip loading silently.
    """
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        try:
            # Try to use python-dotenv if available
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            # python-dotenv not installed, parse manually (basic support)
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value


def _get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def _get_env_int(key: str, default: int) -> int:
    """Get integer environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


# Load .env file if it exists
_load_env_file()

# =============================================================================
# Security & Authentication Settings
# =============================================================================

# Environment type
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Debug mode
DEBUG = _get_env_bool("DEBUG", False)

# JWT Secret Key (CRITICAL: Required for JWT authentication)
# This should NEVER be hardcoded. Always use environment variables.
SECRET_KEY: Optional[str] = os.getenv("SECRET_KEY")

# JWT Configuration
JWT_EXPIRATION_MINUTES = _get_env_int("JWT_EXPIRATION_MINUTES", 30)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def validate_jwt_config() -> None:
    """
    Validate JWT configuration before using authentication features.
    
    This function should be called at application startup if JWT 
    authentication is enabled. It ensures that SECRET_KEY is set 
    and meets minimum security requirements.
    
    Raises:
        ValueError: If SECRET_KEY is not set or doesn't meet requirements
        
    Example:
        >>> from config.settings import validate_jwt_config
        >>> validate_jwt_config()  # Raises error if SECRET_KEY not set
    """
    if not SECRET_KEY:
        raise ValueError(
            "CRITICAL SECURITY ERROR: SECRET_KEY environment variable is not set!\n"
            "\n"
            "JWT authentication requires a SECRET_KEY for signing tokens.\n"
            "\n"
            "To fix this:\n"
            "1. Copy .env.example to .env in the SchedularV3 directory\n"
            "2. Generate a secure secret key:\n"
            "   python -c \"import secrets; print(secrets.token_urlsafe(32))\"\n"
            "3. Set SECRET_KEY in .env file with the generated key\n"
            "4. NEVER commit .env file to version control\n"
            "\n"
            "For more information, see .env.example and README.md\n"
        )
    
    # Validate minimum length
    if len(SECRET_KEY) < 32:
        raise ValueError(
            f"SECURITY WARNING: SECRET_KEY is too short ({len(SECRET_KEY)} chars)!\n"
            "\n"
            "For security, SECRET_KEY should be at least 32 characters.\n"
            "Generate a new key using:\n"
            "  python -c \"import secrets; print(secrets.token_urlsafe(32))\"\n"
        )
    
    # Warn about insecure defaults
    insecure_values = [
        "your-super-secret-jwt-key-change-this-in-production-min-32-chars",
        "change-this-secret-key",
        "secret",
        "password",
        "test",
    ]
    if SECRET_KEY.lower() in insecure_values:
        raise ValueError(
            "SECURITY ERROR: SECRET_KEY contains an insecure default value!\n"
            "\n"
            "Never use default/example values in production.\n"
            "Generate a secure random key:\n"
            "  python -c \"import secrets; print(secrets.token_urlsafe(32))\"\n"
        )
    
    # Production environment checks
    if ENVIRONMENT == "production":
        if DEBUG:
            warnings.warn(
                "WARNING: DEBUG is enabled in production environment! "
                "This is a security risk.",
                category=UserWarning
            )


def get_secret_key() -> str:
    """
    Get the JWT secret key, validating configuration first.
    
    This is the recommended way to access SECRET_KEY as it ensures
    validation has been performed.
    
    Returns:
        str: The validated SECRET_KEY
        
    Raises:
        ValueError: If SECRET_KEY is not properly configured
        
    Example:
        >>> from config.settings import get_secret_key
        >>> secret = get_secret_key()  # Will raise error if not configured
    """
    validate_jwt_config()
    return SECRET_KEY  # type: ignore


# Override LOG_LEVEL from environment if specified
if "LOG_LEVEL" in os.environ:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

