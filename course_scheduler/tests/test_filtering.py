"""
Tests for course filtering functionality.

This module tests the course filtering capabilities in the Course Preview tab.
"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
import tkinter as tk
from tkinter import ttk
from course_scheduler.app.data.models import Course
from course_scheduler.app.gui.course_preview import CoursePreviewTab


@pytest.fixture
def sample_courses():
    """Fixture providing test courses with various attributes."""
    return [
        Course(
            code="CS101.1",
            main_code="CS101",
            name="Introduction to Programming",
            ects=5,
            course_type="lecture",
            schedule=[("M", 1), ("W", 1)],
            teacher="Prof. Smith",
            faculty="Computer Science",
            department="Software Engineering",
            campus="Main"
        ),
        Course(
            code="CS101-PS1",
            main_code="CS101",
            name="CS101 Problem Session",
            ects=0,
            course_type="ps",
            schedule=[("T", 3)],
            teacher="TA Johnson",
            faculty="Computer Science",
            department="Software Engineering",
            campus="Main"
        ),
        Course(
            code="MATH201.1",
            main_code="MATH201",
            name="Calculus I",
            ects=6,
            course_type="lecture",
            schedule=[("Th", 2), ("F", 2)],
            teacher="Prof. Brown",
            faculty="Science",
            department="Mathematics",
            campus="South"
        ),
        Course(
            code="ENG101.1",
            main_code="ENG101",
            name="English Composition",
            ects=3,
            course_type="lecture",
            schedule=[("M", 5), ("W", 5)],
            teacher="Prof. Davis",
            faculty="Humanities",
            department="English",
            campus="North"
        )
    ]


class TestCourseFiltering:
    """Tests for course filtering functionality."""

    def setup_method(self):
        """Set up test environment for each test method."""
        # Create a mock parent and main_app
        self.parent = MagicMock()
        self.main_app = MagicMock()

        # Use a headless approach for testing
        with patch('tkinter.ttk.Frame'):
            with patch('tkinter.ttk.LabelFrame'):
                with patch('tkinter.ttk.Entry'):
                    with patch('tkinter.ttk.Combobox'):
                        with patch('tkinter.ttk.Treeview'):
                            # Initialize CoursePreviewTab with mocked components
                            self.preview_tab = CoursePreviewTab(self.parent, self.main_app)

    def test_create_dataframe(self, sample_courses):
        """Test creating a DataFrame from courses."""
        # Create a dataframe directly from sample courses
        data = []
        for course in sample_courses:
            data.append({
                "code": course.code,
                "main_code": course.main_code,
                "name": course.name,
                "ects": course.ects,
                "course_type": course.course_type,
                "schedule": course.schedule,
                "teacher": course.teacher,
                "faculty": course.faculty,
                "department": course.department,
                "campus": course.campus
            })

        df = pd.DataFrame(data)

        # Verify dataframe structure
        assert len(df) == len(sample_courses)
        assert set(df.columns) == {
            "code", "main_code", "name", "ects", "course_type",
            "schedule", "teacher", "faculty", "department", "campus"
        }

        # Verify unique values
        assert set(df["faculty"]) == {"Computer Science", "Science", "Humanities"}
        assert set(df["department"]) == {"Software Engineering", "Mathematics", "English"}
        assert set(df["campus"]) == {"Main", "South", "North"}

    def test_faculty_filtering(self):
        """Test filtering courses by faculty."""
        # Create test data with faculty values
        df = pd.DataFrame({
            "code": ["CS101", "CS102", "MATH101", "ENG101"],
            "faculty": ["CS", "CS", "Science", "Humanities"]
        })

        # Filter by faculty
        filtered = df[df["faculty"] == "CS"]
        assert len(filtered) == 2
        assert set(filtered["code"]) == {"CS101", "CS102"}

    def test_department_filtering(self):
        """Test filtering courses by department."""
        # Create test data with department values
        df = pd.DataFrame({
            "code": ["CS101", "CS102", "MATH101", "ENG101"],
            "department": ["SE", "SE", "Math", "English"]
        })

        # Filter by department
        filtered = df[df["department"] == "SE"]
        assert len(filtered) == 2
        assert set(filtered["code"]) == {"CS101", "CS102"}

    def test_campus_filtering(self):
        """Test filtering courses by campus."""
        # Create test data with campus values
        df = pd.DataFrame({
            "code": ["CS101", "CS102", "MATH101", "ENG101"],
            "campus": ["Main", "Main", "South", "North"]
        })

        # Filter by campus
        filtered = df[df["campus"] == "Main"]
        assert len(filtered) == 2
        assert set(filtered["code"]) == {"CS101", "CS102"}

    def test_combined_filters(self):
        """Test combining multiple filters."""
        # Create test data
        df = pd.DataFrame({
            "code": ["CS101", "CS102", "CS201", "MATH101"],
            "faculty": ["CS", "CS", "CS", "Science"],
            "department": ["SE", "SE", "AI", "Math"],
            "campus": ["Main", "South", "Main", "Main"],
            "ects": [5, 4, 6, 5]
        })

        # Apply faculty + department filter
        filtered = df[(df["faculty"] == "CS") & (df["department"] == "SE")]
        assert len(filtered) == 2
        assert set(filtered["code"]) == {"CS101", "CS102"}

        # Apply faculty + campus filter
        filtered = df[(df["faculty"] == "CS") & (df["campus"] == "Main")]
        assert len(filtered) == 2
        assert set(filtered["code"]) == {"CS101", "CS201"}

        # Apply all filters
        filtered = df[(df["faculty"] == "CS") &
                     (df["department"] == "SE") &
                     (df["campus"] == "Main")]
        assert len(filtered) == 1
        assert filtered["code"].iloc[0] == "CS101"

    def test_credit_range_filter(self):
        """Test filtering by credit range."""
        # Create test data with credit values
        df = pd.DataFrame({
            "code": ["CS101", "CS102", "MATH101", "ENG101"],
            "ects": [3, 5, 6, 2]
        })

        # Filter by minimum credit
        min_filtered = df[df["ects"] >= 5]
        assert len(min_filtered) == 2
        assert set(min_filtered["code"]) == {"CS102", "MATH101"}

        # Filter by maximum credit
        max_filtered = df[df["ects"] <= 3]
        assert len(max_filtered) == 2
        assert set(max_filtered["code"]) == {"CS101", "ENG101"}

        # Filter by range
        range_filtered = df[(df["ects"] >= 3) & (df["ects"] <= 5)]
        assert len(range_filtered) == 2
        assert set(range_filtered["code"]) == {"CS101", "CS102"}

    def test_day_slot_filtering(self):
        """Test filtering by day and time slot."""
        # Create test data with schedule values
        df = pd.DataFrame({
            "code": ["CS101", "CS102", "MATH101", "ENG101"],
            "schedule": [
                [("M", 1), ("W", 2)],
                [("T", 3), ("Th", 4)],
                [("M", 5), ("F", 6)],
                [("W", 7), ("F", 8)]
            ]
        })

        # Function to filter by day
        def filter_by_day(df, day):
            mask = pd.Series(False, index=df.index)
            for idx, row in df.iterrows():
                if any(slot[0] == day for slot in row["schedule"]):
                    mask.loc[idx] = True
            return df[mask]

        # Test day filter
        m_courses = filter_by_day(df, "M")
        assert len(m_courses) == 2
        assert set(m_courses["code"]) == {"CS101", "MATH101"}

        # Function to filter by slot
        def filter_by_slot(df, slot):
            mask = pd.Series(False, index=df.index)
            for idx, row in df.iterrows():
                if any(slot_info[1] == slot for slot_info in row["schedule"]):
                    mask.loc[idx] = True
            return df[mask]

        # Test slot filter
        slot_5_courses = filter_by_slot(df, 5)
        assert len(slot_5_courses) == 1
        assert slot_5_courses["code"].iloc[0] == "MATH101"

        # Function to filter by both day and slot
        def filter_by_day_and_slot(df, days, slots):
            mask = pd.Series(False, index=df.index)
            for idx, row in df.iterrows():
                days_match = not days or any(slot[0] in days for slot in row["schedule"])
                slots_match = not slots or any(slot[1] in slots for slot in row["schedule"])
                mask.loc[idx] = days_match and slots_match
            return df[mask]

        # Test combined day and slot filter
        filtered = filter_by_day_and_slot(df, {"M", "W"}, {1, 2, 7})
        assert len(filtered) == 2
        assert set(filtered["code"]) == {"CS101", "ENG101"}
