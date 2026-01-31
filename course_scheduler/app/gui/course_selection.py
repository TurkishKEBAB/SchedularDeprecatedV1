"""
Course selection window implementation for the course scheduler.

This module provides a dialog window where users can select mandatory courses
and set frequency preferences.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Callable, Set
import logging

from ..data.models import Course, build_course_groups
from ..config import DEFAULT_MAX_ECTS, FREQUENCY_OPTIONS

# Set up logging
logger = logging.getLogger(__name__)


class CourseSelectionWindow:
    """
    Dialog window for selecting mandatory courses and setting preferences.

    This window allows users to:
    1. Mark courses as mandatory/excluded
    2. Set frequency preferences for each course
    3. Select teacher preferences
    4. Choose whether to include extra courses
    """

    def __init__(self, master: tk.Tk, courses: List[Course], callback: Callable):
        """
        Initialize the course selection window.

        Args:
            master: Parent window
            courses: List of available courses
            callback: Function to call with selection results
        """
        self.top = tk.Toplevel(master)
        self.top.title("Select Mandatory Courses")
        self.top.geometry("800x600")

        # Store parameters
        self.courses = courses
        self.callback = callback

        # Initialize state
        self.state_vars = {}  # Maps main code to selection state (0=neutral, 1=include, 2=exclude)
        self.fixed_sections = {}
        self.teacher_vars = {}
        self.freq_vars = {}

        # Process course data
        self.course_groups = build_course_groups(courses)
        self.valid_counts = self._calculate_valid_counts()
        self.lecture_courses = self._get_lecture_courses()
        self.teacher_options = self._get_teacher_options()

        # Create UI components
        self._create_header()
        self._create_course_list()
        self._create_footer()

        # Position window in center of screen
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f"{width}x{height}+{x}+{y}")

        # Make dialog modal
        self.top.transient(master)
        self.top.grab_set()

        logger.info("Course selection window initialized")

    def _calculate_valid_counts(self) -> Dict[str, int]:
        """
        Calculate the number of valid selections for each course group.

        Returns:
            Dictionary mapping main codes to counts
        """
        valid_counts = {}
        for code, group in self.course_groups.items():
            if any(c.has_lecture for c in group.courses):
                valid_counts[code] = len(group.courses)
            else:
                valid_counts[code] = 0
        return valid_counts

    def _get_lecture_courses(self) -> Dict[str, str]:
        """
        Get a dictionary of lecture courses with formatted display info.

        Returns:
            Dictionary mapping main codes to formatted display strings
        """
        lecture_courses = {}
        for course in self.courses:
            if course.course_type == "lecture":
                lecture_courses[course.main_code] = f"{course.code} {course.name} ({course.ects})"
        return lecture_courses

    def _get_teacher_options(self) -> Dict[str, List[str]]:
        """
        Get a dictionary of available teachers for each course.

        Returns:
            Dictionary mapping main codes to lists of teacher names
        """
        teacher_options = {}
        for course in self.courses:
            if course.course_type == "lecture":
                if course.main_code not in teacher_options:
                    teacher_options[course.main_code] = set()
                teacher_options[course.main_code].add(course.teacher)

        # Convert sets to sorted lists
        for code in teacher_options:
            teacher_options[code] = sorted(list(teacher_options[code]))

        return teacher_options

    def _create_header(self):
        """Create the window header section."""
        header_frame = ttk.Frame(self.top)
        header_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            header_frame,
            text="Select lecture courses to include (click to toggle: Neutral → Include → Exclude):",
            font=("", 10, "bold")
        ).pack(anchor="w")

        self.comb_label = ttk.Label(header_frame, text="Total possible combinations: 0")
        self.comb_label.pack(anchor="w", pady=2)

    def _create_course_list(self):
        """Create the scrollable course list with selection options."""
        # Create a frame to hold the canvas and scrollbar
        container = ttk.Frame(self.top)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        # Create a canvas widget
        canvas = tk.Canvas(container)
        canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the canvas to use the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas for the course list
        self.selection_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.selection_frame, anchor="nw")

        # Add course selection widgets
        for code, info in sorted(self.lecture_courses.items()):
            frame = ttk.Frame(self.selection_frame)
            frame.pack(fill="x", anchor="w", pady=2)

            # Course selection button
            state_var = tk.IntVar(value=0)
            self.state_vars[code] = state_var
            btn = tk.Button(
                frame, text=f"{code} - {info}", width=40,
                command=lambda c=code, b=frame: self._cycle_state(c, b)
            )
            btn.pack(side="left")
            frame.button = btn

            # Teacher selection
            ttk.Label(frame, text="Teacher:").pack(side="left", padx=5)
            teacher_var = tk.StringVar()
            self.teacher_vars[code] = teacher_var
            opts = self.teacher_options.get(code, ["Default"])
            cb = ttk.Combobox(frame, textvariable=teacher_var, values=opts, state="readonly", width=10)
            cb.set(opts[0])
            cb.pack(side="left", padx=5)

            # Frequency selection
            freq_frame = ttk.Frame(frame)
            freq_frame.pack(side="left", padx=5)
            ttk.Label(freq_frame, text="Frequency:").pack(side="left")

            freq_var = tk.IntVar(value=2)  # Default to "Often"
            self.freq_vars[code] = freq_var

            for val, text in sorted(FREQUENCY_OPTIONS.items()):
                ttk.Radiobutton(
                    freq_frame, text=text, variable=freq_var, value=val
                ).pack(side="left")

            # Fix section button
            fix_btn = ttk.Button(
                frame, text="Fix Section",
                command=lambda c=code: self._fix_section(c)
            )
            fix_btn.pack(side="left", padx=5)

    def _create_footer(self):
        """Create the window footer with action buttons."""
        footer_frame = ttk.Frame(self.top)
        footer_frame.pack(fill="x", padx=10, pady=10)

        # Clear selections button
        clear_btn = ttk.Button(footer_frame, text="Clear Selections", command=self._clear_selections)
        clear_btn.pack(side="left", pady=5)

        # Include extra courses option
        self.extra_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            footer_frame, text="Include extra courses", variable=self.extra_var
        ).pack(side="left", padx=20, pady=5)

        # OK button
        self.ok_button = ttk.Button(footer_frame, text="OK", command=self._on_ok)
        self.ok_button.pack(side="right", pady=5)

    def _cycle_state(self, code: str, frame: ttk.Frame):
        """
        Cycle through course selection states.

        Args:
            code: Course main code
            frame: Frame containing the button
        """
        current = self.state_vars[code].get()
        new_state = (current + 1) % 3
        self.state_vars[code].set(new_state)

        # Update button appearance
        if new_state == 0:  # Neutral
            frame.button.config(bg="SystemButtonFace")
        elif new_state == 1:  # Include
            frame.button.config(bg="lightgreen")
        elif new_state == 2:  # Exclude
            frame.button.config(bg="tomato")

        # Update combination count
        self._update_combination_count()

    def _update_combination_count(self):
        """Update the display of possible combinations."""
        comb = 1
        for code, state_var in self.state_vars.items():
            state = state_var.get()
            if state == 1:  # Include
                comb *= self.valid_counts.get(code, 1)

        self.comb_label.config(text=f"Total possible combinations: {comb}")

    def _fix_section(self, code: str):
        """
        Open dialog to fix specific section for a course.

        Args:
            code: Course main code
        """
        # This is a placeholder for the section fixing functionality
        # In a full implementation, this would open a dialog to select specific sections
        messagebox.showinfo("Fix Section", f"Section fixing for {code} not implemented yet.")

    def _clear_selections(self):
        """Clear all course selections."""
        for code, state_var in self.state_vars.items():
            state_var.set(0)
            for frame in self.selection_frame.winfo_children():
                if hasattr(frame, 'button') and frame.button.cget('text').startswith(f"{code} -"):
                    frame.button.config(bg="SystemButtonFace")

        self._update_combination_count()

    def _on_ok(self):
        """Process selections and call the callback function."""
        selected = []
        freq_prefs = {}

        # Process selection states
        for code, state_var in self.state_vars.items():
            state = state_var.get()
            if state == 1:  # Include
                selected.append(code)
            elif state == 2:  # Exclude
                freq_prefs[code] = 0  # Never

        # Process frequency settings for included courses
        for code in selected:
            freq = self.freq_vars[code].get()
            freq_prefs[code] = freq

        # Calculate total credits
        total_credits = 0
        for code in selected:
            group = self.course_groups.get(code)
            if group:
                lecture_courses = [c for c in group.courses if c.course_type == "lecture"]
                if lecture_courses:
                    total_credits += lecture_courses[0].ects

        # Check if total credits exceed maximum
        if total_credits > DEFAULT_MAX_ECTS:
            messagebox.showerror(
                "Credit Error",
                f"Total selected credits ({total_credits}) exceed the maximum allowed ({DEFAULT_MAX_ECTS}).\n"
                f"Please reselect courses."
            )
            return

        logger.info(f"Course selection: {len(selected)} courses selected")

        # Close window and call callback
        self.top.destroy()
        self.callback(selected, self.extra_var.get(), freq_prefs)
