"""
Course Scheduler Core Package
Contains the core business logic for course scheduling.
"""

__version__ = "2.0.0"
__author__ = "Course Scheduler Team"

# Import main classes for convenience
from .models import Course, Schedule, FilterProfile, SchedulerConfig, UserPreferences
from .planner import CourseScheduler
from .parser import process_excel_robust, validate_course_data
from .export import ScheduleExporter

__all__ = [
    'Course', 'Schedule', 'FilterProfile', 'SchedulerConfig', 'UserPreferences',
    'CourseScheduler', 'process_excel_robust', 'validate_course_data',
    'ScheduleExporter'
]
