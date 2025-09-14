#!/usr/bin/env python3
"""
Course Scheduler Application
Entry point for the refactored modular course scheduler.
"""

import sys
import os
import logging
import tkinter as tk
from tkinter import messagebox

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('course_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are available."""
    required_packages = [
        'pandas', 'matplotlib', 'numpy', 'openpyxl'
    ]

    # Check for PIL (Pillow)
    try:
        from PIL import Image
        logger.info("PIL/Pillow found successfully")
    except ImportError:
        required_packages.append('Pillow')

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        error_msg = f"Missing required packages: {', '.join(missing)}\n"
        error_msg += "Please install them using: pip install " + " ".join(missing)
        logger.error(error_msg)
        messagebox.showerror("Missing Dependencies", error_msg)
        return False

    return True


def main():
    """Main entry point for the course scheduler application."""
    try:
        # Check dependencies first
        if not check_dependencies():
            return 1

        # Import the main application
        from course_scheduler.ui.app import SchedulerApplication

        # Create the main window
        root = tk.Tk()

        # Configure style
        try:
            from tkinter import ttk
            style = ttk.Style()
            # Try to use a modern theme
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif 'alt' in available_themes:
                style.theme_use('alt')
            logger.info(f"Using theme: {style.theme_use()}")
        except Exception as e:
            logger.warning(f"Could not set theme: {e}")

        # Create and run the application
        app = SchedulerApplication(root)

        logger.info("Course Scheduler application started successfully")

        # Start the main loop
        root.mainloop()

        logger.info("Course Scheduler application closed")
        return 0

    except ImportError as e:
        error_msg = f"Import error: {e}\nPlease ensure all modules are properly installed."
        logger.error(error_msg)
        if 'tk' in globals():
            messagebox.showerror("Import Error", error_msg)
        else:
            print(error_msg)
        return 1

    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg, exc_info=True)
        if 'tk' in globals():
            messagebox.showerror("Application Error", error_msg)
        else:
            print(error_msg)
        return 1


if __name__ == "__main__":
    sys.exit(main())
