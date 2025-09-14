"""
Enhanced schedule visualization with weekly calendar view.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import numpy as np
from typing import List, Dict, Tuple
from ..core.models import Course, Schedule

class WeeklyScheduleView:
    """Interactive weekly schedule calendar view."""

    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.fig = None
        self.canvas = None
        self.courses = []

        # Time slots and days
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.day_codes = ['M', 'T', 'W', 'Th', 'F', 'Sa', 'Su']
        self.time_slots = list(range(1, 13))  # 1-12 time slots

        # Colors for different course types
        self.colors = {
            'lecture': '#4CAF50',    # Green
            'ps': '#2196F3',        # Blue
            'lab': '#FF9800',       # Orange
            'default': '#9E9E9E'    # Gray
        }

        self.setup_ui()

    def setup_ui(self):
        """Setup the weekly calendar UI."""
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        self.fig.patch.set_facecolor('white')

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial empty calendar
        self.draw_empty_calendar()

    def draw_empty_calendar(self):
        """Draw empty calendar grid."""
        self.ax.clear()

        # Set up the grid
        self.ax.set_xlim(0, 7)
        self.ax.set_ylim(0, 12)

        # Draw grid lines
        for i in range(8):
            self.ax.axvline(x=i, color='lightgray', linewidth=0.5)
        for i in range(13):
            self.ax.axhline(y=i, color='lightgray', linewidth=0.5)

        # Set labels
        self.ax.set_xticks(np.arange(0.5, 7.5))
        self.ax.set_xticklabels(self.days, rotation=45, ha='right')

        self.ax.set_yticks(np.arange(0.5, 12.5))
        self.ax.set_yticklabels([f'Slot {i}' for i in range(12, 0, -1)])

        # Style
        self.ax.set_title('Weekly Schedule Overview', fontsize=16, fontweight='bold', pad=20)
        self.ax.set_xlabel('Days', fontsize=12)
        self.ax.set_ylabel('Time Slots', fontsize=12)

        # Remove spines
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        self.canvas.draw()

    def update_schedule(self, courses: List[Course]):
        """Update the calendar with course schedule."""
        self.courses = courses
        self.draw_empty_calendar()

        if not courses:
            return

        # Group courses by time slot for conflict detection
        slot_courses = {}

        for course in courses:
            for day_code, time_slot in course.schedule:
                key = (day_code, time_slot)
                if key not in slot_courses:
                    slot_courses[key] = []
                slot_courses[key].append(course)

        # Draw courses
        for (day_code, time_slot), course_list in slot_courses.items():
            if day_code in self.day_codes:
                day_idx = self.day_codes.index(day_code)
                self.draw_course_block(day_idx, time_slot, course_list)

        # Add legend
        self.add_legend()

        self.canvas.draw()

    def draw_course_block(self, day_idx: int, time_slot: int, courses: List[Course]):
        """Draw a course block on the calendar."""
        # Calculate position (invert y-axis for proper display)
        x = day_idx
        y = 12 - time_slot
        width = 1
        height = 1

        # Handle conflicts (multiple courses in same slot)
        if len(courses) > 1:
            # Split the cell for conflicts
            cell_height = height / len(courses)
            for i, course in enumerate(courses):
                y_pos = y + (i * cell_height)
                self.draw_single_course(x, y_pos, width, cell_height, course, is_conflict=True)
        else:
            self.draw_single_course(x, y, width, height, courses[0], is_conflict=False)

    def draw_single_course(self, x: float, y: float, width: float, height: float,
                          course: Course, is_conflict: bool):
        """Draw a single course rectangle."""
        # Choose color based on course type
        color = self.colors.get(course.course_type.value, self.colors['default'])

        # Make conflicted courses more transparent
        alpha = 0.6 if is_conflict else 0.8

        # Draw rectangle
        rect = Rectangle((x, y), width, height,
                        facecolor=color, alpha=alpha,
                        edgecolor='black', linewidth=1)
        self.ax.add_patch(rect)

        # Add course text
        font_size = 8 if is_conflict else 10

        # Course code (top line)
        self.ax.text(x + width/2, y + height*0.7, course.code,
                    ha='center', va='center', fontsize=font_size,
                    fontweight='bold', color='white')

        # Course name (bottom line, truncated)
        name = course.name[:15] + '...' if len(course.name) > 15 else course.name
        self.ax.text(x + width/2, y + height*0.3, name,
                    ha='center', va='center', fontsize=font_size-1,
                    color='white', style='italic')

        # Add conflict indicator
        if is_conflict:
            self.ax.text(x + width*0.9, y + height*0.9, '⚠',
                        ha='center', va='center', fontsize=12, color='red')

    def add_legend(self):
        """Add legend for course types."""
        legend_elements = []
        for course_type, color in self.colors.items():
            if course_type != 'default':
                legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=color,
                                                   label=course_type.capitalize()))

        if legend_elements:
            self.ax.legend(handles=legend_elements, loc='upper right',
                          bbox_to_anchor=(1.15, 1))

    def export_schedule_image(self, filename: str):
        """Export the schedule as an image."""
        self.fig.savefig(filename, dpi=300, bbox_inches='tight',
                        facecolor='white', edgecolor='none')

    def get_statistics(self) -> Dict:
        """Get schedule statistics."""
        if not self.courses:
            return {}

        stats = {
            'total_courses': len(self.courses),
            'total_ects': sum(c.ects for c in self.courses),
            'conflicts': self.get_conflicts(),
            'daily_load': self.get_daily_load(),
            'course_types': self.get_course_type_distribution()
        }

        return stats

    def get_conflicts(self) -> int:
        """Count scheduling conflicts."""
        slot_usage = {}
        for course in self.courses:
            for day_code, time_slot in course.schedule:
                key = (day_code, time_slot)
                slot_usage[key] = slot_usage.get(key, 0) + 1

        return sum(1 for count in slot_usage.values() if count > 1)

    def get_daily_load(self) -> Dict[str, int]:
        """Get course load per day."""
        daily_load = {day: 0 for day in self.day_codes}

        for course in self.courses:
            for day_code, _ in course.schedule:
                if day_code in daily_load:
                    daily_load[day_code] += 1

        return daily_load

    def get_course_type_distribution(self) -> Dict[str, int]:
        """Get distribution of course types."""
        distribution = {}
        for course in self.courses:
            course_type = course.course_type.value
            distribution[course_type] = distribution.get(course_type, 0) + 1

        return distribution
