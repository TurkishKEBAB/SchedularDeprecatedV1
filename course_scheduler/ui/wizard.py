"""
Course selection wizard with tri-state selection and teacher preferences.

This module provides the course selection interface where users can
include/exclude courses and set teacher preferences.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import List, Dict, Callable, Optional
import logging

from ..core.models import Course, CourseSelection, SelectionState
from .dialogs import CourseInfoDialog

logger = logging.getLogger(__name__)


class CourseSelectionWizard:
    """Wizard for course selection with tri-state options and teacher preferences."""

    def __init__(self, parent: tk.Tk, courses: List[Course],
                 completion_callback: Callable[[Dict[str, CourseSelection], Dict[str, int]], None]):
        """Initialize the course selection wizard."""
        self.parent = parent
        self.courses = courses
        self.completion_callback = completion_callback

        # Group courses by main_code
        self.course_groups = self._group_courses()

        # Selection state
        self.selections: Dict[str, CourseSelection] = {}
        self.frequency_prefs: Dict[str, int] = {}

        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Course Selection Wizard")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"900x700+{x}+{y}")

        self.setup_ui()
        self._initialize_selections()

    def _group_courses(self) -> Dict[str, List[Course]]:
        """Group courses by main_code."""
        groups = {}
        for course in self.courses:
            if course.main_code not in groups:
                groups[course.main_code] = []
            groups[course.main_code].append(course)
        return groups

    def setup_ui(self):
        """Set up the wizard interface."""
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(main_frame, text="📋 Course Selection",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        # Instructions
        instructions = """
        For each course, choose:
        • Include: Course MUST be in the schedule
        • Exclude: Course will NOT be considered
        • Neutral: Course is optional
        
        Set frequency preferences and teacher preferences as needed.
        """
        ctk.CTkLabel(main_frame, text=instructions.strip(),
                    font=ctk.CTkFont(size=11), justify="left").pack(pady=5)

        # Create selection interface
        self.create_selection_interface(main_frame)

        # Buttons
        self.create_buttons(main_frame)

    def create_selection_interface(self, parent):
        """Create the main selection interface."""
        # Create scrollable frame for course selection
        scroll_frame = ctk.CTkScrollableFrame(parent, height=400)
        scroll_frame.pack(fill="both", expand=True, pady=10)

        # Create selection widgets for each course group
        self.selection_widgets = {}

        for main_code, courses in sorted(self.course_groups.items()):
            self.create_course_group_widget(scroll_frame, main_code, courses)

    def create_course_group_widget(self, parent, main_code: str, courses: List[Course]):
        """Create selection widget for a course group."""
        # Main course frame
        course_frame = ctk.CTkFrame(parent)
        course_frame.pack(fill="x", padx=5, pady=5)

        # Course header
        header_frame = ctk.CTkFrame(course_frame)
        header_frame.pack(fill="x", padx=10, pady=5)

        # Course info
        main_course = courses[0]  # Use first course for main info
        course_name = main_course.name
        total_ects = main_course.ects

        ctk.CTkLabel(header_frame, text=f"{main_code}: {course_name} ({total_ects} ECTS)",
                    font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

        # Info button
        ctk.CTkButton(header_frame, text="ℹ️", width=30,
                     command=lambda: self.show_course_info(main_course)).pack(side="right", padx=5)

        # Selection controls frame
        controls_frame = ctk.CTkFrame(course_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)

        # Tri-state selection
        selection_frame = ctk.CTkFrame(controls_frame)
        selection_frame.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkLabel(selection_frame, text="Selection:", width=80).pack(side="left", padx=5)

        selection_var = tk.StringVar(value="Neutral")
        self.selection_widgets[main_code] = {
            'selection_var': selection_var,
            'courses': courses
        }

        selection_combo = ctk.CTkComboBox(
            selection_frame,
            variable=selection_var,
            values=["Include", "Exclude", "Neutral"],
            command=lambda v, mc=main_code: self.on_selection_changed(mc, v),
            width=120
        )
        selection_combo.pack(side="left", padx=5)

        # Frequency control
        freq_frame = ctk.CTkFrame(controls_frame)
        freq_frame.pack(side="left", padx=5)

        ctk.CTkLabel(freq_frame, text="Frequency:", width=80).pack(side="left", padx=5)

        freq_var = tk.IntVar(value=3)  # Default to "Always"
        self.selection_widgets[main_code]['freq_var'] = freq_var

        freq_slider = ctk.CTkSlider(freq_frame, from_=0, to=3, variable=freq_var,
                                   number_of_steps=3, width=120,
                                   command=lambda v, mc=main_code: self.on_frequency_changed(mc, v))
        freq_slider.pack(side="left", padx=5)

        freq_label = ctk.CTkLabel(freq_frame, text="Always", width=60)
        freq_label.pack(side="left", padx=5)
        self.selection_widgets[main_code]['freq_label'] = freq_label

        # Teacher preference (if multiple teachers available)
        teachers = list(set(course.teacher for course in courses))
        if len(teachers) > 1:
            teacher_frame = ctk.CTkFrame(controls_frame)
            teacher_frame.pack(side="right", padx=5)

            ctk.CTkLabel(teacher_frame, text="Teacher:", width=60).pack(side="left", padx=5)

            teacher_var = tk.StringVar(value="Any")
            teacher_combo = ctk.CTkComboBox(
                teacher_frame,
                variable=teacher_var,
                values=["Any"] + sorted(teachers),
                width=150
            )
            teacher_combo.pack(side="left", padx=5)
            self.selection_widgets[main_code]['teacher_var'] = teacher_var

        # Course sections info
        if len(courses) > 1:
            sections_frame = ctk.CTkFrame(course_frame)
            sections_frame.pack(fill="x", padx=10, pady=2)

            sections_text = f"Available sections: {', '.join(course.code for course in courses)}"
            ctk.CTkLabel(sections_frame, text=sections_text,
                        font=ctk.CTkFont(size=9), text_color="gray").pack(anchor="w", padx=5)

    def create_buttons(self, parent):
        """Create action buttons."""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", pady=10)

        # Stats display
        self.stats_label = ctk.CTkLabel(button_frame, text="Ready to select courses",
                                       font=ctk.CTkFont(size=11))
        self.stats_label.pack(side="left", padx=10)

        # Preset buttons
        preset_frame = ctk.CTkFrame(button_frame)
        preset_frame.pack(side="left", padx=20)

        ctk.CTkButton(preset_frame, text="📋 All Optional", command=self.set_all_neutral,
                     width=100).pack(side="left", padx=2)

        ctk.CTkButton(preset_frame, text="✅ All Include", command=self.set_all_include,
                     width=100).pack(side="left", padx=2)

        # Action buttons
        ctk.CTkButton(button_frame, text="Cancel", command=self.close,
                     width=100).pack(side="right", padx=5)

        ctk.CTkButton(button_frame, text="Generate Schedules", command=self.complete_selection,
                     width=150, fg_color="green", hover_color="darkgreen",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="right", padx=5)

    def _initialize_selections(self):
        """Initialize default selections."""
        for main_code in self.course_groups:
            self.selections[main_code] = CourseSelection(
                main_code=main_code,
                state=SelectionState.NEUTRAL,
                frequency=3
            )
            self.frequency_prefs[main_code] = 3

        self.update_stats()

    def on_selection_changed(self, main_code: str, value: str):
        """Handle selection state change."""
        state_map = {
            "Include": SelectionState.INCLUDE,
            "Exclude": SelectionState.EXCLUDE,
            "Neutral": SelectionState.NEUTRAL
        }

        if main_code in self.selections:
            self.selections[main_code].state = state_map[value]

        self.update_stats()

    def on_frequency_changed(self, main_code: str, value: float):
        """Handle frequency preference change."""
        freq_value = int(value)
        freq_labels = ["Never", "Rarely", "Often", "Always"]

        if main_code in self.selection_widgets:
            self.selection_widgets[main_code]['freq_label'].configure(text=freq_labels[freq_value])

        if main_code in self.selections:
            self.selections[main_code].frequency = freq_value

        self.frequency_prefs[main_code] = freq_value
        self.update_stats()

    def update_stats(self):
        """Update selection statistics display."""
        include_count = sum(1 for sel in self.selections.values() if sel.state == SelectionState.INCLUDE)
        exclude_count = sum(1 for sel in self.selections.values() if sel.state == SelectionState.EXCLUDE)
        neutral_count = len(self.selections) - include_count - exclude_count

        stats_text = f"Include: {include_count}, Exclude: {exclude_count}, Optional: {neutral_count}"
        self.stats_label.configure(text=stats_text)

    def set_all_neutral(self):
        """Set all courses to neutral (optional)."""
        for main_code, widgets in self.selection_widgets.items():
            widgets['selection_var'].set("Neutral")
            self.on_selection_changed(main_code, "Neutral")

    def set_all_include(self):
        """Set all courses to include (mandatory)."""
        for main_code, widgets in self.selection_widgets.items():
            widgets['selection_var'].set("Include")
            self.on_selection_changed(main_code, "Include")

    def show_course_info(self, course: Course):
        """Show detailed course information."""
        CourseInfoDialog(self.dialog, course)

    def complete_selection(self):
        """Complete the selection process."""
        # Update teacher preferences
        for main_code, widgets in self.selection_widgets.items():
            if 'teacher_var' in widgets:
                teacher = widgets['teacher_var'].get()
                if teacher != "Any":
                    self.selections[main_code].teacher_preference = teacher

        # Validate selection
        include_count = sum(1 for sel in self.selections.values() if sel.state == SelectionState.INCLUDE)
        if include_count == 0:
            if not messagebox.askyesno("Warning",
                                     "No courses are marked as 'Include'. This means no courses are mandatory. Continue?"):
                return

        # Call completion callback
        try:
            self.completion_callback(self.selections, self.frequency_prefs)
            self.close()
        except Exception as e:
            logger.error(f"Error in completion callback: {e}")
            messagebox.showerror("Error", f"Failed to proceed with selection: {e}")

    def close(self):
        """Close the wizard."""
        self.dialog.grab_release()
        self.dialog.destroy()
