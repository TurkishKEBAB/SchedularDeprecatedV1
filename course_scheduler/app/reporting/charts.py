"""
Analytics charts for course schedules.

This module provides interactive chart visualizations for analyzing
and comparing course schedules.
"""
import tkinter as tk
from typing import List, Dict, Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ..data.models import Schedule
from ..config import CHART_UPDATE_INTERVAL_MS, CHART_DIMENSIONS, BAR_WIDTH


class ScheduleAnalyticsChart:
    """
    Interactive analytics chart for visualizing schedule metrics.

    This chart shows a real-time comparison of multiple schedules,
    displaying credit totals and conflict counts in a grouped bar chart.
    """

    def __init__(self, master_window: tk.Toplevel, scheduler_reference: Any):
        """
        Initialize the analytics chart.

        Args:
            master_window: Parent Tkinter window
            scheduler_reference: Reference to the scheduler GUI that has access to schedules
        """
        self.master_window = master_window
        self.scheduler_reference = scheduler_reference

        # Initialize matplotlib figure and canvas
        self.figure, self.axes = plt.subplots(figsize=CHART_DIMENSIONS)
        self.canvas = FigureCanvasTkAgg(self.figure, master=master_window)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Start real-time updates
        self.refresh_chart()

    def refresh_chart(self):
        """
        Update chart with latest schedule data.
        """
        self.axes.clear()
        self._plot_schedule_data()
        self.canvas.draw()

        # Schedule next update
        self.master_window.after(CHART_UPDATE_INTERVAL_MS, self.refresh_chart)

    def _plot_schedule_data(self):
        """
        Plot schedule analytics if data is available.
        """
        schedules = getattr(self.scheduler_reference, "final_schedules", None)
        if not schedules:
            self._draw_empty_state()
            return

        schedule_indices = list(range(1, len(schedules) + 1))
        credit_totals = [self._calculate_total_credits(schedule) for schedule in schedules]
        conflict_counts = [schedule.conflict_count for schedule in schedules]

        # Plot credit totals and conflicts as grouped bars
        self._create_grouped_bars(schedule_indices, credit_totals, conflict_counts)
        self._set_chart_labels()

    def _calculate_total_credits(self, schedule):
        """
        Calculate total ECTS credits for a schedule.

        Args:
            schedule: Schedule to analyze

        Returns:
            Total ECTS credits
        """
        if hasattr(schedule, 'total_credits'):
            return schedule.total_credits
        else:
            # Fallback for legacy data format (list of dictionaries)
            return sum(course.get("ECTS", 0) for course in schedule)

    def _create_grouped_bars(self, indices, credits, conflicts):
        """
        Create grouped bar chart showing credits and conflicts.

        Args:
            indices: List of schedule indices
            credits: List of credit totals
            conflicts: List of conflict counts
        """
        offset = BAR_WIDTH / 2
        self.axes.bar([x - offset for x in indices], credits,
                     BAR_WIDTH, label="Total Credits")
        self.axes.bar([x + offset for x in indices], conflicts,
                     BAR_WIDTH, label="Conflict Count")

        # Add data labels above bars
        for i, (credit, conflict) in enumerate(zip(credits, conflicts)):
            idx = i + 1  # Schedule number
            self.axes.text(idx - offset, credit + 1, str(credit),
                          ha='center', va='bottom', fontsize=9)
            self.axes.text(idx + offset, conflict + 1, str(conflict),
                          ha='center', va='bottom', fontsize=9)

    def _set_chart_labels(self):
        """
        Set chart title, labels and legend.
        """
        self.axes.set_xlabel("Schedule Number")
        self.axes.set_ylabel("Value")
        self.axes.set_title("Schedule Comparison")
        self.axes.legend()
        self.axes.grid(True, linestyle='--', alpha=0.3)

    def _draw_empty_state(self):
        """
        Display a message when no schedules are available.
        """
        self.axes.text(0.5, 0.5, "No schedules available.\nRun scheduling process first.",
                      ha='center', va='center', fontsize=12,
                      transform=self.axes.transAxes)
        self.axes.set_axis_off()


class DayDistributionChart:
    """
    Chart showing the distribution of courses across days of the week.
    """

    def __init__(self, master_window: tk.Toplevel, schedule: Schedule):
        """
        Initialize the day distribution chart.

        Args:
            master_window: Parent Tkinter window
            schedule: Schedule to visualize
        """
        self.master_window = master_window
        self.schedule = schedule

        # Initialize matplotlib figure and canvas
        self.figure, self.axes = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.figure, master=master_window)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Plot data
        self._plot_day_distribution()

    def _plot_day_distribution(self):
        """Plot course distribution by day of week."""
        # Count courses per day
        days = ["M", "T", "W", "Th", "F", "Sa", "Su"]
        day_counts = {day: 0 for day in days}

        # Count how many courses have sessions on each day
        for course in self.schedule.courses:
            day_set = set(day for day, _ in course.schedule)
            for day in day_set:
                if day in day_counts:
                    day_counts[day] += 1

        # Create bar chart
        days_with_data = [day for day in days if day_counts[day] > 0]
        counts = [day_counts[day] for day in days_with_data]

        colors = plt.cm.viridis(range(len(days_with_data)))
        bars = self.axes.bar(days_with_data, counts, color=colors)

        # Add data labels
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            self.axes.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                          str(count), ha='center', va='bottom')

        # Add labels and title
        self.axes.set_xlabel("Day of Week")
        self.axes.set_ylabel("Number of Courses")
        self.axes.set_title("Course Distribution by Day")
        self.axes.grid(axis='y', linestyle='--', alpha=0.3)

        # Add schedule info in the corner
        self.axes.text(0.95, 0.95,
                      f"Total Credits: {self.schedule.total_credits}\nConflicts: {self.schedule.conflict_count}",
                      transform=self.axes.transAxes,
                      horizontalalignment='right',
                      verticalalignment='top',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7))


def create_course_type_chart(schedule: Schedule, master: tk.Toplevel) -> FigureCanvasTkAgg:
    """
    Create a pie chart showing the distribution of course types.

    Args:
        schedule: Schedule to analyze
        master: Parent Tkinter window

    Returns:
        FigureCanvasTkAgg object
    """
    # Count courses by type
    course_types = {"lecture": 0, "ps": 0, "lab": 0}
    for course in schedule.courses:
        if course.course_type in course_types:
            course_types[course.course_type] += 1

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(5, 4))

    # Create pie chart
    labels = [f"{key.capitalize()} ({value})" for key, value in course_types.items() if value > 0]
    sizes = [value for value in course_types.values() if value > 0]
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    explode = (0.1, 0, 0)  # explode first slice (lectures)

    if sizes:
        ax.pie(sizes, explode=explode[:len(sizes)], labels=labels, colors=colors[:len(sizes)],
              autopct='%1.1f%%', shadow=True, startangle=90)
    else:
        ax.text(0.5, 0.5, "No courses available", ha='center', va='center')

    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    ax.set_title("Course Types Distribution")

    # Create canvas
    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    return canvas
