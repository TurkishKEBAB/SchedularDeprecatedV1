"""
Main window implementation for the course scheduler application.

This module defines the main application window class with its tabbed interface and
overall application control flow.
"""
import customtkinter as ctk
from tkinter import messagebox
import os
import threading
import logging
from typing import List, Dict, Set, Any, Optional

from ..config import (
    DEFAULT_MAX_ECTS, DEFAULT_ALLOW_CONFLICT,
    DEFAULT_MAX_RESULTS, DEFAULT_PRIORITY,
    DEFAULT_REPLACEMENT_TARGET
)
from ..data.models import Course, Schedule, Program, build_course_groups
from ..data.excel_loader import process_excel
from .file_settings import FileSettingsTab
from .course_preview import CoursePreviewTab
from .course_selection import CourseSelectionWindow
from .schedule_report import ScheduleReportTab
from .preferences_panel import AdvancedPreferencesPanel
from ..scheduler.constraints import ConstraintUtils
from ..scheduler.dfs import DFSScheduler
from ..scheduler.annealing import AnnealingOptimizer
from ..reporting.pdf import create_conflict_report, save_all_selection_matrices_to_pdf
from ..reporting.jpeg import save_schedules_as_jpegs
from ..utils.schedule_metrics import SchedulerPrefs, compute_schedule_stats

# Set up logging
logger = logging.getLogger(__name__)

# Configure CustomTkinter appearance
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


def show_splash(parent: ctk.CTk) -> Optional[ctk.CTkToplevel]:
    """Show splash screen during application startup."""
    try:
        splash = ctk.CTkToplevel(parent)
        splash.title("Course Scheduler")
        splash.geometry("400x300")
        splash.resizable(False, False)

        # Center the splash screen
        splash.update_idletasks()
        x = (splash.winfo_screenwidth() // 2) - (400 // 2)
        y = (splash.winfo_screenheight() // 2) - (300 // 2)
        splash.geometry(f"400x300+{x}+{y}")

        # Create splash content
        main_frame = ctk.CTkFrame(splash, corner_radius=0)
        main_frame.pack(fill="both", expand=True)

        title_label = ctk.CTkLabel(
            main_frame,
            text="🎓 Course Scheduler",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(50, 20))

        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="University Course Scheduling Application",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=10)

        loading_label = ctk.CTkLabel(
            main_frame,
            text="Loading...",
            font=ctk.CTkFont(size=12)
        )
        loading_label.pack(pady=20)

        progress = ctk.CTkProgressBar(main_frame, width=300)
        progress.pack(pady=20)
        progress.set(0.8)

        version_label = ctk.CTkLabel(
            main_frame,
            text="Version 1.0.0",
            font=ctk.CTkFont(size=10)
        )
        version_label.pack(side="bottom", pady=10)

        return splash

    except Exception as e:
        logger.error(f"Error creating splash screen: {e}")
        return None


class MainWindow:
    """
    Main application window with tabbed interface for course scheduling.

    This class manages the overall application flow, including tab navigation,
    data loading, scheduling, and report generation.
    """

    def __init__(self, root: ctk.CTk):
        """
        Initialize the main application window.

        Args:
            root: Root CustomTkinter window
        """
        self.root = root
        self.courses: List[Course] = []
        self.schedules: List[Schedule] = []
        self.course_groups: Dict[str, Any] = {}
        self.selected_courses: List[Course] = []
        self.scheduler_prefs = SchedulerPrefs()

        # Initialize program and missing variables
        self.program = Program("Course Schedule")
        self.final_schedules = []

        # Configure window
        self.root.title("🎓 University Course Scheduler")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        # Set window icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # Create modern UI
        self._setup_ui()

        logger.info("Main window initialized")

    def _setup_ui(self):
        """Set up the user interface components."""
        # Create tabview (modern tabs)
        self.tabview = ctk.CTkTabview(self.root, width=1350, height=850)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Add tabs
        self.tabview.add("Step 1: File & Settings")
        self.tabview.add("Step 2: Preview Courses")
        self.tabview.add("Step 3: Select Courses")
        self.tabview.add("Step 4: Schedule Reports")

        # Get tab frames
        self.tab1 = self.tabview.tab("Step 1: File & Settings")
        self.tab2 = self.tabview.tab("Step 2: Preview Courses")
        self.tab3 = self.tabview.tab("Step 3: Select Courses")
        self.tab4 = self.tabview.tab("Step 4: Schedule Reports")

        # Initialize tabs
        self.file_settings_tab = FileSettingsTab(self.tab1, self._load_courses_from_file)
        self.course_preview_tab = CoursePreviewTab(self.tab2, self)
        self.schedule_report_tab = ScheduleReportTab(self.tab4, self)

        # Add placeholder for course selection tab
        self._create_course_selection_placeholder()

        logger.info("UI setup completed")

    def _create_course_selection_placeholder(self):
        """Create placeholder content for the course selection tab."""
        placeholder_frame = ctk.CTkFrame(self.tab3)
        placeholder_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            placeholder_frame,
            text="📚 Course Selection",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(50, 20))

        info_label = ctk.CTkLabel(
            placeholder_frame,
            text="Load courses from the File & Settings tab and preview them\nto proceed with course selection.",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        info_label.pack(pady=20)

        self.selection_button = ctk.CTkButton(
            placeholder_frame,
            text="🎯 Open Course Selection",
            command=self.open_course_selection,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled"
        )
        self.selection_button.pack(pady=20)

    def _load_courses_from_file(self, file_path: str, sheet_name: str):
        """
        Load courses from an Excel file.

        Args:
            file_path: Path to the Excel file
            sheet_name: Name of the sheet to load
        """
        try:
            # Update status
            self.file_settings_tab.update_status(f"Loading courses from {sheet_name}...")

            # Load courses
            self.courses = process_excel(file_path, sheet_name)

            # Update status
            message = f"Successfully loaded {len(self.courses)} courses from {sheet_name}"
            self.file_settings_tab.update_status(message)

            # Update course preview
            self.course_preview_tab.update_courses(self.courses)

            # Enable course selection
            self.selection_button.configure(state="normal")

            # Build course groups
            self.course_groups = build_course_groups(self.courses)

            logger.info(f"Loaded {len(self.courses)} courses from {file_path}")

        except Exception as e:
            error_msg = f"Error loading courses: {str(e)}"
            self.file_settings_tab.update_status(error_msg)
            logger.error(f"Error loading courses: {e}")
            raise

    def open_course_selection(self, filtered_courses: Optional[List[Course]] = None):
        """
        Open the course selection window.

        Args:
            filtered_courses: Optional list of pre-filtered courses
        """
        if not self.courses:
            messagebox.showwarning("No Courses", "Please load courses first.")
            return

        courses_to_use = filtered_courses if filtered_courses else self.courses

        # Open course selection window
        selection_window = CourseSelectionWindow(
            self.root,
            courses_to_use,
            self._on_course_selection_complete
        )

    def _on_course_selection_complete(self, selected_codes: List[str], include_extra: bool, freq_prefs: Dict[str, int]):
        """
        Handle completion of course selection.

        Args:
            selected_codes: List of selected course main codes
            include_extra: Whether to include extra courses
            freq_prefs: Frequency preferences for courses
        """
        try:
            # Generate schedules
            self._generate_schedules(selected_codes, include_extra)

            # Switch to reports tab
            self.tabview.set("Step 4: Schedule Reports")

            logger.info(f"Course selection completed: {len(selected_codes)} courses selected")

        except Exception as e:
            messagebox.showerror("Scheduling Error", f"Error generating schedules: {str(e)}")
            logger.error(f"Error in course selection: {e}")

    def _generate_schedules(self, selected_codes: List[str], include_extra: bool):
        """
        Generate schedules based on selected courses.

        Args:
            selected_codes: List of selected course main codes
            include_extra: Whether to include extra courses
        """
        try:
            # Get settings
            settings = self.file_settings_tab.get_settings()

            # Initialize scheduler
            scheduler = DFSScheduler(
                max_results=settings["max_results"],
                max_ects=settings["max_ects"],
                allow_conflicts=settings["allow_conflicts"]
            )

            # Generate schedules
            mandatory_codes = set(selected_codes)
            self.final_schedules = scheduler.generate_schedules(self.course_groups, mandatory_codes)

            # Update reports tab
            self.schedule_report_tab.update_schedules(self.final_schedules)

            logger.info(f"Generated {len(self.final_schedules)} schedules")

        except Exception as e:
            logger.error(f"Error generating schedules: {e}")
            raise

    def export_schedules(self, format_type: str, output_path: str) -> bool:
        """
        Export schedules in the specified format.

        Args:
            format_type: Type of export ("pdf", "jpeg", "excel")
            output_path: Path for output

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.final_schedules:
                messagebox.showwarning("No Schedules", "No schedules available to export.")
                return False

            if format_type == "pdf":
                return save_all_selection_matrices_to_pdf(self.final_schedules, output_path)
            elif format_type == "jpeg":
                return save_schedules_as_jpegs(self.final_schedules, output_path)
            elif format_type == "conflict_report":
                return create_conflict_report(self.final_schedules, output_path)
            else:
                logger.error(f"Unknown export format: {format_type}")
                return False

        except Exception as e:
            logger.error(f"Error exporting schedules: {e}")
            return False
