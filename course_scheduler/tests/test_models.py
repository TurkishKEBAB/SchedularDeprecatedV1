"""
Tests for the data models module.
"""
import pytest
from course_scheduler.app.data.models import Course, Schedule, Program, build_course_groups


def test_course_creation():
    """Test Course class initialization."""
    course = Course(
        code="CS101.1",
        main_code="CS101",
        name="Introduction to Computer Science",
        ects=5,
        course_type="lecture",
        schedule=[("M", 1), ("W", 1)],
        teacher="Dr. Smith",
        has_lecture=True
    )

    assert course.code == "CS101.1"
    assert course.main_code == "CS101"
    assert course.name == "Introduction to Computer Science"
    assert course.ects == 5
    assert course.course_type == "lecture"
    assert len(course.schedule) == 2
    assert course.teacher == "Dr. Smith"
    assert course.has_lecture is True


def test_course_from_dict():
    """Test creating a Course from a dictionary."""
    course_dict = {
        "code": "CS101.1",
        "main_code": "CS101",
        "name": "Introduction to Computer Science",
        "ECTS": 5,
        "type": "lecture",
        "schedule": [("M", 1), ("W", 1)],
        "teacher": "Dr. Smith",
        "hasLecture": True
    }

    course = Course.from_dict(course_dict)

    assert course.code == "CS101.1"
    assert course.ects == 5
    assert course.course_type == "lecture"


def test_course_to_dict():
    """Test converting Course to dictionary."""
    course = Course(
        code="CS101.1",
        main_code="CS101",
        name="Introduction to Computer Science",
        ects=5,
        course_type="lecture",
        schedule=[("M", 1), ("W", 1)],
        teacher="Dr. Smith",
        has_lecture=True
    )

    course_dict = course.to_dict()

    assert course_dict["code"] == "CS101.1"
    assert course_dict["ECTS"] == 5
    assert course_dict["type"] == "lecture"
    assert course_dict["hasLecture"] is True


def test_course_conflicts_with(sample_courses, conflicting_courses):
    """Test conflict detection between courses."""
    # CS101 should conflict with CS201 (same time slots)
    assert sample_courses[0].conflicts_with(conflicting_courses[0])

    # CS101 should not conflict with CS301 (different time slots)
    assert not sample_courses[0].conflicts_with(conflicting_courses[1])

    # CS101 should not conflict with its own problem session
    assert not sample_courses[0].conflicts_with(sample_courses[1])


def test_schedule_total_credits(sample_schedule):
    """Test schedule total credits calculation."""
    assert sample_schedule.total_credits == 11  # 5 (CS101) + 0 (PS) + 6 (MATH201)


def test_schedule_conflict_count(sample_courses):
    """Test schedule conflict detection."""
    # Non-conflicting schedule
    schedule1 = Schedule([sample_courses[0], sample_courses[1], sample_courses[2]])
    assert schedule1.conflict_count == 0

    # Add a conflicting course (same time slot as CS101)
    conflicting_schedule = Schedule([
        sample_courses[0],  # CS101 lecture (M1, W1)
        Course(
            code="CONF101.1",
            main_code="CONF101",
            name="Conflicting Course",
            ects=3,
            course_type="lecture",
            schedule=[("M", 1), ("F", 2)],  # M1 conflicts with CS101
            teacher="Dr. Conflict",
            has_lecture=True
        )
    ])
    assert conflicting_schedule.conflict_count == 1


def test_schedule_has_conflict_with(sample_schedule, conflicting_courses):
    """Test detecting conflicts when adding new courses."""
    # Adding CS201 would create a conflict (same slots as CS101)
    assert sample_schedule.has_conflict_with([conflicting_courses[0]])

    # Adding CS301 would not create conflicts
    assert not sample_schedule.has_conflict_with([conflicting_courses[1]])


def test_schedule_get_courses_by_main_code(sample_schedule, sample_courses):
    """Test retrieving courses by main code."""
    cs_courses = sample_schedule.get_courses_by_main_code("CS101")

    assert len(cs_courses) == 2
    assert sample_courses[0] in cs_courses  # CS101 lecture
    assert sample_courses[1] in cs_courses  # CS101 problem session


def test_program_operations(sample_courses):
    """Test Program class operations."""
    program = Program(
        name="Computer Science",
        mandatory_courses={"CS101", "MATH201"},
        frequency_prefs={"CS101": 3, "MATH201": 2},
        include_extra=True
    )

    schedule1 = Schedule([sample_courses[0], sample_courses[1]])
    schedule2 = Schedule([sample_courses[0], sample_courses[1], sample_courses[2]])

    program.add_schedule(schedule1)
    program.add_schedule(schedule2)

    # Test getting the best schedule (highest credits, lowest conflicts)
    best_schedule = program.get_best_schedule()
    assert best_schedule is not None
    assert best_schedule.total_credits == 11  # Should be schedule2

    # Test getting unique courses
    unique_courses = program.get_unique_courses(1)  # Courses unique to schedule2
    assert "MATH201.1" in unique_courses


def test_build_course_groups(sample_courses):
    """Test building course groups from a list of courses."""
    groups = build_course_groups(sample_courses)

    assert len(groups) == 3  # CS101, MATH201, PHY101
    assert "CS101" in groups
    assert len(groups["CS101"].courses) == 2  # Lecture and PS
    assert len(groups["MATH201"].courses) == 2  # Lecture and PS
    assert len(groups["PHY101"].courses) == 2  # Lecture and Lab
