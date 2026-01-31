"""
Dialog windows for course selection and snapshot management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Callable, Dict, Set
from collections import defaultdict
import logging

from ..core.models import Course, UserPreferences, Frequency, CourseType

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CourseSelectionDialog:
    """Dialog for selecting courses with automatic section assignment."""

    def __init__(self, parent: tk.Widget, courses: List[Course], callback: Callable[[UserPreferences], None]):
        logger.info("="*80)
        logger.info("🚀 CourseSelectionDialog initialized")
        logger.info(f"📚 Total courses received: {len(courses)}")

        self.parent = parent
        self.courses = courses
        self.callback = callback

        # Build course groups for validation
        self.course_groups = self._build_course_groups()
        logger.info(f"📦 Grouped into {len(self.course_groups)} unique course groups")

        # Log course groups
        for main_code, group_courses in self.course_groups.items():
            logger.debug(f"  - {main_code}: {len(group_courses)} sections")

        # State tracking - simplified to only track course selection
        self.state_vars: Dict[str, tk.IntVar] = {}
        self.frequency_vars: Dict[str, tk.IntVar] = {}

        self.setup_dialog()

    def _build_course_groups(self) -> Dict[str, List[Course]]:
        """Build course groups from course list."""
        logger.debug("🔍 Building course groups by main_code...")
        groups = defaultdict(list)
        for course in self.courses:
            groups[course.main_code].append(course)

        result = dict(groups)
        logger.debug(f"✅ Built {len(result)} course groups")
        return result

    def setup_dialog(self):
        """Setup the course selection dialog."""
        logger.info("🎨 Setting up dialog UI...")

        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Courses - Automatic Section Assignment")
        self.dialog.geometry("1000x700")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Instructions
        instructions = ttk.Label(main_frame,
                                text="Select courses to include. The system will automatically choose the best sections, labs, and PS sessions.\n"
                                     "Click to toggle: Neutral → Include → Exclude",
                                font=("Arial", 10), justify="left")
        instructions.pack(anchor="w", pady=(0, 10))

        # Total credits counter
        self.credits_var = tk.StringVar(value="Total selected credits: 0")
        credits_label = ttk.Label(main_frame, textvariable=self.credits_var, font=("Arial", 11, "bold"))
        credits_label.pack(anchor="w", pady=(0, 10))

        # Scrollable course list
        self.setup_course_list(main_frame)

        # Controls
        self.setup_controls(main_frame)

        # Populate courses
        self.populate_courses()

        # Update initial credits count
        self.update_credits_count()

        logger.info("✅ Dialog UI setup complete")

    def setup_course_list(self, parent):
        """Setup scrollable course selection list."""
        logger.debug("📋 Setting up scrollable course list...")

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
        logger.debug("🎛️ Setting up control buttons...")

        control_frame = ttk.Frame(parent)
        control_frame.pack(fill="x", pady=(10, 0))

        # Clear button
        clear_btn = ttk.Button(control_frame, text="Clear Selections",
                  command=self.clear_selections)
        clear_btn.pack(side="left", padx=(0, 10))

        # Auto-selection preferences frame
        pref_frame = ttk.LabelFrame(control_frame, text="Auto-Selection Preferences")
        pref_frame.pack(side="left", padx=(10, 20), fill="x", expand=True)

        # Auto-selection criteria
        self.prefer_early_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(pref_frame, text="Prefer early time slots",
                       variable=self.prefer_early_var,
                       command=lambda: logger.debug(f"⚙️ Prefer early: {self.prefer_early_var.get()}")).pack(side="left", padx=5)

        self.avoid_friday_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(pref_frame, text="Avoid Friday classes",
                       variable=self.avoid_friday_var,
                       command=lambda: logger.debug(f"⚙️ Avoid Friday: {self.avoid_friday_var.get()}")).pack(side="left", padx=5)

        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side="right")

        cancel_btn = ttk.Button(button_frame, text="Cancel",
                  command=lambda: (logger.info("❌ User clicked Cancel"), self.dialog.destroy()))
        cancel_btn.pack(side="left", padx=5)

        generate_btn = ttk.Button(button_frame, text="Generate Schedule",
                  command=self.on_ok)
        generate_btn.pack(side="left", padx=5)

    def populate_courses(self):
        """Populate the course selection list with unique main codes only."""
        logger.info("📝 Populating course list (only showing unique courses)...")

        # Get unique courses by main_code
        unique_courses = {}
        for main_code, group in self.course_groups.items():
            # Prefer lecture sections for display
            lecture = next((c for c in group if c.course_type == CourseType.LECTURE), None)
            if lecture:
                unique_courses[main_code] = lecture
            else:
                unique_courses[main_code] = group[0]

        logger.info(f"📊 Displaying {len(unique_courses)} unique courses (grouped by main_code)")

        # Create course selection widgets for unique main codes only
        for main_code in sorted(unique_courses.keys()):
            representative_course = unique_courses[main_code]
            self.create_course_widget(main_code, representative_course)

        logger.info("✅ Course list populated")

    def create_course_widget(self, main_code: str, course: Course):
        """Create widget for a single course selection using main_code."""
        frame = ttk.Frame(self.selection_frame)
        frame.pack(fill="x", anchor="w", pady=2)

        # State variable (0=Neutral, 1=Include, 2=Exclude)
        state_var = tk.IntVar(value=0)
        self.state_vars[main_code] = state_var

        # Course info - ONLY show main_code and name, NO section details
        course_info = f"{main_code} - {course.name} ({course.ects} ECTS)"

        # Count available sections for info only (not displayed in button)
        group_courses = self.course_groups.get(main_code, [])
        lectures = [c for c in group_courses if c.course_type == CourseType.LECTURE]
        labs = [c for c in group_courses if c.course_type == CourseType.LAB]
        ps_sections = [c for c in group_courses if c.course_type == CourseType.PS]

        logger.debug(f"  📌 {main_code}: {len(lectures)} lectures, {len(labs)} labs, {len(ps_sections)} PS")

        # Selection button - NO SECTION INFO SHOWN
        btn = tk.Button(frame, text=course_info, width=70, anchor="w",
                       command=lambda: self.cycle_state(main_code, frame))
        btn.pack(side="left", padx=(0, 10))
        frame.button = btn

        # Frequency selection (Priority)
        freq_frame = ttk.Frame(frame)
        freq_frame.pack(side="left", padx=(10, 0))

        ttk.Label(freq_frame, text="Priority:").pack(side="left", padx=(0, 5))

        freq_var = tk.IntVar(value=2)  # Default to "Normal"
        self.frequency_vars[main_code] = freq_var

        for val, text in [(0, "Never"), (1, "Low"), (2, "Normal"), (3, "High")]:
            rb = ttk.Radiobutton(freq_frame, text=text, variable=freq_var, value=val,
                               command=lambda m=main_code, v=val, t=text:
                                   logger.debug(f"🔘 {m} priority changed to: {t}"))
            rb.pack(side="left", padx=2)

    def cycle_state(self, main_code: str, frame: ttk.Frame):
        """Cycle through selection states for a course."""
        current = self.state_vars[main_code].get()
        new_state = (current + 1) % 3
        self.state_vars[main_code].set(new_state)

        state_names = {0: "Neutral", 1: "Include", 2: "Exclude"}
        logger.info(f"🔄 {main_code} state changed: {state_names[current]} → {state_names[new_state]}")

        # Update button appearance
        if new_state == 0:  # Neutral
            frame.button.config(bg="SystemButtonFace", relief="raised")
        elif new_state == 1:  # Include
            frame.button.config(bg="lightgreen", relief="sunken")
        elif new_state == 2:  # Exclude
            frame.button.config(bg="lightcoral", relief="sunken")

        self.update_credits_count()

    def update_credits_count(self):
        """Update the credits counter display."""
        total_credits = 0
        included_courses = []

        for main_code, state_var in self.state_vars.items():
            state = state_var.get()
            if state == 1:  # Include
                group = self.course_groups.get(main_code, [])
                lecture = next((c for c in group if c.course_type == CourseType.LECTURE), None)
                if lecture:
                    total_credits += lecture.ects
                    included_courses.append(main_code)

        self.credits_var.set(f"Total selected credits: {total_credits}")
        logger.debug(f"💳 Credits updated: {total_credits} ECTS from {len(included_courses)} courses")

    def clear_selections(self):
        """Clear all course selections."""
        logger.info("🧹 Clearing all selections...")

        for main_code in self.state_vars:
            self.state_vars[main_code].set(0)
            # Find and reset button appearance
            for child in self.selection_frame.winfo_children():
                if hasattr(child, 'button'):
                    child.button.config(bg="SystemButtonFace", relief="raised")

        self.update_credits_count()
        logger.info("✅ All selections cleared")

    def on_ok(self):
        """Handle OK button click."""
        logger.info("="*80)
        logger.info("✅ Generate Schedule button clicked!")

        try:
            # Collect selections
            mandatory_courses = set()
            frequency_prefs = {}

            for main_code, state_var in self.state_vars.items():
                state = state_var.get()
                if state == 1:  # Include
                    mandatory_courses.add(main_code)
                    logger.info(f"  ✓ {main_code} - INCLUDED")
                elif state == 2:  # Exclude
                    frequency_prefs[main_code] = Frequency.NEVER
                    logger.info(f"  ✗ {main_code} - EXCLUDED")

                # Collect frequency preferences for all courses
                freq_value = self.frequency_vars[main_code].get()
                frequency_prefs[main_code] = Frequency(freq_value)

            logger.info(f"📊 Total included courses: {len(mandatory_courses)}")

            # Validate that at least one course is selected
            if not mandatory_courses:
                logger.warning("⚠️ No courses selected")
                messagebox.showwarning("Selection Warning", "Please select at least one course.")
                return

            # Validate credit limit
            total_credits = 0
            for main_code in mandatory_courses:
                group = self.course_groups.get(main_code, [])
                lecture = next((c for c in group if c.course_type == CourseType.LECTURE), None)
                if lecture:
                    total_credits += lecture.ects

            logger.info(f"💳 Total credits: {total_credits} ECTS")

            if total_credits > 31:  # Default max ECTS
                logger.warning(f"⚠️ Credits ({total_credits}) exceed maximum (31)")
                if not messagebox.askyesno("Credit Warning",
                                         f"Total selected credits ({total_credits}) exceed the recommended maximum (31).\n"
                                         "Do you want to continue anyway?"):
                    logger.info("❌ User cancelled due to credit warning")
                    return

            # Create preferences object with auto-selection preferences
            preferences = UserPreferences(
                mandatory_courses=mandatory_courses,
                frequency_prefs=frequency_prefs,
                auto_select_sections=True,  # System will auto-select sections
                prefer_early_times=self.prefer_early_var.get(),
                avoid_friday_classes=self.avoid_friday_var.get()
            )

            logger.info("🎯 Preferences created:")
            logger.info(f"  - Auto-select sections: {preferences.auto_select_sections}")
            logger.info(f"  - Prefer early times: {preferences.prefer_early_times}")
            logger.info(f"  - Avoid Friday: {preferences.avoid_friday_classes}")

            # Close dialog and call callback
            self.dialog.destroy()
            logger.info("🚀 Calling scheduler callback...")
            self.callback(preferences)

            logger.info(f"✅ Course selection completed: {len(mandatory_courses)} courses selected for automatic scheduling")
            logger.info("="*80)

        except Exception as e:
            logger.error(f"❌ Error in course selection: {e}", exc_info=True)
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
