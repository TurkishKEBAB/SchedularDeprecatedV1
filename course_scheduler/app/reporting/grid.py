"""
Schedule grid generation and visualization.

This module provides functions for generating schedule grids and visualizing
course schedules in various formats.
"""
from typing import List, Dict, Any, Tuple
from ..data.models import Course, Schedule
from ..utils.schedule_utils import DAY_ORDER, SLOT_TIMES, get_full_day_name, get_short_day_name
import logging

# Set up logging
logger = logging.getLogger(__name__)


def get_schedule_grid_data(schedule: Schedule) -> List[List[str]]:
    """
    Generate a grid representation of a schedule.

    Args:
        schedule: Schedule object to represent as a grid

    Returns:
        List of lists representing the schedule grid, with the first list being the header
    """
    # Use the standardized day codes from schedule_utils.py
    days = DAY_ORDER
    period_times = SLOT_TIMES

    # Create the grid structure
    grid = []
    header = ["Time"] + days
    grid.append(header)

    # Add rows for each period
    for period in range(1, 13):  # 12 periods (slots)
        time_str = period_times.get(period, f"Slot {period}")
        row = [time_str]
        row.extend([""] * len(days))
        grid.append(row)

    # If no courses or no schedule slots, return the empty grid
    if not schedule.courses:
        return grid

    # Count courses with empty schedules for diagnostic purposes
    empty_schedule_count = 0
    processed_course_count = 0

    # Fill in the grid with course information
    for course in schedule.courses:
        processed_course_count += 1
        display_str = course.code

        # If course has no schedule entries, log a warning
        if not course.schedule:
            empty_schedule_count += 1
            raw_schedule = getattr(course, 'raw_schedule', None)
            logger.warning(f"Course {course.code} has empty schedule. Raw schedule: {raw_schedule}")
            continue

        # Loop through each day/period in the course schedule
        for day, period in course.schedule:
            # Make sure day is in our day list
            if day not in days:
                logger.warning(f"Day '{day}' not recognized for course {course.code}. Skipping.")
                continue

            # Make sure period is within range
            if period < 1 or period > 12:
                logger.warning(f"Period {period} out of range for course {course.code}. Skipping.")
                continue

            # Place the course in the grid
            col_index = days.index(day) + 1  # +1 because first column is "Time"
            row_index = period  # Period maps directly to row index since we start at row 1

            # Append the course code to any existing courses in that cell
            if grid[row_index][col_index]:
                grid[row_index][col_index] += "\n" + display_str
            else:
                grid[row_index][col_index] = display_str

    # Log diagnostic information
    if empty_schedule_count > 0:
        logger.warning(f"{empty_schedule_count} out of {processed_course_count} courses have empty schedules")

    return grid


def format_grid_for_terminal(grid: List[List[str]]) -> str:
    """
    Format a schedule grid for terminal display using ASCII art.

    Args:
        grid: Grid data from get_schedule_grid_data

    Returns:
        Formatted string for terminal display
    """
    from tabulate import tabulate

    headers = grid[0]
    data_rows = grid[1:]

    return tabulate(data_rows, headers=headers, tablefmt="fancy_grid")


def compute_unique_courses(schedule: Schedule, all_schedules: List[Schedule]) -> set:
    """
    Find courses that are unique to a specific schedule compared to other schedules.

    Args:
        schedule: The schedule to analyze
        all_schedules: List of all schedules to compare against

    Returns:
        Set of course codes unique to this schedule
    """
    all_sets = [set(c.code for c in s.courses) for s in all_schedules]
    if not all_sets:
        return set()

    common = set.intersection(*all_sets)
    current = set(c.code for c in schedule.courses)

    return current - common


def group_courses_by_type(schedule: Schedule) -> Dict[str, List[Course]]:
    """
    Group courses in a schedule by their type (lecture, ps, lab).

    Args:
        schedule: Schedule to analyze

    Returns:
        Dictionary mapping course types to lists of courses
    """
    result = {
        "lecture": [],
        "ps": [],
        "lab": []
    }

    for course in schedule.courses:
        course_type = course.course_type if hasattr(course, 'course_type') else 'lecture'
        if course_type in result:
            result[course_type].append(course)

    return result


def generate_schedule_summary(schedule: Schedule, index: int = 1) -> Dict[str, Any]:
    """
    Generate a comprehensive summary of a schedule.

    Args:
        schedule: Schedule to summarize
        index: Schedule number/index

    Returns:
        Dictionary with schedule summary information
    """
    course_counts = {
        "lecture": 0,
        "ps": 0,
        "lab": 0
    }

    # Count courses by type
    for course in schedule.courses:
        if course.course_type in course_counts:
            course_counts[course.course_type] += 1

    # Group courses by day
    courses_by_day = {day: [] for day in DAY_ORDER}
    for course in schedule.courses:
        for day, period in course.schedule:
            if day in courses_by_day and course not in courses_by_day[day]:
                courses_by_day[day].append(course)

    # Calculate day loads
    day_loads = {day: len(courses) for day, courses in courses_by_day.items()}

    return {
        "index": index,
        "total_credits": schedule.total_credits,
        "conflict_count": schedule.conflict_count,
        "course_counts": course_counts,
        "total_courses": len(schedule.courses),
        "day_loads": day_loads,
        "busiest_day": max(day_loads.items(), key=lambda x: x[1])[0] if day_loads else None,
        "lightest_day": min(day_loads.items(), key=lambda x: x[1])[0] if day_loads else None
    }


def format_schedule_details(schedule: Schedule, index: int = 1) -> str:
    """
    Format detailed schedule information as a string.

    Args:
        schedule: Schedule to format
        index: Schedule number/index

    Returns:
        Formatted string with schedule details
    """
    summary = generate_schedule_summary(schedule, index)

    details = [
        f"Schedule {index} Details:",
        f"Total Credits: {summary['total_credits']}",
        f"Conflict Count: {summary['conflict_count']}",
        f"Total Courses: {summary['total_courses']} ({summary['course_counts']['lecture']} lectures, "
        f"{summary['course_counts']['ps']} PS, {summary['course_counts']['lab']} labs)",
        f"Busiest Day: {summary['busiest_day']} ({summary['day_loads'][summary['busiest_day']]} courses)"
        if summary['busiest_day'] else "No days scheduled",
        f"Lightest Day: {summary['lightest_day']} ({summary['day_loads'][summary['lightest_day']]} courses)"
        if summary['lightest_day'] else "No days scheduled",
        "\nCourses by Day:"
    ]

    # Group courses by day for display
    courses_by_day = {day: [] for day in DAY_ORDER}
    for course in schedule.courses:
        for day, period in course.schedule:
            if day in courses_by_day and course not in courses_by_day[day]:
                courses_by_day[day].append(course)

    for day in DAY_ORDER:
        if courses_by_day[day]:
            details.append(f"{day}:")
            for course in sorted(courses_by_day[day], key=lambda c: c.code):
                periods = [period for d, period in course.schedule if d == day]
                periods_str = ", ".join(str(p) for p in sorted(periods))
                details.append(f"  - {course.code}: {course.name} (Periods: {periods_str})")

    return "\n".join(details)
