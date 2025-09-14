"""
Dialog windows for course selection and snapshot management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Callable, Dict, Set
from collections import defaultdict
import logging

from ..core.models import Course, UserPreferences, Frequency, CourseType

logger = logging.getLogger(__name__)


class CourseSelectionDialog:
    """Dialog for selecting mandatory courses with tri-state logic."""

    def __init__(self, parent: tk.Widget, courses: List[Course], callback: Callable[[UserPreferences], None]):
        self.parent = parent
        self.courses = courses
        self.callback = callback

        # Build course groups for validation
        self.course_groups = self._build_course_groups()

        # State tracking
        self.state_vars: Dict[str, tk.IntVar] = {}
        self.teacher_vars: Dict[str, tk.StringVar] = {}
        self.frequency_vars: Dict[str, tk.IntVar] = {}

        self.setup_dialog()

    def _build_course_groups(self) -> Dict[str, List[Course]]:
        """Build course groups from course list."""
        groups = defaultdict(list)
        for course in self.courses:
            groups[course.main_code].append(course)
        return dict(groups)

    def setup_dialog(self):
        """Setup the course selection dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Mandatory Courses")
        self.dialog.geometry("800x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Instructions
        instructions = ttk.Label(main_frame,
                                text="Select lecture courses to include (click to toggle: Neutral → Include → Exclude):",
                                font=("Arial", 10))
        instructions.pack(anchor="w", pady=(0, 10))

        # Combination counter
        self.combo_var = tk.StringVar(value="Total possible combinations: 0")
        combo_label = ttk.Label(main_frame, textvariable=self.combo_var)
        combo_label.pack(anchor="w", pady=(0, 10))

        # Scrollable course list
        self.setup_course_list(main_frame)

        # Controls
        self.setup_controls(main_frame)

        # Populate courses
        self.populate_courses()

        # Update initial combination count
        self.update_combination_count()

    def setup_course_list(self, parent):
        """Setup scrollable course selection list."""
        # Container frame
        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True, pady=(0, 10))

        # Canvas for scrolling
        canvas = tk.Canvas(container)
        canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Frame inside canvas
        self.selection_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.selection_frame, anchor="nw")

        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def setup_controls(self, parent):
        """Setup control buttons and options."""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill="x", pady=(10, 0))

        # Clear button
        ttk.Button(control_frame, text="Clear Selections",
                  command=self.clear_selections).pack(side="left", padx=(0, 10))

        # Extra courses option
        self.extra_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Include extra courses",
                       variable=self.extra_var).pack(side="left", padx=(0, 20))

        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side="right")

        ttk.Button(button_frame, text="Cancel",
                  command=self.dialog.destroy).pack(side="left", padx=5)
        ttk.Button(button_frame, text="OK",
                  command=self.on_ok, style="Accent.TButton").pack(side="left", padx=5)

    def populate_courses(self):
        """Populate the course selection list."""
        # Get unique lecture courses
        lecture_courses = {}
        teacher_options = defaultdict(set)

        for course in self.courses:
            if course.course_type == CourseType.LECTURE:
                course_info = f"{course.code} {course.name} ({course.ects} ECTS)"
                lecture_courses[course.main_code] = course_info
                teacher_options[course.main_code].add(course.teacher)

        # Convert teacher options to sorted lists
        for code in teacher_options:
            teacher_options[code] = sorted(list(teacher_options[code]))

        # Create course selection widgets
        for main_code, course_info in sorted(lecture_courses.items()):
            self.create_course_widget(main_code, course_info, teacher_options[main_code])

    def create_course_widget(self, main_code: str, course_info: str, teachers: List[str]):
        """Create widget for a single course selection."""
        frame = ttk.Frame(self.selection_frame)
        frame.pack(fill="x", anchor="w", pady=2)

        # State variable (0=Neutral, 1=Include, 2=Exclude)
        state_var = tk.IntVar(value=0)
        self.state_vars[main_code] = state_var

        # Selection button
        btn = tk.Button(frame, text=course_info, width=60, anchor="w",
                       command=lambda: self.cycle_state(main_code, frame))
        btn.pack(side="left", padx=(0, 10))
        frame.button = btn

        # Teacher selection
        ttk.Label(frame, text="Teacher:").pack(side="left", padx=(0, 5))
        teacher_var = tk.StringVar(value=teachers[0] if teachers else "Default")
        self.teacher_vars[main_code] = teacher_var

        teacher_combo = ttk.Combobox(frame, textvariable=teacher_var,
                                   values=teachers, state="readonly", width=15)
        teacher_combo.pack(side="left", padx=(0, 10))

        # Frequency selection
        freq_frame = ttk.Frame(frame)
        freq_frame.pack(side="left", padx=(10, 0))

        ttk.Label(freq_frame, text="Frequency:").pack(side="left", padx=(0, 5))

        freq_var = tk.IntVar(value=2)  # Default to "Often"
        self.frequency_vars[main_code] = freq_var

        for val, text in [(0, "Never"), (1, "Rarely"), (2, "Often"), (3, "Always")]:
            rb = ttk.Radiobutton(freq_frame, text=text, variable=freq_var, value=val)
            rb.pack(side="left", padx=2)

    def cycle_state(self, main_code: str, frame: ttk.Frame):
        """Cycle through selection states for a course."""
        current = self.state_vars[main_code].get()
        new_state = (current + 1) % 3
        self.state_vars[main_code].set(new_state)

        # Update button appearance
        if new_state == 0:  # Neutral
            frame.button.config(bg="SystemButtonFace", relief="raised")
        elif new_state == 1:  # Include
            frame.button.config(bg="lightgreen", relief="sunken")
        elif new_state == 2:  # Exclude
            frame.button.config(bg="lightcoral", relief="sunken")

        self.update_combination_count()

    def update_combination_count(self):
        """Update the combination counter display."""
        combinations = 1

        for main_code, state_var in self.state_vars.items():
            state = state_var.get()
            if state == 1:  # Include
                group_size = len(self.course_groups.get(main_code, []))
                combinations *= max(1, group_size)

        self.combo_var.set(f"Total possible combinations: {combinations:,}")

    def clear_selections(self):
        """Clear all course selections."""
        for main_code in self.state_vars:
            self.state_vars[main_code].set(0)
            # Find and reset button appearance
            for child in self.selection_frame.winfo_children():
                if hasattr(child, 'button'):
                    child.button.config(bg="SystemButtonFace", relief="raised")

        self.update_combination_count()

    def on_ok(self):
        """Handle OK button click."""
        try:
            # Collect selections
            mandatory_courses = set()
            frequency_prefs = {}
            teacher_prefs = {}

            for main_code, state_var in self.state_vars.items():
                state = state_var.get()
                if state == 1:  # Include
                    mandatory_courses.add(main_code)
                elif state == 2:  # Exclude
                    frequency_prefs[main_code] = Frequency.NEVER

                # Collect frequency preferences for all courses
                freq_value = self.frequency_vars[main_code].get()
                frequency_prefs[main_code] = Frequency(freq_value)

                # Collect teacher preferences
                teacher_prefs[main_code] = self.teacher_vars[main_code].get()

            # Validate credit limit
            total_credits = 0
            for main_code in mandatory_courses:
                group = self.course_groups.get(main_code, [])
                lecture = next((c for c in group if c.course_type == CourseType.LECTURE), None)
                if lecture:
                    total_credits += lecture.ects

            if total_credits > 31:  # Default max ECTS
                messagebox.showerror("Credit Error",
                                   f"Total selected credits ({total_credits}) exceed the maximum allowed (31).\n"
                                   "Please reselect courses.")
                return

            # Create preferences object
            preferences = UserPreferences(
                mandatory_courses=mandatory_courses,
                frequency_prefs=frequency_prefs,
                teacher_prefs=teacher_prefs,
                include_extra=self.extra_var.get()
            )

            # Close dialog and call callback
            self.dialog.destroy()
            self.callback(preferences)

            logger.info(f"Course selection completed: {len(mandatory_courses)} mandatory courses")

        except Exception as e:
            logger.error(f"Error in course selection: {e}")
            messagebox.showerror("Selection Error", f"Failed to process selection: {e}")


class SnapshotLoadDialog:
    """Dialog for loading saved snapshots."""

    def __init__(self, parent: tk.Widget, snapshots: List, callback: Callable[[int], None]):
        self.parent = parent
        self.snapshots = snapshots
        self.callback = callback

        self.setup_dialog()

    def setup_dialog(self):
        """Setup the snapshot loading dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Load Snapshot")
        self.dialog.geometry("700x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Instructions
        ttk.Label(main_frame, text="Select a snapshot to load:",
                 font=("Arial", 12)).pack(anchor="w", pady=(0, 10))

        # Snapshot list
        self.setup_snapshot_list(main_frame)

        # Buttons
        self.setup_buttons(main_frame)

        # Populate snapshots
        self.populate_snapshots()

    def setup_snapshot_list(self, parent):
        """Setup the snapshot list display."""
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Treeview for snapshots
        columns = ("ID", "Created", "Courses", "Description")
        self.snapshot_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        # Configure columns
        self.snapshot_tree.heading("ID", text="ID")
        self.snapshot_tree.heading("Created", text="Created")
        self.snapshot_tree.heading("Courses", text="Courses")
        self.snapshot_tree.heading("Description", text="Description")

        self.snapshot_tree.column("ID", width=50)
        self.snapshot_tree.column("Created", width=150)
        self.snapshot_tree.column("Courses", width=80)
        self.snapshot_tree.column("Description", width=400)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.snapshot_tree.yview)
        self.snapshot_tree.configure(yscrollcommand=scrollbar.set)

        # Pack
        self.snapshot_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Double-click to load
        self.snapshot_tree.bind("<Double-1>", lambda e: self.load_selected())

    def setup_buttons(self, parent):
        """Setup dialog buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x")

        ttk.Button(button_frame, text="Cancel",
                  command=self.dialog.destroy).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Load Selected",
                  command=self.load_selected, style="Accent.TButton").pack(side="right", padx=5)
        ttk.Button(button_frame, text="Delete Selected",
                  command=self.delete_selected).pack(side="left")

    def populate_snapshots(self):
        """Populate the snapshot list."""
        for snapshot in self.snapshots:
            brief = snapshot.get_brief_description()
            self.snapshot_tree.insert("", tk.END, values=(
                snapshot.id,
                snapshot.created_at,
                snapshot.course_count,
                brief
            ))

    def load_selected(self):
        """Load the selected snapshot."""
        selection = self.snapshot_tree.selection()
        if not selection:
            messagebox.showwarning("Load Snapshot", "Please select a snapshot to load.")
            return

        item = selection[0]
        snapshot_id = int(self.snapshot_tree.set(item, "ID"))

        self.dialog.destroy()
        self.callback(snapshot_id)

    def delete_selected(self):
        """Delete the selected snapshot."""
        selection = self.snapshot_tree.selection()
        if not selection:
            messagebox.showwarning("Delete Snapshot", "Please select a snapshot to delete.")
            return

        item = selection[0]
        snapshot_id = int(self.snapshot_tree.set(item, "ID"))

        response = messagebox.askyesno("Delete Snapshot",
                                     f"Are you sure you want to delete snapshot #{snapshot_id}?")
        if response:
            try:
                # This would need to be implemented in the snapshot manager
                # self.snapshot_manager.delete_snapshot(snapshot_id)
                self.snapshot_tree.delete(item)
                logger.info(f"Deleted snapshot {snapshot_id}")
            except Exception as e:
                logger.error(f"Failed to delete snapshot: {e}")
                messagebox.showerror("Delete Error", f"Failed to delete snapshot: {e}")


class ProgressDialog:
    """Simple progress dialog for long-running operations."""

    def __init__(self, parent: tk.Widget, title: str = "Please Wait", message: str = "Processing..."):
        self.parent = parent

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x100")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Message
        ttk.Label(self.dialog, text=message, font=("Arial", 10)).pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(self.dialog, mode="indeterminate", length=250)
        self.progress.pack(pady=10)
        self.progress.start(10)

        # Update display
        self.dialog.update()

    def close(self):
        """Close the progress dialog."""
        self.progress.stop()
        self.dialog.destroy()

    def update_message(self, message: str):
        """Update the progress message."""
        for widget in self.dialog.winfo_children():
            if isinstance(widget, ttk.Label):
                widget.config(text=message)
                break
        self.dialog.update()
