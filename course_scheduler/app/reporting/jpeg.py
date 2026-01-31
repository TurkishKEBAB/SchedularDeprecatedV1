"""
JPEG reporting utilities for schedule visualization.

This module provides functions for exporting schedules as visual
JPEG images with professional formatting.
"""
import logging
from typing import List
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg
import os

from ..data.models import Schedule

logger = logging.getLogger(__name__)

# Time slot mapping
TIME_SLOTS = {
    1: "08:30-09:20",
    2: "09:30-10:20",
    3: "10:30-11:20",
    4: "11:30-12:20",
    5: "12:30-13:20",
    6: "13:30-14:20",
    7: "14:30-15:20",
    8: "15:30-16:20",
    9: "16:30-17:20",
    10: "17:30-18:20",
    11: "18:30-19:20",
    12: "19:30-20:20"
}

DAYS = ["M", "T", "W", "Th", "F", "Sa", "Su"]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def save_schedules_as_jpegs(schedules: List[Schedule], output_dir: str) -> bool:
    """
    Save multiple schedules as JPEG images.

    Args:
        schedules: List of Schedule objects to export
        output_dir: Directory where JPEG files will be saved

    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(output_dir, exist_ok=True)

        for i, schedule in enumerate(schedules, 1):
            filename = f"schedule_{i}.jpg"
            filepath = os.path.join(output_dir, filename)
            save_schedule_as_jpeg(schedule, filepath, f"Schedule {i}")

        logger.info(f"Successfully exported {len(schedules)} schedules as JPEG to: {output_dir}")
        return True

    except Exception as e:
        logger.error(f"Error exporting schedules to JPEG: {e}")
        return False


def save_schedule_as_jpeg(schedule: Schedule, output_path: str, title: str = "Course Schedule") -> bool:
    """
    Save a single schedule as JPEG image.

    Args:
        schedule: Schedule object to export
        output_path: Path where JPEG will be saved
        title: Title for the schedule

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(14, 10))

        # Set up the grid
        num_days = len(DAYS)
        num_slots = len(TIME_SLOTS)

        # Draw grid
        for i in range(num_days + 1):
            ax.axvline(x=i, color='black', linewidth=1)
        for i in range(num_slots + 1):
            ax.axhline(y=i, color='black', linewidth=1)

        # Set up the schedule grid
        course_colors = plt.cm.Set3(range(len(schedule.courses)))

        # Create a mapping of courses to colors
        course_color_map = {}
        for idx, course in enumerate(schedule.courses):
            course_color_map[course.code] = course_colors[idx % len(course_colors)]

        # Fill in the courses
        for course in schedule.courses:
            color = course_color_map[course.code]

            for day_code, slot in course.schedule:
                if day_code in DAYS and slot in TIME_SLOTS:
                    day_idx = DAYS.index(day_code)
                    slot_idx = slot - 1  # Convert to 0-based index

                    # Draw rectangle for this time slot
                    rect = patches.Rectangle(
                        (day_idx, num_slots - slot_idx - 1), 1, 1,
                        linewidth=1, edgecolor='black',
                        facecolor=color, alpha=0.7
                    )
                    ax.add_patch(rect)

                    # Add course code text
                    ax.text(
                        day_idx + 0.5, num_slots - slot_idx - 0.5,
                        course.code,
                        ha='center', va='center',
                        fontsize=8, fontweight='bold',
                        wrap=True
                    )

        # Set labels
        ax.set_xlim(0, num_days)
        ax.set_ylim(0, num_slots)

        # Day labels
        ax.set_xticks([i + 0.5 for i in range(num_days)])
        ax.set_xticklabels(DAY_NAMES, fontsize=10, fontweight='bold')

        # Time labels
        ax.set_yticks([i + 0.5 for i in range(num_slots)])
        time_labels = [TIME_SLOTS[i+1] for i in range(num_slots)]
        ax.set_yticklabels(time_labels[::-1], fontsize=9)  # Reverse for top-down display

        # Title and info
        plt.title(title, fontsize=16, fontweight='bold', pad=20)

        # Add schedule info at the bottom
        info_text = f"Total Credits: {schedule.total_credits} | "
        info_text += f"Courses: {len(schedule.courses)} | "
        info_text += f"Conflicts: {schedule.conflict_count}"

        plt.figtext(0.5, 0.02, info_text, ha='center', fontsize=12,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))

        # Course legend
        if len(schedule.courses) <= 15:  # Only show legend if not too many courses
            legend_elements = []
            for course in schedule.courses:
                color = course_color_map[course.code]
                legend_elements.append(
                    patches.Patch(color=color, label=f"{course.code}: {course.name[:20]}...")
                )

            ax.legend(handles=legend_elements, loc='center left',
                     bbox_to_anchor=(1, 0.5), fontsize=8)

        # Remove axis spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()

        logger.info(f"Successfully exported schedule as JPEG: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error exporting schedule to JPEG: {e}")
        return False
