"""
Detailed schedule report with interactive grid view and course information panel.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict
import logging

from ..core.models import Schedule, Course

logger = logging.getLogger(__name__)


class DetailedScheduleReport:
    """Interactive detailed schedule report with navigation and course info."""

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    HOURS = range(1, 13)  # 8:30 AM to 8:20 PM
    CELL_DIMENSIONS = {"width": 100, "height": 50}
    COURSE_COLORS = {
        "lecture": "#FFE5E5",  # Light red
        "ps": "#E5FFE5",       # Light green
        "lab": "#E5E5FF"       # Light blue
    }

    TIME_LABELS = {
        1: "08:30-09:20", 2: "09:30-10:20", 3: "10:30-11:20", 4: "11:30-12:20",
        5: "12:30-13:20", 6: "13:30-14:20", 7: "14:30-15:20", 8: "15:30-16:20",
        9: "16:30-17:20", 10: "17:30-18:20", 11: "18:30-19:20", 12: "19:30-20:20"
    }

    def __init__(self, parent: tk.Widget, schedules: List[Schedule]):
        self.parent = parent
        self.schedules = schedules
        self.current_index = 0

        self.setup_window()
        self.create_navigation()
        self.create_main_layout()
        self.create_schedule_grid()
        self.create_info_panel()
        self.render_current_schedule()

        logger.info(f"Detailed schedule report opened with {len(schedules)} schedules")

    def setup_window(self):
        """Setup the main report window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Detailed Schedule Report")
        self.window.geometry("1000x700")
        self.window.transient(self.parent)

        # Main container
        self.main_container = ttk.Frame(self.window)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

    def create_navigation(self):
        """Create navigation controls for browsing schedules."""
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(fill="x", pady=(0, 10))

        # Navigation controls
        ttk.Button(nav_frame, text="◀ Previous",
                  command=self.show_previous).pack(side="left")

        self.schedule_indicator = ttk.Label(nav_frame, text="Schedule 1",
                                          font=("Arial", 12, "bold"))
        self.schedule_indicator.pack(side="left", padx=20)

        ttk.Button(nav_frame, text="Next ▶",
                  command=self.show_next).pack(side="left")

        # Schedule summary
        self.summary_label = ttk.Label(nav_frame, text="", font=("Arial", 10))
        self.summary_label.pack(side="right")

        # Export buttons
        export_frame = ttk.Frame(nav_frame)
        export_frame.pack(side="right", padx=(0, 20))

        ttk.Button(export_frame, text="📄 Export Current",
                  command=self.export_current).pack(side="left", padx=2)
        ttk.Button(export_frame, text="📊 Export All",
                  command=self.export_all).pack(side="left", padx=2)

    def create_main_layout(self):
        """Create the main layout with grid and info panel."""
        # Create paned window for resizable layout
        self.paned_window = ttk.PanedWindow(self.main_container, orient="horizontal")
        self.paned_window.pack(fill="both", expand=True)

        # Left side: Schedule grid
        self.grid_frame = ttk.LabelFrame(self.paned_window, text="Weekly Schedule", padding=10)
        self.paned_window.add(self.grid_frame, weight=3)

        # Right side: Course information
        self.info_frame = ttk.LabelFrame(self.paned_window, text="Course Information", padding=10)
        self.paned_window.add(self.info_frame, weight=1)

    def create_schedule_grid(self):
        """Create the interactive schedule grid."""
        # Create scrollable frame for the grid
        grid_canvas = tk.Canvas(self.grid_frame)
        grid_scrollbar = ttk.Scrollbar(self.grid_frame, orient="vertical", command=grid_canvas.yview)
        self.scrollable_grid = ttk.Frame(grid_canvas)

        grid_canvas.configure(yscrollcommand=grid_scrollbar.set)
        grid_canvas.create_window((0, 0), window=self.scrollable_grid, anchor="nw")

        # Pack canvas and scrollbar
        grid_canvas.pack(side="left", fill="both", expand=True)
        grid_scrollbar.pack(side="right", fill="y")

        # Update scroll region when frame changes
        self.scrollable_grid.bind("<Configure>",
                                 lambda e: grid_canvas.configure(scrollregion=grid_canvas.bbox("all")))

        # Create time labels (header row)
        ttk.Label(self.scrollable_grid, text="Time", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=1, pady=1, sticky="nsew")

        for col, day in enumerate(self.DAYS, 1):
            ttk.Label(self.scrollable_grid, text=day, font=("Arial", 10, "bold")).grid(
                row=0, column=col, padx=1, pady=1, sticky="nsew")

        # Create the grid cells
        self.grid_cells = {}
        for row, hour in enumerate(self.HOURS, 1):
            # Time label
            time_label = self.TIME_LABELS.get(hour, f"{hour}:00")
            ttk.Label(self.scrollable_grid, text=time_label, font=("Arial", 9)).grid(
                row=row, column=0, padx=1, pady=1, sticky="nsew")

            # Day cells
            for col, day in enumerate(self.DAYS, 1):
                cell_frame = tk.Frame(self.scrollable_grid,
                                    width=self.CELL_DIMENSIONS["width"],
                                    height=self.CELL_DIMENSIONS["height"],
                                    relief="solid", borderwidth=1, bg="white")
                cell_frame.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
                cell_frame.grid_propagate(False)

                # Store cell reference
                day_code = self.get_day_code(day)
                self.grid_cells[(day_code, hour)] = cell_frame

        # Configure grid weights
        for i in range(len(self.DAYS) + 1):
            self.scrollable_grid.columnconfigure(i, weight=1)

    def create_info_panel(self):
        """Create the course information panel."""
        # Welcome message
        self.info_content = ttk.Frame(self.info_frame)
        self.info_content.pack(fill="both", expand=True)

        # Course code header
        self.course_header = ttk.Label(self.info_content, text="Click a course to view details",
                                     font=("Arial", 12, "bold"), anchor="center")
        self.course_header.pack(fill="x", pady=(0, 10))

        # Details text area
        details_frame = ttk.Frame(self.info_content)
        details_frame.pack(fill="both", expand=True)

        self.details_text = tk.Text(details_frame, wrap="word", font=("Arial", 10),
                                  height=10, state="disabled")
        details_scroll = ttk.Scrollbar(details_frame, orient="vertical",
                                     command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)

        self.details_text.pack(side="left", fill="both", expand=True)
        details_scroll.pack(side="right", fill="y")

        # Related courses section
        related_frame = ttk.LabelFrame(self.info_content, text="Related Sections", padding=5)
        related_frame.pack(fill="x", pady=(10, 0))

        self.related_listbox = tk.Listbox(related_frame, height=4, font=("Arial", 9))
        self.related_listbox.pack(fill="x")
        self.related_listbox.bind("<<ListboxSelect>>", self.on_related_select)

    def get_day_code(self, day_name: str) -> str:
        """Convert full day name to day code."""
        day_mapping = {
            "Monday": "M", "Tuesday": "T", "Wednesday": "W",
            "Thursday": "Th", "Friday": "F", "Saturday": "Sa", "Sunday": "Su"
        }
        return day_mapping.get(day_name, day_name[0])

    def show_previous(self):
        """Show the previous schedule."""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def show_next(self):
        """Show the next schedule."""
        if self.current_index < len(self.schedules) - 1:
            self.current_index += 1
            self.update_display()

    def update_display(self):
        """Update the display for current schedule."""
        current_schedule = self.schedules[self.current_index]

        # Update indicators
        self.schedule_indicator.config(text=f"Schedule {self.current_index + 1} of {len(self.schedules)}")
        self.summary_label.config(text=f"ECTS: {current_schedule.total_ects} | "
                                      f"Conflicts: {current_schedule.conflict_cost} | "
                                      f"Courses: {len(current_schedule.courses)}")

        # Re-render the schedule
        self.render_current_schedule()

        # Clear course info
        self.clear_course_info()

    def render_current_schedule(self):
        """Render the current schedule in the grid."""
        # Clear all cells
        for cell_frame in self.grid_cells.values():
            for widget in cell_frame.winfo_children():
                widget.destroy()
            cell_frame.config(bg="white")

        if not self.schedules:
            return

        current_schedule = self.schedules[self.current_index]

        # Place courses in grid
        for course in current_schedule.courses:
            for day, hour in course.schedule:
                cell_frame = self.grid_cells.get((day, hour))
                if cell_frame:
                    self.add_course_to_cell(cell_frame, course)

    def add_course_to_cell(self, cell_frame: tk.Frame, course: Course):
        """Add a course to a grid cell."""
        # Set cell background color
        bg_color = self.COURSE_COLORS.get(course.course_type.value, "white")
        cell_frame.config(bg=bg_color)

        # Create course label
        course_label = tk.Label(cell_frame, text=course.code,
                              bg=bg_color, font=("Arial", 8, "bold"),
                              cursor="hand2", anchor="center", wraplength=80)
        course_label.pack(fill="both", expand=True)

        # Bind click event
        course_label.bind("<Button-1>", lambda e: self.on_course_click(course))

        # Tooltip on hover
        self.create_tooltip(course_label, f"{course.name}\nInstructor: {course.teacher}")

    def create_tooltip(self, widget: tk.Widget, text: str):
        """Create a simple tooltip for a widget."""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(tooltip, text=text, background="lightyellow",
                           font=("Arial", 9), relief="solid", borderwidth=1)
            label.pack()

            def hide_tooltip():
                tooltip.destroy()

            tooltip.after(3000, hide_tooltip)  # Auto-hide after 3 seconds

        widget.bind("<Enter>", show_tooltip)

    def on_course_click(self, course: Course):
        """Handle course selection."""
        self.display_course_info(course)
        self.highlight_course(course)
        self.show_related_courses(course)

    def display_course_info(self, course: Course):
        """Display detailed course information."""
        # Update header
        self.course_header.config(text=f"{course.code} - {course.course_type.value.upper()}")

        # Build detailed information
        details = [
            f"Course Name: {course.name}",
            f"Course Code: {course.code}",
            f"Main Code: {course.main_code}",
            f"ECTS Credits: {course.ects}",
            f"Course Type: {course.course_type.value.title()}",
            f"Instructor: {course.teacher}",
            f"Faculty: {course.faculty}",
            f"Department: {course.department}",
            f"Campus: {course.campus}",
            "",
            "Schedule:",
        ]

        # Add schedule details
        for day, hour in course.schedule:
            time_label = self.TIME_LABELS.get(hour, f"{hour}:00")
            day_full = next((d for d in self.DAYS if self.get_day_code(d) == day), day)
            details.append(f"  {day_full} {time_label}")

        # Update text display
        self.details_text.config(state="normal")
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, "\n".join(details))
        self.details_text.config(state="disabled")

    def highlight_course(self, selected_course: Course):
        """Highlight all instances of the selected course."""
        current_schedule = self.schedules[self.current_index]

        # Reset all highlights
        for cell_frame in self.grid_cells.values():
            for widget in cell_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(relief="flat", borderwidth=0)

        # Highlight selected course instances
        for course in current_schedule.courses:
            if course.main_code == selected_course.main_code:
                for day, hour in course.schedule:
                    cell_frame = self.grid_cells.get((day, hour))
                    if cell_frame:
                        for widget in cell_frame.winfo_children():
                            if isinstance(widget, tk.Label):
                                widget.config(relief="solid", borderwidth=2)

    def show_related_courses(self, selected_course: Course):
        """Show related course sections."""
        current_schedule = self.schedules[self.current_index]

        # Find related courses (same main code)
        related = [c for c in current_schedule.courses if c.main_code == selected_course.main_code]

        # Update related courses listbox
        self.related_listbox.delete(0, tk.END)
        for course in related:
            display_text = f"{course.code} ({course.course_type.value}) - {course.teacher}"
            self.related_listbox.insert(tk.END, display_text)

            # Highlight if this is the selected course
            if course.code == selected_course.code:
                self.related_listbox.selection_set(tk.END)

    def on_related_select(self, event):
        """Handle selection in related courses list."""
        selection = self.related_listbox.curselection()
        if selection:
            index = selection[0]
            current_schedule = self.schedules[self.current_index]

            # Find the selected related course
            selected_main_code = None
            if hasattr(self, '_last_selected_course'):
                selected_main_code = self._last_selected_course.main_code

            if selected_main_code:
                related = [c for c in current_schedule.courses if c.main_code == selected_main_code]
                if index < len(related):
                    self.on_course_click(related[index])

    def clear_course_info(self):
        """Clear the course information panel."""
        self.course_header.config(text="Click a course to view details")
        self.details_text.config(state="normal")
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state="disabled")
        self.related_listbox.delete(0, tk.END)

        # Clear highlights
        for cell_frame in self.grid_cells.values():
            for widget in cell_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(relief="flat", borderwidth=0)

    def export_current(self):
        """Export current schedule as image."""
        try:
            current_schedule = self.schedules[self.current_index]
            from ..core.export import ScheduleExporter

            filename = f"schedule_{self.current_index + 1}.jpg"
            unique_courses = current_schedule.get_unique_courses(self.schedules)
            note = f"Schedule {self.current_index + 1}\n"
            note += f"ECTS: {current_schedule.total_ects}, Conflicts: {current_schedule.conflict_cost}\n"
            note += f"Unique courses: {', '.join(sorted(unique_courses)) if unique_courses else 'None'}"

            ScheduleExporter.save_schedule_as_jpeg(current_schedule, filename, note)
            logger.info(f"Exported current schedule to {filename}")

        except Exception as e:
            logger.error(f"Failed to export current schedule: {e}")

    def export_all(self):
        """Export all schedules."""
        try:
            from ..core.export import ScheduleExporter
            # Note: This would need access to all courses for the selection matrix
            # For now, just export individual schedules
            for i, schedule in enumerate(self.schedules, 1):
                filename = f"detailed_schedule_{i}.jpg"
                unique_courses = schedule.get_unique_courses(self.schedules)
                note = f"Schedule {i}\n"
                note += f"ECTS: {schedule.total_ects}, Conflicts: {schedule.conflict_cost}\n"
                note += f"Unique courses: {', '.join(sorted(unique_courses)) if unique_courses else 'None'}"

                ScheduleExporter.save_schedule_as_jpeg(schedule, filename, note)

            logger.info(f"Exported all {len(self.schedules)} schedules")

        except Exception as e:
            logger.error(f"Failed to export all schedules: {e}")
