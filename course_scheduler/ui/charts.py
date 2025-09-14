"""
Analytics charts and visualizations for schedule data.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from typing import List
import logging

from ..core.models import Schedule

logger = logging.getLogger(__name__)


class ScheduleAnalyticsChart:
    """Live analytics chart for schedule data."""

    CHART_UPDATE_INTERVAL_MS = 2000
    CHART_DIMENSIONS = (10, 6)
    BAR_WIDTH = 0.35

    def __init__(self, parent: tk.Widget, schedules: List[Schedule]):
        self.parent = parent
        self.schedules = schedules

        self.setup_ui()
        self.create_charts()

        # Start real-time updates
        self.refresh_charts()

    def setup_ui(self):
        """Setup the analytics UI."""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title_label = ttk.Label(main_frame, text="Schedule Analytics Dashboard",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))

        # Create notebook for different chart types
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Overview tab
        self.overview_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_tab, text="Overview")

        # Detailed analysis tab
        self.detailed_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.detailed_tab, text="Detailed Analysis")

        # Statistics tab
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="Statistics")

    def create_charts(self):
        """Create all chart visualizations."""
        self.create_overview_charts()
        self.create_detailed_charts()
        self.create_statistics_display()

    def create_overview_charts(self):
        """Create overview charts in the overview tab."""
        # Create matplotlib figure
        self.overview_fig = Figure(figsize=self.CHART_DIMENSIONS, dpi=100)

        # Create subplots
        self.ax1 = self.overview_fig.add_subplot(221)  # Credits comparison
        self.ax2 = self.overview_fig.add_subplot(222)  # Conflicts comparison
        self.ax3 = self.overview_fig.add_subplot(223)  # ECTS distribution
        self.ax4 = self.overview_fig.add_subplot(224)  # Course type distribution

        # Embed in tkinter
        self.overview_canvas = FigureCanvasTkAgg(self.overview_fig, self.overview_tab)
        self.overview_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Control frame
        control_frame = ttk.Frame(self.overview_tab)
        control_frame.pack(fill="x", pady=5)

        ttk.Button(control_frame, text="Refresh",
                  command=self.refresh_charts).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Export PNG",
                  command=self.export_overview).pack(side="left", padx=5)

    def create_detailed_charts(self):
        """Create detailed analysis charts."""
        # Create matplotlib figure for detailed analysis
        self.detailed_fig = Figure(figsize=self.CHART_DIMENSIONS, dpi=100)

        # Create subplots for detailed analysis
        self.ax5 = self.detailed_fig.add_subplot(221)  # Time slot utilization
        self.ax6 = self.detailed_fig.add_subplot(222)  # Day utilization
        self.ax7 = self.detailed_fig.add_subplot(223)  # Faculty distribution
        self.ax8 = self.detailed_fig.add_subplot(224)  # Department distribution

        # Embed in tkinter
        self.detailed_canvas = FigureCanvasTkAgg(self.detailed_fig, self.detailed_tab)
        self.detailed_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Control frame
        detailed_control_frame = ttk.Frame(self.detailed_tab)
        detailed_control_frame.pack(fill="x", pady=5)

        ttk.Button(detailed_control_frame, text="Refresh",
                  command=self.refresh_charts).pack(side="left", padx=5)
        ttk.Button(detailed_control_frame, text="Export PNG",
                  command=self.export_detailed).pack(side="left", padx=5)

    def create_statistics_display(self):
        """Create statistics display."""
        # Statistics text display
        stats_frame = ttk.Frame(self.stats_tab)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ttk.Label(stats_frame, text="Schedule Statistics Summary",
                 font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))

        # Text widget for statistics
        self.stats_text = tk.Text(stats_frame, wrap="word", font=("Consolas", 10))
        stats_scroll = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)

        self.stats_text.pack(side="left", fill="both", expand=True)
        stats_scroll.pack(side="right", fill="y")

        # Refresh button
        ttk.Button(stats_frame, text="Refresh Statistics",
                  command=self.update_statistics).pack(anchor="w", pady=10)

    def refresh_charts(self):
        """Refresh all charts with current data."""
        if not self.schedules:
            return

        try:
            self.update_overview_charts()
            self.update_detailed_charts()
            self.update_statistics()

            # Schedule next update
            self.parent.after(self.CHART_UPDATE_INTERVAL_MS, self.refresh_charts)

        except Exception as e:
            logger.error(f"Error refreshing charts: {e}")

    def update_overview_charts(self):
        """Update overview charts."""
        # Clear existing plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()

        if not self.schedules:
            return

        # Chart 1: Credits comparison
        schedule_nums = list(range(1, len(self.schedules) + 1))
        credits = [schedule.total_ects for schedule in self.schedules]

        self.ax1.bar(schedule_nums, credits, color='skyblue', alpha=0.7)
        self.ax1.set_title('Total ECTS per Schedule')
        self.ax1.set_xlabel('Schedule #')
        self.ax1.set_ylabel('ECTS Credits')
        self.ax1.grid(True, alpha=0.3)

        # Chart 2: Conflicts comparison
        conflicts = [schedule.conflict_cost for schedule in self.schedules]
        colors = ['red' if c > 0 else 'green' for c in conflicts]

        self.ax2.bar(schedule_nums, conflicts, color=colors, alpha=0.7)
        self.ax2.set_title('Conflict Cost per Schedule')
        self.ax2.set_xlabel('Schedule #')
        self.ax2.set_ylabel('Conflict Cost')
        self.ax2.grid(True, alpha=0.3)

        # Chart 3: ECTS distribution
        self.ax3.hist(credits, bins=max(1, len(set(credits))), color='lightgreen', alpha=0.7, edgecolor='black')
        self.ax3.set_title('ECTS Distribution')
        self.ax3.set_xlabel('Total ECTS')
        self.ax3.set_ylabel('Frequency')
        self.ax3.grid(True, alpha=0.3)

        # Chart 4: Course type distribution (for first schedule)
        if self.schedules:
            first_schedule = self.schedules[0]
            type_counts = {}
            for course in first_schedule.courses:
                course_type = course.course_type.value
                type_counts[course_type] = type_counts.get(course_type, 0) + 1

            if type_counts:
                types = list(type_counts.keys())
                counts = list(type_counts.values())
                colors = ['lightcoral', 'lightblue', 'lightgreen'][:len(types)]

                self.ax4.pie(counts, labels=types, colors=colors, autopct='%1.1f%%', startangle=90)
                self.ax4.set_title('Course Type Distribution\n(First Schedule)')

        # Adjust layout and redraw
        self.overview_fig.tight_layout()
        self.overview_canvas.draw()

    def update_detailed_charts(self):
        """Update detailed analysis charts."""
        # Clear existing plots
        self.ax5.clear()
        self.ax6.clear()
        self.ax7.clear()
        self.ax8.clear()

        if not self.schedules:
            return

        # Use first schedule for detailed analysis
        first_schedule = self.schedules[0]

        # Chart 5: Time slot utilization
        slot_usage = {}
        for course in first_schedule.courses:
            for day, hour in course.schedule:
                slot_usage[hour] = slot_usage.get(hour, 0) + 1

        if slot_usage:
            hours = sorted(slot_usage.keys())
            usage = [slot_usage[h] for h in hours]

            self.ax5.bar(hours, usage, color='orange', alpha=0.7)
            self.ax5.set_title('Time Slot Utilization')
            self.ax5.set_xlabel('Hour')
            self.ax5.set_ylabel('Number of Courses')
            self.ax5.grid(True, alpha=0.3)

        # Chart 6: Day utilization
        day_usage = {}
        for course in first_schedule.courses:
            for day, hour in course.schedule:
                day_usage[day] = day_usage.get(day, 0) + 1

        if day_usage:
            days = ['M', 'T', 'W', 'Th', 'F', 'Sa', 'Su']
            usage = [day_usage.get(day, 0) for day in days]

            self.ax6.bar(days, usage, color='purple', alpha=0.7)
            self.ax6.set_title('Day Utilization')
            self.ax6.set_xlabel('Day')
            self.ax6.set_ylabel('Number of Courses')
            self.ax6.grid(True, alpha=0.3)

        # Chart 7: Faculty distribution
        faculty_counts = {}
        for course in first_schedule.courses:
            faculty = course.faculty
            faculty_counts[faculty] = faculty_counts.get(faculty, 0) + 1

        if faculty_counts:
            # Show top 5 faculties
            sorted_faculties = sorted(faculty_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            faculties = [f[0][:15] + '...' if len(f[0]) > 15 else f[0] for f, _ in sorted_faculties]
            counts = [c for _, c in sorted_faculties]

            self.ax7.barh(faculties, counts, color='teal', alpha=0.7)
            self.ax7.set_title('Top 5 Faculties')
            self.ax7.set_xlabel('Number of Courses')
            self.ax7.grid(True, alpha=0.3)

        # Chart 8: Department distribution
        dept_counts = {}
        for course in first_schedule.courses:
            dept = course.department
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        if dept_counts:
            # Show top 5 departments
            sorted_depts = sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            depts = [d[0][:15] + '...' if len(d[0]) > 15 else d[0] for d, _ in sorted_depts]
            counts = [c for _, c in sorted_depts]

            self.ax8.barh(depts, counts, color='brown', alpha=0.7)
            self.ax8.set_title('Top 5 Departments')
            self.ax8.set_xlabel('Number of Courses')
            self.ax8.grid(True, alpha=0.3)

        # Adjust layout and redraw
        self.detailed_fig.tight_layout()
        self.detailed_canvas.draw()

    def update_statistics(self):
        """Update statistics display."""
        if not self.schedules:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "No schedule data available.")
            return

        # Generate comprehensive statistics
        stats = self.generate_statistics()

        # Update text display
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)

    def generate_statistics(self) -> str:
        """Generate comprehensive statistics text."""
        if not self.schedules:
            return "No data available."

        lines = []
        lines.append("=" * 60)
        lines.append("SCHEDULE ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append("")

        # Overall statistics
        lines.append("OVERALL STATISTICS:")
        lines.append(f"  Total Schedules Generated: {len(self.schedules)}")
        lines.append(f"  Schedules with Conflicts: {sum(1 for s in self.schedules if s.has_conflicts())}")
        lines.append(f"  Conflict-free Schedules: {sum(1 for s in self.schedules if not s.has_conflicts())}")
        lines.append("")

        # ECTS analysis
        ects_values = [s.total_ects for s in self.schedules]
        lines.append("ECTS ANALYSIS:")
        lines.append(f"  Average ECTS: {np.mean(ects_values):.1f}")
        lines.append(f"  Min ECTS: {min(ects_values)}")
        lines.append(f"  Max ECTS: {max(ects_values)}")
        lines.append(f"  ECTS Standard Deviation: {np.std(ects_values):.1f}")
        lines.append("")

        # Conflict analysis
        conflict_values = [s.conflict_cost for s in self.schedules]
        lines.append("CONFLICT ANALYSIS:")
        lines.append(f"  Average Conflict Cost: {np.mean(conflict_values):.1f}")
        lines.append(f"  Max Conflict Cost: {max(conflict_values)}")
        lines.append(f"  Total Conflicts Across All Schedules: {sum(conflict_values)}")
        lines.append("")

        # Detailed schedule breakdown
        lines.append("SCHEDULE BREAKDOWN:")
        for i, schedule in enumerate(self.schedules, 1):
            lines.append(f"  Schedule {i}:")
            lines.append(f"    ECTS: {schedule.total_ects}")
            lines.append(f"    Conflicts: {schedule.conflict_cost}")
            lines.append(f"    Courses: {len(schedule.courses)}")

            # Course type breakdown
            type_counts = {}
            for course in schedule.courses:
                course_type = course.course_type.value
                type_counts[course_type] = type_counts.get(course_type, 0) + 1

            type_breakdown = ", ".join(f"{t}: {c}" for t, c in type_counts.items())
            lines.append(f"    Types: {type_breakdown}")
            lines.append("")

        return "\n".join(lines)

    def export_overview(self):
        """Export overview charts as PNG."""
        try:
            filename = "schedule_overview.png"
            self.overview_fig.savefig(filename, dpi=300, bbox_inches='tight')
            logger.info(f"Overview charts exported to {filename}")
        except Exception as e:
            logger.error(f"Failed to export overview: {e}")

    def export_detailed(self):
        """Export detailed charts as PNG."""
        try:
            filename = "schedule_detailed.png"
            self.detailed_fig.savefig(filename, dpi=300, bbox_inches='tight')
            logger.info(f"Detailed charts exported to {filename}")
        except Exception as e:
            logger.error(f"Failed to export detailed charts: {e}")


class SimpleBarChart:
    """Simple bar chart widget for basic visualizations."""

    def __init__(self, parent: tk.Widget, title: str = "Chart"):
        self.parent = parent
        self.title = title

        # Create figure
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_data(self, labels: List[str], values: List[float],
                   xlabel: str = "", ylabel: str = "", color: str = "skyblue"):
        """Update chart with new data."""
        self.ax.clear()

        self.ax.bar(labels, values, color=color, alpha=0.7)
        self.ax.set_title(self.title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True, alpha=0.3)

        # Rotate labels if there are many
        if len(labels) > 5:
            self.ax.tick_params(axis='x', rotation=45)

        self.fig.tight_layout()
        self.canvas.draw()
