"""
Course Scheduler - Application Entry Point

This module serves as the entry point for the course scheduler application,
initializing the GUI and setting up logging.
"""
import os
import sys
import logging
import customtkinter as ctk
from datetime import datetime

# Add the parent directory to Python path to enable package imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Setup logging
def setup_logging():
    """Configure the logging system."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"scheduler_{timestamp}.log")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.info("Logging initialized")
    return log_file

# Import application modules after logging is set up
from course_scheduler.app.gui.main_window import MainWindow, show_splash

def main():
    """
    Application entry point.

    Initializes the application, shows the splash screen,
    and creates the main window.
    """
    # Setup logging
    log_file = setup_logging()
    logging.info("Starting Course Scheduler application")

    # Create root window with CustomTkinter
    root = ctk.CTk()

    # Show splash screen
    splash = show_splash(root)

    # Initialize main application
    try:
        app = MainWindow(root)
        logging.info("Main window initialized successfully")

        # Close splash screen
        if splash:
            splash.destroy()

        # Start the application
        root.mainloop()

    except Exception as e:
        logging.error(f"Error starting application: {e}")
        if splash:
            splash.destroy()
        root.destroy()
        raise

if __name__ == "__main__":
    main()
