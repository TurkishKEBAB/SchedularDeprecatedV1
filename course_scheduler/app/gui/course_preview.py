"""
Course preview tab implementation for the course scheduler.

This module provides the second tab of the application, where users can
preview loaded courses and search through them.
"""
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk  # Keep ttk for Treeview since CustomTkinter doesn't have one yet
import pandas as pd
from typing import List, Any
import logging

from ..data.models import Course
from ..utils.schedule_utils import get_all_days, get_short_day_name, get_time_for_slot

# Set up logging
logger = logging.getLogger(__name__)


class CoursePreviewTab:
    """
    Second tab of the scheduler application for previewing loaded courses.

    This tab allows users to:
    1. See all loaded courses in a table view
    2. Search for specific courses by code or name
    3. Apply multiple filters: Faculty, Department, Campus, Day, Time slot, Credits
    4. Sort courses by any column
    5. Restrict course selection to the filtered set
    """

    def __init__(self, parent: ctk.CTkFrame, main_app: Any):
        """
        Initialize the course preview tab.

        Args:
            parent: Parent frame (tab container)
            main_app: Reference to the main application
        """
        self.parent = parent
        self.main_app = main_app

        # Internal dataframe for filtering
        self.courses_df = pd.DataFrame()

        # Filter state variables
        self.faculty_var = ctk.StringVar(value="All")
        self.department_var = ctk.StringVar(value="All")
        self.campus_var = ctk.StringVar(value="All")
        self.restrict_var = ctk.BooleanVar(value=True)  # Changed from False to True
        self.selected_days = set()
        self.selected_slots = set()
        self.min_credit = ctk.IntVar(value=0)
        self.max_credit = ctk.IntVar(value=20)

        # Create widgets
        self._create_filter_section()
        self._create_course_treeview()
        self._create_button_section()

    def _create_filter_section(self):
        """Create the filter section with all filtering options."""
        # Main filter frame
        filter_frame = ctk.CTkFrame(self.parent)
        filter_frame.pack(fill="x", padx=20, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            filter_frame,
            text="🔍 Search & Filter Courses",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # Top row - Text search and restrict checkbox
        top_row = ctk.CTkFrame(filter_frame)
        top_row.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            top_row,
            text="Search:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(10, 5))

        self.search_entry = ctk.CTkEntry(
            top_row,
            placeholder_text="Enter course code or name...",
            width=300
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda event: self._apply_filters())

        search_btn = ctk.CTkButton(
            top_row,
            text="🔍 Search",
            command=self._apply_filters,
            width=100
        )
        search_btn.pack(side="left", padx=5)

        clear_btn = ctk.CTkButton(
            top_row,
            text="🗑️ Clear",
            command=self._clear_filters,
            width=80,
            fg_color=("gray60", "gray40"),
            hover_color=("gray50", "gray30")
        )
        clear_btn.pack(side="left", padx=5)

        # Restrict to filtered courses checkbox with color indication
        self.restrict_check = ctk.CTkCheckBox(
            top_row,
            text="Use filtered courses in next step",
            variable=self.restrict_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_restrict_changed
        )
        self.restrict_check.pack(side="right", padx=15)

        # Update checkbox color based on state
        self._update_restrict_checkbox_color()

        # Second row - Faculty, Department, Campus dropdowns
        dropdowns_row = ctk.CTkFrame(filter_frame)
        dropdowns_row.pack(fill="x", padx=15, pady=5)

        # Faculty dropdown
        ctk.CTkLabel(
            dropdowns_row,
            text="Faculty:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=(10, 5))

        self.faculty_combo = ctk.CTkComboBox(
            dropdowns_row,
            variable=self.faculty_var,
            state="readonly",
            width=200,
            command=self._on_faculty_changed  # Fixed: remove parameter
        )
        self.faculty_combo.pack(side="left", padx=5)

        # Department dropdown
        ctk.CTkLabel(
            dropdowns_row,
            text="Department:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=(15, 5))

        self.department_combo = ctk.CTkComboBox(
            dropdowns_row,
            variable=self.department_var,
            state="readonly",
            width=200,
            command=lambda x: self._apply_filters()
        )
        self.department_combo.pack(side="left", padx=5)

        # Campus dropdown
        ctk.CTkLabel(
            dropdowns_row,
            text="Campus:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=(15, 5))

        self.campus_combo = ctk.CTkComboBox(
            dropdowns_row,
            variable=self.campus_var,
            state="readonly",
            width=150,
            command=lambda x: self._apply_filters()
        )
        self.campus_combo.pack(side="left", padx=5)

        # Third row - Credit range slider
        credit_row = ctk.CTkFrame(filter_frame)
        credit_row.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            credit_row,
            text="Credits:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=(10, 10))

        # Min credit scale
        ctk.CTkLabel(
            credit_row,
            text="Min:",
            font=ctk.CTkFont(size=10)
        ).pack(side="left", padx=(0, 5))

        self.min_scale = ctk.CTkSlider(
            credit_row,
            from_=0, to=20,
            number_of_steps=20,
            variable=self.min_credit,
            command=self._on_min_credit_change,
            width=120
        )
        self.min_scale.pack(side="left", padx=5)

        self.min_label = ctk.CTkLabel(
            credit_row,
            text="0",
            width=30,
            font=ctk.CTkFont(size=10)
        )
        self.min_label.pack(side="left", padx=(0, 15))

        # Max credit scale
        ctk.CTkLabel(
            credit_row,
            text="Max:",
            font=ctk.CTkFont(size=10)
        ).pack(side="left", padx=(0, 5))

        self.max_scale = ctk.CTkSlider(
            credit_row,
            from_=0, to=20,
            number_of_steps=20,
            variable=self.max_credit,
            command=self._on_max_credit_change,
            width=120
        )
        self.max_scale.pack(side="left", padx=5)

        self.max_label = ctk.CTkLabel(
            credit_row,
            text="20",
            width=30,
            font=ctk.CTkFont(size=10)
        )
        self.max_label.pack(side="left")

        # Fourth row - Day and Slot filters (collapsible)
        self.time_filter_frame = ctk.CTkFrame(filter_frame)
        self.time_filter_frame.pack(fill="x", padx=15, pady=5)

        # Toggle button for time filters
        self.show_time_filters = ctk.BooleanVar(value=False)
        self.time_toggle_btn = ctk.CTkButton(
            self.time_filter_frame,
            text="⏰ Show Time Filters",
            command=self._toggle_time_filters,
            width=150,
            height=30
        )
        self.time_toggle_btn.pack(pady=10)

        # Time filters container (initially hidden)
        self.time_filters_container = ctk.CTkFrame(self.time_filter_frame)

    def _toggle_time_filters(self):
        """Toggle visibility of time filters."""
        if self.show_time_filters.get():
            self.time_filters_container.pack_forget()
            self.time_toggle_btn.configure(text="⏰ Show Time Filters")
            self.show_time_filters.set(False)
        else:
            self._create_time_filters()
            self.time_filters_container.pack(fill="x", pady=5)
            self.time_toggle_btn.configure(text="🚫 Hide Time Filters")
            self.show_time_filters.set(True)

    def _create_time_filters(self):
        """Create the time filter widgets."""
        # Clear existing widgets
        for widget in self.time_filters_container.winfo_children():
            widget.destroy()

        # Day filter section
        day_section = ctk.CTkFrame(self.time_filters_container)
        day_section.pack(side="left", fill="both", expand=True, padx=5, pady=10)

        ctk.CTkLabel(
            day_section,
            text="📅 Days",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(5, 10))

        # Create day checkbuttons
        self.day_vars = {}
        day_buttons_frame = ctk.CTkFrame(day_section)
        day_buttons_frame.pack(padx=10, pady=5)

        for i, day_code in enumerate(get_all_days()):
            day_var = ctk.BooleanVar(value=False)
            self.day_vars[day_code] = day_var

            day_check = ctk.CTkCheckBox(
                day_buttons_frame,
                text=get_short_day_name(day_code),
                variable=day_var,
                command=self._update_day_selection,
                font=ctk.CTkFont(size=10)
            )
            day_check.grid(row=i//4, column=i%4, padx=3, pady=2, sticky="w")

        # Slot filter section
        slot_section = ctk.CTkFrame(self.time_filters_container)
        slot_section.pack(side="right", fill="both", expand=True, padx=5, pady=10)

        ctk.CTkLabel(
            slot_section,
            text="🕐 Time Slots",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(5, 10))

        # Create slot checkbuttons in a scrollable frame
        slot_scroll = ctk.CTkScrollableFrame(slot_section, height=120)
        slot_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        self.slot_vars = {}
        for i, slot in enumerate(range(1, 13)):
            slot_var = ctk.BooleanVar(value=False)
            self.slot_vars[slot] = slot_var

            slot_time = get_time_for_slot(slot)
            slot_check = ctk.CTkCheckBox(
                slot_scroll,
                text=f"{slot}: {slot_time}",
                variable=slot_var,
                command=self._update_slot_selection,
                font=ctk.CTkFont(size=9)
            )
            slot_check.grid(row=i//2, column=i%2, padx=3, pady=1, sticky="w")

    def _create_course_treeview(self):
        """Create the treeview for displaying courses."""
        tree_frame = ctk.CTkFrame(self.parent)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            tree_frame,
            text="📋 Course List",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Create treeview container
        tree_container = ctk.CTkFrame(tree_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Define columns
        columns = (
            "Code", "Lecture Name", "Credit", "Hour", "Lecture Instructor",
            "Faculty", "Department", "Campus"
        )

        # Create treeview (using ttk since CustomTkinter doesn't have treeview yet)
        self.courses_tree = ttk.Treeview(tree_container, columns=columns, show="headings")

        # Configure columns
        for col in columns:
            self.courses_tree.heading(
                col,
                text=col,
                command=lambda c=col: self._sort_by_column(c)
            )
            width = 150 if col in ("Lecture Name", "Faculty", "Department") else 100
            self.courses_tree.column(col, width=width)

        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.courses_tree.yview)
        y_scrollbar.pack(side="right", fill="y")

        x_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.courses_tree.xview)
        x_scrollbar.pack(side="bottom", fill="x")

        # Configure treeview to use scrollbars
        self.courses_tree.configure(
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        self.courses_tree.pack(fill="both", expand=True)

        # Add enhanced scrolling
        self._add_enhanced_scrolling()

    def _create_button_section(self):
        """Create the button section at the bottom of the tab."""
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.pack(fill="x", padx=20, pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(
            button_frame,
            text="Ready. Load courses to begin.",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="left", padx=15)

        # Proceed button
        self.proceed_btn = ctk.CTkButton(
            button_frame,
            text="➡️ Proceed to Course Selection",
            command=self._proceed_to_selection,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("blue", "darkblue"),
            hover_color=("darkblue", "blue")
        )
        self.proceed_btn.pack(side="right", padx=15)

    def _add_enhanced_scrolling(self):
        """Add enhanced scrolling with touchpad support."""
        # Bind mousewheel events for vertical scrolling
        self.courses_tree.bind("<MouseWheel>", self._on_mousewheel)  # Windows
        self.courses_tree.bind("<Button-4>", self._on_mousewheel)    # Linux scroll up
        self.courses_tree.bind("<Button-5>", self._on_mousewheel)    # Linux scroll down

        # For touchpad two-finger scrolling (horizontal)
        self.courses_tree.bind("<Shift-MouseWheel>", self._on_horizontal_scroll)

    def _on_mousewheel(self, event):
        """
        Handle vertical mousewheel/touchpad scrolling.

        Args:
            event: Mousewheel event
        """
        # Different event.delta values for Windows vs macOS/Linux
        if hasattr(event, 'num') and event.num == 5 or hasattr(event, 'delta') and event.delta < 0:
            # Scroll down - use smaller increments for smoother scrolling
            self.courses_tree.yview_scroll(2, "units")
        elif hasattr(event, 'num') and event.num == 4 or hasattr(event, 'delta') and event.delta > 0:
            # Scroll up - use smaller increments for smoother scrolling
            self.courses_tree.yview_scroll(-2, "units")

    def _on_horizontal_scroll(self, event):
        """
        Handle horizontal touchpad scrolling.

        Args:
            event: Shift+Mousewheel event
        """
        # For touchpad gestures or shift+wheel
        if event.delta < 0:  # Scroll right
            self.courses_tree.xview_scroll(2, "units")
        elif event.delta > 0:  # Scroll left
            self.courses_tree.xview_scroll(-2, "units")

    def _on_faculty_changed(self, value=None):  # Fixed: make parameter optional
        """Handle faculty selection change."""
        # Update departments based on selected faculty
        faculty = self.faculty_var.get()

        if faculty == "All":
            departments = ["All"] + sorted(self.courses_df["department"].unique().tolist())
        else:
            faculty_df = self.courses_df[self.courses_df["faculty"] == faculty]
            departments = ["All"] + sorted(faculty_df["department"].unique().tolist())

        # Update department dropdown
        self.department_combo["values"] = departments
        self.department_var.set("All")

        # Apply filters
        self._apply_filters()

    def _on_min_credit_change(self, value):
        """
        Handle minimum credit slider change.

        Args:
            value: New slider value
        """
        # Update label
        min_val = int(float(value))
        self.min_label.configure(text=f"Min: {min_val}")

        # Ensure min <= max
        max_val = self.max_credit.get()
        if min_val > max_val:
            self.max_credit.set(min_val)
            self.max_label.configure(text=f"Max: {min_val}")

        # Apply filters after a short delay - Fixed: remove args parameter
        self.parent.after(500, self._apply_filters)

    def _on_max_credit_change(self, value):
        """
        Handle maximum credit slider change.

        Args:
            value: New slider value
        """
        # Update label
        max_val = int(float(value))
        self.max_label.configure(text=f"Max: {max_val}")

        # Ensure max >= min
        min_val = self.min_credit.get()
        if max_val < min_val:
            self.min_credit.set(max_val)
            self.min_label.configure(text=f"Min: {max_val}")

        # Apply filters after a short delay - Fixed: remove args parameter
        self.parent.after(500, self._apply_filters)

    def _update_day_selection(self):
        """Update the set of selected days based on checkbutton states."""
        self.selected_days = {day for day, var in self.day_vars.items() if var.get()}
        self._apply_filters()

    def _update_slot_selection(self):
        """Update the set of selected slots based on checkbutton states."""
        self.selected_slots = {slot for slot, var in self.slot_vars.items() if var.get()}
        self._apply_filters()

    def _apply_filters(self):
        """Apply all active filters to the course data."""
        if self.courses_df.empty:
            return

        # Start with the full dataframe
        filtered_df = self.courses_df.copy()

        # Apply text search if provided
        search_term = self.search_entry.get().strip().lower()
        if search_term:
            mask = (
                filtered_df["code"].str.lower().str.contains(search_term) |
                filtered_df["name"].str.lower().str.contains(search_term)
            )
            filtered_df = filtered_df[mask]

        # Apply faculty filter
        faculty = self.faculty_var.get()
        if faculty != "All":
            filtered_df = filtered_df[filtered_df["faculty"] == faculty]

        # Apply department filter
        department = self.department_var.get()
        if department != "All":
            filtered_df = filtered_df[filtered_df["department"] == department]

        # Apply campus filter
        campus = self.campus_var.get()
        if campus != "All":
            filtered_df = filtered_df[filtered_df["campus"] == campus]

        # Apply credit range filter
        min_credit = self.min_credit.get()
        max_credit = self.max_credit.get()
        filtered_df = filtered_df[
            (filtered_df["ects"] >= min_credit) &
            (filtered_df["ects"] <= max_credit)
        ]

        # Apply day and slot filters if any are selected
        if self.selected_days or self.selected_slots:
            # Create a mask for rows that have at least one schedule slot matching the filters
            mask = pd.Series(False, index=filtered_df.index)

            for idx, row in filtered_df.iterrows():
                schedule = row["schedule"]
                # If days are selected, check if any schedule item matches selected days
                days_match = not self.selected_days or any(slot[0] in self.selected_days for slot in schedule)
                # If slots are selected, check if any schedule item matches selected slots
                slots_match = not self.selected_slots or any(slot[1] in self.selected_slots for slot in schedule)
                # Both day and slot filters must match
                mask.loc[idx] = days_match and slots_match

            filtered_df = filtered_df[mask]

        # Update treeview with filtered data
        self._update_treeview(filtered_df)

        # Update status label
        self.status_label.configure(text=f"Showing {len(filtered_df)} of {len(self.courses_df)} courses")

    def _update_treeview(self, df: pd.DataFrame):
        """
        Update the treeview with the given dataframe.

        Args:
            df: DataFrame containing course data to display
        """
        # Clear current items
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)

        # Add rows from dataframe
        for _, row in df.iterrows():
            # Format the schedule as a string
            schedule_str = ", ".join(f"{d}{h}" for d, h in row["schedule"])

            self.courses_tree.insert("", "end", values=(  # Fixed: use "end" instead of tk.END
                row["code"],
                row["name"],
                row["ects"],
                schedule_str,
                row["teacher"],
                row["faculty"],
                row["department"],
                row["campus"]
            ))

    def _clear_filters(self):
        """Clear all filters and show all courses."""
        # Reset search field
        self.search_entry.delete(0, tk.END)

        # Reset dropdowns
        self.faculty_var.set("All")
        self.department_var.set("All")
        self.campus_var.set("All")

        # Reset day checkboxes
        for var in self.day_vars.values():
            var.set(False)
        self.selected_days.clear()

        # Reset slot checkboxes
        for var in self.slot_vars.values():
            var.set(False)
        self.selected_slots.clear()

        # Reset credit range
        self.min_credit.set(0)
        self.min_label.configure(text="Min: 0")
        self.max_credit.set(20)
        self.max_label.configure(text="Max: 20")

        # Apply cleared filters (show all)
        self._apply_filters()

    def _sort_by_column(self, column):
        """
        Sort treeview by the specified column.

        Args:
            column: Column name to sort by
        """
        # Toggle sort direction
        if not hasattr(self, "_sort_reverse"):
            self._sort_reverse = {}

        if column not in self._sort_reverse:
            self._sort_reverse[column] = False
        else:
            self._sort_reverse[column] = not self._sort_reverse[column]

        # Get all items
        items = [(self.courses_tree.set(item, column), item) for item in self.courses_tree.get_children("")]

        # Sort items based on column type
        if column == "Credit":
            # Sort numerically
            items.sort(key=lambda x: float(x[0]) if x[0].replace(".", "").isdigit() else 0,
                      reverse=self._sort_reverse[column])
        else:
            # Sort alphabetically
            items.sort(reverse=self._sort_reverse[column])

        # Rearrange items in sorted order
        for idx, (_, item) in enumerate(items):
            self.courses_tree.move(item, "", idx)

    def _proceed_to_selection(self):
        """Proceed to the course selection step."""
        # Check if we should restrict to filtered courses
        if self.restrict_var.get() and not self.courses_df.empty:
            # Get visible (filtered) courses
            visible_indices = set()
            for item in self.courses_tree.get_children():
                code = self.courses_tree.item(item, "values")[0]
                mask = self.courses_df["code"] == code
                # Fixed: Check if any rows match instead of using mask.any() on boolean
                matching_rows = self.courses_df[mask]
                if not matching_rows.empty:
                    idx = matching_rows.index[0]
                    visible_indices.add(idx)

            # Create filtered course list
            filtered_courses = [
                self.main_app.courses[i] for i in range(len(self.main_app.courses))
                if i in visible_indices
            ]

            # Pass filtered course list to selection window
            self.main_app.open_course_selection(filtered_courses)
        else:
            # Pass all courses
            self.main_app.open_course_selection()

    def update_courses(self, courses: List[Course]):
        """
        Update the displayed courses.

        Args:
            courses: List of courses to display
        """
        # Create pandas DataFrame for easier filtering
        data = []
        for course in courses:
            data.append({
                "code": course.code,
                "main_code": course.main_code,
                "name": course.name,
                "ects": course.ects,
                "course_type": course.course_type,
                "schedule": course.schedule,
                "teacher": course.teacher,
                "faculty": getattr(course, 'faculty', 'Unknown Faculty'),  # Safe access
                "department": getattr(course, 'department', 'Unknown Department'),  # Safe access
                "campus": getattr(course, 'campus', 'Main Campus')  # Safe access
            })

        self.courses_df = pd.DataFrame(data)

        # Safely update dropdown values with error checking
        try:
            if not self.courses_df.empty and "faculty" in self.courses_df.columns:
                faculties = ["All"] + sorted(self.courses_df["faculty"].unique().tolist())
                departments = ["All"] + sorted(self.courses_df["department"].unique().tolist())
                campuses = ["All"] + sorted(self.courses_df["campus"].unique().tolist())
            else:
                # Fallback if columns don't exist
                faculties = ["All", "Unknown Faculty"]
                departments = ["All", "Unknown Department"]
                campuses = ["All", "Main Campus"]

            self.faculty_combo.configure(values=faculties)
            self.department_combo.configure(values=departments)
            self.campus_combo.configure(values=campuses)

            # Find max credit for slider
            if not self.courses_df.empty and "ects" in self.courses_df.columns:
                max_course_credit = int(self.courses_df["ects"].max())
                self.max_scale.configure(to=max_course_credit)
                self.max_credit.set(max_course_credit)
                self.max_label.configure(text=f"{max_course_credit}")

        except Exception as e:
            logger.error(f"Error updating course preview UI: {e}")
            # Set safe defaults
            self.faculty_combo.configure(values=["All"])
            self.department_combo.configure(values=["All"])
            self.campus_combo.configure(values=["All"])

        # Apply filters (shows all courses initially)
        self._apply_filters()

        logger.info(f"Course preview updated with {len(courses)} courses")

    def _on_restrict_changed(self):
        """Handle changes to the restrict checkbox."""
        # Update checkbox color based on new state
        self._update_restrict_checkbox_color()

    def _update_restrict_checkbox_color(self):
        """Update the color of the restrict checkbox based on its state."""
        if self.restrict_var.get():
            # Checked state - use green color
            self.restrict_check.configure(
                text_color=("green", "lightgreen"),
                hover_color=("darkgreen", "green")
            )
        else:
            # Unchecked state - use default color
            self.restrict_check.configure(
                text_color=("red", "lightcoral"),
                hover_color=("darkred", "red")
            )

