"""
Test configuration and fixtures for the course scheduler tests.
"""
import os
import sys
import pytest
from typing import List, Dict

# Add the project root to sys.path to import the module correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from course_scheduler.app.data.models import Course, Schedule, Program


@pytest.fixture
def sample_courses() -> List[Course]:
    """Fixture providing sample courses for testing."""
    return [
        Course(
            code="CS101.1",
            main_code="CS101",
            name="Introduction to Computer Science",
            ects=5,
            course_type="lecture",
            schedule=[("M", 1), ("W", 1)],
            teacher="Dr. Smith",
            has_lecture=True
        ),
        Course(
            code="CS101-PS1",
            main_code="CS101",
            name="CS101 Problem Session",
            ects=0,
            course_type="ps",
            schedule=[("T", 3)],
            teacher="TA Johnson",
            has_lecture=False
        ),
        Course(
            code="MATH201.1",
            main_code="MATH201",
            name="Linear Algebra",
            ects=6,
            course_type="lecture",
            schedule=[("T", 1), ("Th", 1)],
            teacher="Dr. Brown",
            has_lecture=True
        ),
        Course(
            code="MATH201-PS1",
            main_code="MATH201",
            name="MATH201 Problem Session",
            ects=0,
            course_type="ps",
            schedule=[("F", 3)],
            teacher="TA Davis",
            has_lecture=False
        ),
        Course(
            code="PHY101.1",
            main_code="PHY101",
            name="Physics I",
            ects=5,
            course_type="lecture",
            schedule=[("M", 3), ("W", 3)],
            teacher="Dr. Wilson",
            has_lecture=True
        ),
        Course(
            code="PHY101-L1",
            main_code="PHY101",
            name="Physics Lab",
            ects=1,
            course_type="lab",
            schedule=[("F", 5)],
            teacher="Lab Assistant",
            has_lecture=False
        )
    ]


@pytest.fixture
def sample_schedule(sample_courses) -> Schedule:
    """Fixture providing a sample schedule for testing."""
    # Include just CS101 lecture and PS, and MATH201 lecture
    return Schedule([sample_courses[0], sample_courses[1], sample_courses[2]])


@pytest.fixture
def conflicting_courses() -> List[Course]:
    """Fixture providing courses with time conflicts."""
    return [
        Course(
            code="CS201.1",
            main_code="CS201",
            name="Data Structures",
            ects=5,
            course_type="lecture",
            schedule=[("M", 1), ("W", 1)],  # Conflicts with CS101
            teacher="Dr. Lee",
            has_lecture=True
        ),
        Course(
            code="CS301.1",
            main_code="CS301",
            name="Algorithms",
            ects=5,
            course_type="lecture",
            schedule=[("M", 2), ("W", 2)],  # No conflicts
            teacher="Dr. Garcia",
            has_lecture=True
        )
    ]
