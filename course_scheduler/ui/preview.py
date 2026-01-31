"""
Course preview tab with enhanced filtering capabilities and snapshot management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable
import logging

from ..core.models import Course, FilterProfile
from ..utils.snapshot import SnapshotManager

logger = logging.getLogger(__name__)


class CoursePreviewTab:
    """Enhanced course preview with comprehensive filtering and snapshot functionality."""

    def __init__(self, parent: tk.Widget, app):
        self.parent = parent
        self.app = app
        self.courses: List[Course] = []
        self.snapshot_manager = SnapshotManager("course_snapshots.sqlite")

        # Filter variables
        self.search_var = tk.StringVar()
        self.faculty_var = tk.StringVar(value="All")
        self.department_var = tk.StringVar(value="All")
        self.campus_var = tk.StringVar(value="All")
        self.ects_min_var = tk.IntVar(value=0)
        self.ects_max_var = tk.IntVar(value=50)
        self.restrict_var = tk.BooleanVar(value=True)
        self.show_time_var = tk.BooleanVar(value=False)

        # Day and time slot variables
        self.day_vars = {day: tk.BooleanVar(value=True) for day in ["M", "T", "W", "Th", "F", "Sa", "Su"]}
        self.slot_vars = {slot: tk.BooleanVar(value=True) for slot in range(1, 13)}

        self.setup_ui()

    def setup_ui(self):
        """Setup the course preview UI."""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Filter controls
        self.setup_filter_controls(main_frame)

        # Course treeview
        self.setup_course_treeview(main_frame)

        # Action buttons
        self.setup_action_buttons(main_frame)

        # Status
        self.status_var = tk.StringVar(value="No courses loaded")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack(pady=5)

    def setup_filter_controls(self, parent):
        """Setup filter control panel."""
        filter_frame = ttk.LabelFrame(parent, text="Course Filters", padding=10)
        filter_frame.pack(fill="x", pady=(0, 10))

        # Row 1: Search and Faculty
        row1 = ttk.Frame(filter_frame)
        row1.pack(fill="x", pady=2)

        ttk.Label(row1, text="Search:").pack(side="left", padx=(0, 5))
        search_entry = ttk.Entry(row1, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self.apply_filters())

        ttk.Label(row1, text="Faculty:").pack(side="left", padx=(20, 5))
        self.faculty_combo = ttk.Combobox(row1, textvariable=self.faculty_var, width=20, state="readonly")
        self.faculty_combo.pack(side="left", padx=5)
        self.faculty_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())

        # Row 2: Department and Campus
        row2 = ttk.Frame(filter_frame)
        row2.pack(fill="x", pady=2)

        ttk.Label(row2, text="Department:").pack(side="left", padx=(0, 5))
        self.department_combo = ttk.Combobox(row2, textvariable=self.department_var, width=25, state="readonly")
        self.department_combo.pack(side="left", padx=5)
        self.department_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())

        ttk.Label(row2, text="Campus:").pack(side="left", padx=(20, 5))
        self.campus_combo = ttk.Combobox(row2, textvariable=self.campus_var, width=20, state="readonly")
        self.campus_combo.pack(side="left", padx=5)
        self.campus_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())

        # Row 3: ECTS Range
        row3 = ttk.Frame(filter_frame)
        row3.pack(fill="x", pady=2)

        ttk.Label(row3, text="ECTS Range:").pack(side="left", padx=(0, 5))
        ects_frame = ttk.Frame(row3)
        ects_frame.pack(side="left", padx=5)

        self.ects_min_scale = tk.Scale(ects_frame, from_=0, to=20, orient="horizontal",
                                      variable=self.ects_min_var, length=100, command=lambda v: self.apply_filters())
        self.ects_min_scale.pack(side="left")
        ttk.Label(ects_frame, text="to").pack(side="left", padx=5)
        self.ects_max_scale = tk.Scale(ects_frame, from_=0, to=20, orient="horizontal",
                                      variable=self.ects_max_var, length=100, command=lambda v: self.apply_filters())
        self.ects_max_scale.pack(side="left")

        # Row 4: Days and Time Toggle
        row4 = ttk.Frame(filter_frame)
        row4.pack(fill="x", pady=2)

        ttk.Label(row4, text="Days:").pack(side="left", padx=(0, 5))
        day_frame = ttk.Frame(row4)
        day_frame.pack(side="left", padx=5)

        for day in ["M", "T", "W", "Th", "F", "Sa", "Su"]:
            cb = ttk.Checkbutton(day_frame, text=day, variable=self.day_vars[day],
                               command=self.apply_filters)
            cb.pack(side="left", padx=2)

        # Time slots toggle
        time_toggle = ttk.Checkbutton(row4, text="Time Slots", variable=self.show_time_var,
                                     command=self.toggle_time_filters)
        time_toggle.pack(side="left", padx=(20, 5))

        # Time slots frame (initially hidden)
        self.time_frame = ttk.Frame(filter_frame)
        for hour in range(1, 13):
            cb = ttk.Checkbutton(self.time_frame, text=f"{hour}", variable=self.slot_vars[hour],
                               command=self.apply_filters)
            cb.pack(side="left", padx=2)

        # Row 5: Control buttons and restriction
        row5 = ttk.Frame(filter_frame)
        row5.pack(fill="x", pady=(10, 0))

        ttk.Button(row5, text="Apply Filters", command=self.apply_filters).pack(side="left", padx=5)
        ttk.Button(row5, text="Clear All", command=self.clear_filters).pack(side="left", padx=5)

        # Restriction checkbox with color indicator
        self.restrict_check = ttk.Checkbutton(row5, text="Use filtered courses in next step",
                                            variable=self.restrict_var, command=self.update_restrict_indicator)
        self.restrict_check.pack(side="left", padx=(20, 5))

        # Update indicator initially
        self.update_restrict_indicator()

    def setup_course_treeview(self, parent):
        """Setup course display treeview."""
        tree_frame = ttk.LabelFrame(parent, text="Courses", padding=10)
        tree_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Treeview with enhanced columns
        columns = ("Code", "Name", "ECTS", "Type", "Schedule", "Instructor", "Faculty", "Department", "Campus")
        self.courses_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        # Configure columns
        column_widths = {"Code": 80, "Name": 200, "ECTS": 50, "Type": 60, "Schedule": 120,
                        "Instructor": 120, "Faculty": 100, "Department": 120, "Campus": 80}

        for col in columns:
            self.courses_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.courses_tree.column(col, width=column_widths.get(col, 100))

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.courses_tree.yview)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.courses_tree.xview)
        h_scrollbar.pack(side="bottom", fill="x")

        self.courses_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.courses_tree.pack(fill="both", expand=True)

    def setup_action_buttons(self, parent):
        """Setup action buttons."""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill="x", pady=5)

        # Snapshot controls
        ttk.Button(action_frame, text="💾 Save Snapshot",
                  command=self.save_snapshot_manual).pack(side="left", padx=5)
        ttk.Button(action_frame, text="📂 Load Snapshot",
                  command=self.load_snapshot_dialog).pack(side="left", padx=5)

        # Proceed button
        ttk.Button(action_frame, text="Proceed to Course Selection",
                  command=self.proceed_to_selection, style="Accent.TButton").pack(side="right", padx=5)

    def load_courses(self, courses: List[Course]):
        """Load courses and setup filter options."""
        self.courses = courses

        # Update filter combo options
        faculties = ["All"] + sorted(set(c.faculty for c in courses))
        departments = ["All"] + sorted(set(c.department for c in courses))
        campuses = ["All"] + sorted(set(c.campus for c in courses))

        self.faculty_combo['values'] = faculties
        self.department_combo['values'] = departments
        self.campus_combo['values'] = campuses

        # Apply initial filters
        self.apply_filters()
        logger.info(f"Loaded {len(courses)} courses in preview")

    def toggle_time_filters(self):
        """Toggle visibility of time slot filters."""
        if self.show_time_var.get():
            self.time_frame.pack(fill="x", pady=2)
        else:
            self.time_frame.pack_forget()

    def apply_filters(self):
        """Apply all filters and update the treeview."""
        if not self.courses:
            return

        # Clear existing items
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)

        # Get filter values
        search_term = self.search_var.get().lower().strip()
        faculty_filter = self.faculty_var.get()
        department_filter = self.department_var.get()
        campus_filter = self.campus_var.get()
        ects_min = self.ects_min_var.get()
        ects_max = self.ects_max_var.get()

        selected_days = [day for day, var in self.day_vars.items() if var.get()]
        selected_slots = [slot for slot, var in self.slot_vars.items() if var.get()]

        # Separate courses by data completeness
        valid_courses = []
        non_credit_courses = []  # PS, Lab courses with 0 ECTS (normal)
        non_scheduled_courses = []  # Staj, internship courses (normal)
        incomplete_courses = []  # Actually missing data

        for course in self.courses:
            # Text search
            if search_term and not (search_term in course.code.lower() or
                                   search_term in course.name.lower()):
                continue

            # Faculty filter
            if faculty_filter != "All" and course.faculty != faculty_filter:
                continue

            # Department filter
            if department_filter != "All" and course.department != department_filter:
                continue

            # Campus filter
            if campus_filter != "All" and course.campus != campus_filter:
                continue

            # Classify course based on missing data type
            has_no_schedule = len(course.schedule) == 0
            has_no_ects = course.ects == 0

            # Check if this is a non-scheduled course (Staj, internship, etc.)
            is_non_scheduled = any(keyword in course.name.lower() for keyword in
                                 ['staj', 'internship', 'proje', 'tez', 'thesis'])

            # Check if this is a non-credit course (PS, Lab)
            is_non_credit = (course.course_type.value.lower() in ['ps', 'lab'] or
                           any(keyword in course.name.lower() for keyword in
                               ['ps', 'lab', 'laboratuvar', 'uygulama', 'problem']))

            # Categorize the course
            if is_non_scheduled and has_no_schedule:
                # Non-scheduled courses (Staj, etc.) - no schedule is normal
                # Apply ECTS filter for non-scheduled courses too
                if course.ects > 0 and not (ects_min <= course.ects <= ects_max):
                    continue
                non_scheduled_courses.append(course)
                continue
            elif is_non_credit and has_no_ects:
                # Non-credit courses (PS, Lab) - no ECTS is normal
                # Skip ECTS filter for true non-credit courses (0 ECTS PS/Lab)
                non_credit_courses.append(course)
                continue
            elif has_no_schedule or (has_no_ects and not is_non_credit):
                # Actually incomplete courses - skip ECTS filter as they might have missing data
                incomplete_courses.append(course)
                continue

            # This is a complete course, apply full filtering
            # ECTS range (only for complete courses)
            if not (ects_min <= course.ects <= ects_max):
                continue

            # Day filter (only for complete courses)
            course_days = [day for day, _ in course.schedule]
            if selected_days and not any(day in selected_days for day in course_days):
                continue

            # Time slot filter (only for complete courses)
            course_slots = [slot for _, slot in course.schedule]
            if selected_slots and not any(slot in selected_slots for slot in course_slots):
                continue

            valid_courses.append(course)

        # Configure tags for styling
        self.courses_tree.tag_configure("normal", foreground="black")
        self.courses_tree.tag_configure("non_credit", foreground="blue")
        self.courses_tree.tag_configure("non_scheduled", foreground="purple")
        self.courses_tree.tag_configure("incomplete", foreground="red")

        # Populate with valid courses first
        for course in valid_courses:
            schedule_str = ", ".join(f"{d}{h}" for d, h in course.schedule)
            self.courses_tree.insert("", tk.END, values=(
                course.code,
                course.name,
                course.ects,
                course.course_type.value,
                schedule_str,
                course.teacher,
                course.faculty,
                course.department,
                course.campus
            ), tags=("normal",))

        # Add non-credit courses (PS, Lab with 0 ECTS)
        for course in non_credit_courses:
            schedule_str = ", ".join(f"{d}{h}" for d, h in course.schedule) if course.schedule else "📝 Non-Credit Course"
            course_name = f"📚 {course.name}"

            self.courses_tree.insert("", tk.END, values=(
                course.code,
                course_name,
                "Non-Credit" if course.ects == 0 else course.ects,
                course.course_type.value,
                schedule_str,
                course.teacher,
                course.faculty,
                course.department,
                course.campus
            ), tags=("non_credit",))

        # Add non-scheduled courses (Staj, etc.)
        for course in non_scheduled_courses:
            course_name = f"🎓 {course.name}"
            ects_display = course.ects if course.ects > 0 else "Variable"

            self.courses_tree.insert("", tk.END, values=(
                course.code,
                course_name,
                ects_display,
                course.course_type.value,
                "📅 Non-Scheduled",
                course.teacher,
                course.faculty,
                course.department,
                course.campus
            ), tags=("non_scheduled",))

        # Finally, add truly incomplete courses at the bottom
        for course in incomplete_courses:
            # Handle missing schedule
            if len(course.schedule) == 0:
                schedule_str = "❌ Eksik Saat Bilgisi"
            else:
                schedule_str = ", ".join(f"{d}{h}" for d, h in course.schedule)

            # Handle missing ECTS (only if it's not a PS/Lab course)
            if course.ects == 0:
                ects_display = "❌ Eksik ECTS"
            else:
                ects_display = course.ects

            # Mark course name with warning icon
            course_name = f"⚠️ {course.name}"

            self.courses_tree.insert("", tk.END, values=(
                course.code,
                course_name,
                ects_display,
                course.course_type.value,
                schedule_str,
                course.teacher,
                course.faculty,
                course.department,
                course.campus
            ), tags=("incomplete",))

        # Update status
        total_count = len(self.courses)
        valid_count = len(valid_courses)
        non_credit_count = len(non_credit_courses)
        non_scheduled_count = len(non_scheduled_courses)
        incomplete_count = len(incomplete_courses)
        visible_count = valid_count + non_credit_count + non_scheduled_count + incomplete_count

        status_parts = []
        if valid_count > 0:
            status_parts.append(f"{valid_count} normal")
        if non_credit_count > 0:
            status_parts.append(f"{non_credit_count} non-credit")
        if non_scheduled_count > 0:
            status_parts.append(f"{non_scheduled_count} non-scheduled")
        if incomplete_count > 0:
            status_parts.append(f"{incomplete_count} eksik veri")

        if visible_count == total_count:
            self.status_var.set(f"Tüm {total_count} kurs görünüyor ({', '.join(status_parts)})")
        else:
            self.status_var.set(f"{visible_count} / {total_count} kurs görünüyor ({', '.join(status_parts)})")

        logger.debug(f"Filters applied: {visible_count}/{total_count} courses visible "
                    f"(normal: {valid_count}, non-credit: {non_credit_count}, "
                    f"non-scheduled: {non_scheduled_count}, incomplete: {incomplete_count})")

    def clear_filters(self):
        """Clear all filters and show all courses."""
        self.search_var.set("")
        self.faculty_var.set("All")
        self.department_var.set("All")
        self.campus_var.set("All")
        self.ects_min_var.set(0)
        self.ects_max_var.set(50)

        for var in self.day_vars.values():
            var.set(True)
        for var in self.slot_vars.values():
            var.set(True)

        self.apply_filters()

    def update_restrict_indicator(self):
        """Update the visual indicator for the restrict checkbox."""
        if self.restrict_var.get():
            # Try to configure foreground color (may not work on all systems)
            try:
                self.restrict_check.configure(foreground="red")
            except:
                pass
        else:
            try:
                self.restrict_check.configure(foreground="green")
            except:
                pass

    def sort_by_column(self, column):
        """Sort treeview by the specified column."""
        items = [(self.courses_tree.set(item, column), item) for item in self.courses_tree.get_children("")]

        # Try numeric sort for ECTS column
        if column == "ECTS":
            try:
                items.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0)
            except (ValueError, TypeError):
                items.sort(key=lambda x: str(x[0]))
        else:
            items.sort(key=lambda x: str(x[0]))

        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.courses_tree.move(item, "", index)

    def get_current_filter_profile(self) -> FilterProfile:
        """Get current filter settings as a profile."""
        return FilterProfile(
            query=self.search_var.get(),
            faculty=self.faculty_var.get(),
            department=self.department_var.get(),
            campus=self.campus_var.get(),
            ects_min=self.ects_min_var.get(),
            ects_max=self.ects_max_var.get(),
            days=[day for day, var in self.day_vars.items() if var.get()],
            slots=[slot for slot, var in self.slot_vars.items() if var.get()],
            restricted=self.restrict_var.get()
        )

    def get_visible_courses(self) -> List[Course]:
        """Get list of currently visible courses (excluding incomplete ones for scheduling)."""
        visible_codes = []
        for item in self.courses_tree.get_children():
            # Only exclude truly incomplete courses, include non-credit and non-scheduled
            tags = self.courses_tree.item(item, "tags")
            if "incomplete" not in tags:
                code = self.courses_tree.set(item, "Code")
                visible_codes.append(code)

        return [c for c in self.courses if c.code in visible_codes]

    def get_all_visible_courses(self) -> List[Course]:
        """Get all currently visible courses including incomplete ones."""
        visible_codes = []
        for item in self.courses_tree.get_children():
            code = self.courses_tree.set(item, "Code")
            visible_codes.append(code)

        return [c for c in self.courses if c.code in visible_codes]

    def save_snapshot_manual(self):
        """Manually save current filter state and visible courses."""
        try:
            visible_courses = self.get_visible_courses()
            if not visible_courses:
                messagebox.showwarning("Save Snapshot", "No courses are currently visible to save.")
                return

            filter_profile = self.get_current_filter_profile()
            snapshot_id = self.snapshot_manager.save_snapshot(visible_courses, filter_profile)

            brief = filter_profile.to_dict()
            messagebox.showinfo("Snapshot Saved",
                              f"Snapshot #{snapshot_id} saved successfully!\n"
                              f"Courses: {len(visible_courses)}")
            logger.info(f"Manual snapshot saved: ID {snapshot_id}, {len(visible_courses)} courses")

        except Exception as e:
            logger.error(f"Failed to save manual snapshot: {e}")
            messagebox.showerror("Save Error", f"Failed to save snapshot: {e}")

    def load_snapshot_dialog(self):
        """Show dialog to select and load a snapshot."""
        try:
            snapshots = self.snapshot_manager.list_snapshots()
            if not snapshots:
                messagebox.showinfo("Load Snapshot", "No snapshots found.")
                return

            # Create simple selection dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title("Load Snapshot")
            dialog.geometry("600x400")
            dialog.transient(self.parent)
            dialog.grab_set()

            # Snapshot list
            list_frame = ttk.Frame(dialog)
            list_frame.pack(fill="both", expand=True, padx=10, pady=10)

            columns = ("ID", "Created", "Courses", "Description")
            snapshot_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

            for col in columns:
                snapshot_tree.heading(col, text=col)

            snapshot_tree.column("ID", width=50)
            snapshot_tree.column("Created", width=150)
            snapshot_tree.column("Courses", width=80)
            snapshot_tree.column("Description", width=300)

            # Add snapshots to tree
            for snapshot in snapshots:
                brief = snapshot.get_brief_description()
                snapshot_tree.insert("", tk.END, values=(
                    snapshot.id, snapshot.created_at, snapshot.course_count, brief
                ))

            snapshot_tree.pack(fill="both", expand=True)

            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill="x", padx=10, pady=5)

            def load_selected():
                selection = snapshot_tree.selection()
                if not selection:
                    messagebox.showwarning("Load Snapshot", "Please select a snapshot to load.")
                    return

                item = selection[0]
                snapshot_id = int(snapshot_tree.set(item, "ID"))

                try:
                    courses, profile = self.snapshot_manager.load_snapshot(snapshot_id)
                    self.apply_profile_to_ui(profile)

                    # Update app state
                    self.app.set_filtered_courses(courses, profile)

                    brief = profile.to_dict()
                    self.status_var.set(f"Loaded snapshot #{snapshot_id}")

                    dialog.destroy()
                    logger.info(f"Loaded snapshot {snapshot_id} with {len(courses)} courses")

                except Exception as e:
                    logger.error(f"Failed to load snapshot {snapshot_id}: {e}")
                    messagebox.showerror("Load Error", f"Failed to load snapshot: {e}")

            ttk.Button(button_frame, text="Load Selected", command=load_selected).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

        except Exception as e:
            logger.error(f"Failed to show load dialog: {e}")
            messagebox.showerror("Load Error", f"Failed to load snapshots: {e}")

    def apply_profile_to_ui(self, profile: FilterProfile):
        """Apply a filter profile to the UI controls."""
        self.search_var.set(profile.query)
        self.faculty_var.set(profile.faculty)
        self.department_var.set(profile.department)
        self.campus_var.set(profile.campus)
        self.ects_min_var.set(profile.ects_min)
        self.ects_max_var.set(profile.ects_max)

        # Clear all day/slot selections first
        for var in self.day_vars.values():
            var.set(False)
        for var in self.slot_vars.values():
            var.set(False)

        # Set selected days/slots
        for day in profile.days:
            if day in self.day_vars:
                self.day_vars[day].set(True)
        for slot in profile.slots:
            if slot in self.slot_vars:
                self.slot_vars[slot].set(True)

        self.restrict_var.set(profile.restricted)
        self.update_restrict_indicator()
        self.apply_filters()

    def proceed_to_selection(self):
        """Proceed to course selection with optional filtering."""
        try:
            if self.restrict_var.get():
                # Filter-first workflow
                visible_courses = self.get_visible_courses()

                if not visible_courses:
                    messagebox.showwarning("Proceed",
                                         "No courses are currently visible. Please adjust filters or disable restriction.")
                    return

                filter_profile = self.get_current_filter_profile()

                # Set filtered courses in app
                self.app.set_filtered_courses(visible_courses, filter_profile)

                logger.info(f"Proceeding with FILTERED course set: {len(visible_courses)} courses")
                self.app.proceed_to_selection(visible_courses)
            else:
                # Use all courses
                self.app.set_filtered_courses(None, None)
                logger.info(f"Proceeding with ALL courses: {len(self.courses)} courses")
                self.app.proceed_to_selection(self.courses)

        except Exception as e:
            logger.error(f"Error in proceed_to_selection: {e}")
            messagebox.showerror("Proceed Error", f"Failed to proceed: {e}")

    def clear_data(self):
        """Clear all course data and reset the preview tab."""
        try:
            # Clear courses list
            self.courses = []

            # Clear treeview
            for item in self.courses_tree.get_children():
                self.courses_tree.delete(item)

            # Reset filters to default
            self.search_var.set("")
            self.faculty_var.set("All")
            self.department_var.set("All")
            self.campus_var.set("All")
            self.ects_min_var.set(0)
            self.ects_max_var.set(50)
            self.restrict_var.set(True)
            self.show_time_var.set(False)

            # Reset day and time slot variables
            for var in self.day_vars.values():
                var.set(True)
            for var in self.slot_vars.values():
                var.set(True)

            # Reset combo boxes
            self.faculty_combo['values'] = ["All"]
            self.department_combo['values'] = ["All"]
            self.campus_combo['values'] = ["All"]

            # Hide time frame if visible
            if self.show_time_var.get():
                self.time_frame.pack_forget()

            # Update status
            self.status_var.set("No courses loaded")

            logger.info("Preview tab data cleared successfully")

        except Exception as e:
            logger.error(f"Error clearing preview data: {e}", exc_info=True)
            raise
