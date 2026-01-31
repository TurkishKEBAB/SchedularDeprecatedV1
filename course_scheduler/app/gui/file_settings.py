"""
File settings tab implementation for the course scheduler.

This module provides the first tab of the application, where users can
load course data from Excel files and configure basic settings.
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Optional, Callable
import logging
import os

# Set up logging
logger = logging.getLogger(__name__)


class FileSettingsTab:
    """
    First tab of the scheduler application for file loading and basic settings.

    This tab allows users to:
    1. Select and load Excel files containing course data
    2. Configure basic scheduler settings
    3. Validate loaded data
    """

    def __init__(self, parent: ctk.CTkFrame, load_callback: Callable[[str, str], None]):
        """
        Initialize the file settings tab.

        Args:
            parent: Parent frame (tab container)
            load_callback: Function to call when loading Excel file
        """
        self.parent = parent
        self.load_callback = load_callback
        self.excel_file_path = ""
        self.sheet_name = "Sheet1"

        # Create UI components
        self._create_file_section()
        self._create_settings_section()
        self._create_status_section()

    def _create_file_section(self):
        """Create the file selection section."""
        # File selection frame
        file_frame = ctk.CTkFrame(self.parent)
        file_frame.pack(fill="x", padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            file_frame,
            text="📁 Course Data File",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # File path frame
        path_frame = ctk.CTkFrame(file_frame)
        path_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            path_frame,
            text="Excel File:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(10, 5))

        self.file_path_var = ctk.StringVar(value="No file selected")
        self.file_path_label = ctk.CTkLabel(
            path_frame,
            textvariable=self.file_path_var,
            font=ctk.CTkFont(size=11)
        )
        self.file_path_label.pack(side="left", padx=10, fill="x", expand=True)

        browse_btn = ctk.CTkButton(
            path_frame,
            text="📂 Browse",
            command=self._browse_file,
            width=100
        )
        browse_btn.pack(side="right", padx=10)

        # Sheet selection frame
        sheet_frame = ctk.CTkFrame(file_frame)
        sheet_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            sheet_frame,
            text="Sheet Name:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(10, 5))

        self.sheet_var = ctk.StringVar(value="Sheet1")
        self.sheet_entry = ctk.CTkEntry(
            sheet_frame,
            textvariable=self.sheet_var,
            width=200
        )
        self.sheet_entry.pack(side="left", padx=10)

        # Load button
        self.load_btn = ctk.CTkButton(
            file_frame,
            text="📊 Load Course Data",
            command=self._load_file,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color=("blue", "darkblue"),
            hover_color=("darkblue", "blue")
        )
        self.load_btn.pack(pady=15)

        # Progress section (initially hidden)
        self.progress_frame = ctk.CTkFrame(file_frame)

        ctk.CTkLabel(
            self.progress_frame,
            text="Loading Progress:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(10, 5))

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            width=400,
            height=20
        )
        self.progress_bar.pack(padx=20, pady=5)
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready to load...",
            font=ctk.CTkFont(size=11)
        )
        self.progress_label.pack(pady=(5, 15))

        # Auto-continue feature
        self.auto_continue_frame = ctk.CTkFrame(file_frame)

        self.auto_continue_var = ctk.BooleanVar(value=True)
        self.auto_continue_check = ctk.CTkCheckBox(
            self.auto_continue_frame,
            text="Auto-continue to next step when loading is complete",
            variable=self.auto_continue_var,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.auto_continue_check.pack(pady=15, padx=15)

    def _create_settings_section(self):
        """Create the basic settings section."""
        # Settings frame
        settings_frame = ctk.CTkFrame(self.parent)
        settings_frame.pack(fill="x", padx=20, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            settings_frame,
            text="⚙️ Basic Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # Settings grid
        grid_frame = ctk.CTkFrame(settings_frame)
        grid_frame.pack(fill="x", padx=15, pady=10)

        # Max ECTS
        ctk.CTkLabel(
            grid_frame,
            text="Maximum ECTS Credits:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.max_ects_var = ctk.IntVar(value=31)
        self.max_ects_entry = ctk.CTkEntry(
            grid_frame,
            textvariable=self.max_ects_var,
            width=100
        )
        self.max_ects_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Max results
        ctk.CTkLabel(
            grid_frame,
            text="Maximum Results to Generate:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.max_results_var = ctk.IntVar(value=5)
        self.max_results_entry = ctk.CTkEntry(
            grid_frame,
            textvariable=self.max_results_var,
            width=100
        )
        self.max_results_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Allow conflicts
        self.allow_conflicts_var = ctk.BooleanVar(value=False)
        self.allow_conflicts_check = ctk.CTkCheckBox(
            grid_frame,
            text="Allow schedule conflicts",
            variable=self.allow_conflicts_var,
            font=ctk.CTkFont(size=12)
        )
        self.allow_conflicts_check.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    def _create_status_section(self):
        """Create the status display section."""
        # Status frame
        status_frame = ctk.CTkFrame(self.parent)
        status_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            status_frame,
            text="📊 Data Status",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # Status text
        self.status_text = ctk.CTkTextbox(
            status_frame,
            height=200,
            font=ctk.CTkFont(size=11)
        )
        self.status_text.pack(fill="both", expand=True, padx=15, pady=10)

        # Initial status
        self.update_status("Welcome! Please select an Excel file to begin.")

    def _browse_file(self):
        """Open file browser to select Excel file."""
        file_path = filedialog.askopenfilename(
            title="Select Course Data Excel File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.excel_file_path = file_path
            self.file_path_var.set(os.path.basename(file_path))
            self.update_status(f"Selected file: {file_path}")
            logger.info(f"Selected Excel file: {file_path}")

    def _load_file(self):
        """Load the selected Excel file."""
        if not self.excel_file_path:
            messagebox.showerror("Error", "Please select an Excel file first.")
            return

        sheet_name = self.sheet_var.get().strip()
        if not sheet_name:
            sheet_name = "Sheet1"

        try:
            self.update_status(f"Loading courses from {os.path.basename(self.excel_file_path)}...")
            self.load_callback(self.excel_file_path, sheet_name)

        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            self.update_status(error_msg)
            messagebox.showerror("Loading Error", error_msg)
            logger.error(f"Error loading Excel file: {e}")

    def update_status(self, message: str):
        """
        Update the status display.

        Args:
            message: Status message to display
        """
        self.status_text.insert("end", f"{message}\n")
        self.status_text.see("end")
        self.parent.update_idletasks()

    def get_settings(self) -> dict:
        """
        Get current settings values.

        Returns:
            Dictionary of current settings
        """
        return {
            "max_ects": self.max_ects_var.get(),
            "max_results": self.max_results_var.get(),
            "allow_conflicts": self.allow_conflicts_var.get()
        }

    def show_progress(self, show: bool = True):
        """Show or hide the progress bar."""
        if show:
            self.progress_frame.pack(fill="x", padx=15, pady=10, after=self.load_btn)
            self.auto_continue_frame.pack(fill="x", padx=15, pady=5, after=self.progress_frame)
        else:
            self.progress_frame.pack_forget()
            self.auto_continue_frame.pack_forget()

    def update_progress(self, value: float, message: str = ""):
        """
        Update the progress bar.

        Args:
            value: Progress value between 0 and 1
            message: Progress message to display
        """
        self.progress_bar.set(value)
        if message:
            self.progress_label.configure(text=message)
        self.parent.update_idletasks()

        # Auto-continue when progress is complete
        if value >= 1.0 and self.auto_continue_var.get():
            self.parent.after(1000, self._auto_continue_to_next_step)

    def _auto_continue_to_next_step(self):
        """Automatically continue to the next step when loading is complete."""
        # This will be called by the main window to switch tabs
        if hasattr(self.parent.master, 'switch_to_next_tab'):
            self.parent.master.switch_to_next_tab()

    def reset_progress(self):
        """Reset the progress bar to initial state."""
        self.progress_bar.set(0)
        self.progress_label.configure(text="Ready to load...")
        self.show_progress(False)
