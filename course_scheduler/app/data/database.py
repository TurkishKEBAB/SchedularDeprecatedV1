"""
Database integration for the course scheduler application.

This module provides functionality for storing and retrieving course data
using SQLite database, as an alternative to Excel files.
"""
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from ..data.models import Course, Schedule, Program
from ..config import DATABASE_PATH

# Set up logging
logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for course scheduler application."""

    def __init__(self, db_path: str = DATABASE_PATH):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None

    def connect(self) -> None:
        """
        Connect to the database, creating it if it doesn't exist.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")

    def __enter__(self):
        """
        Support context manager protocol for 'with' statement.
        """
        if not self.conn:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensure the database connection is closed when exiting context.
        """
        self.close()

    def initialize(self) -> None:
        """
        Initialize the database schema, creating tables if they don't exist.
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()

            # Create courses table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                main_code TEXT NOT NULL,
                name TEXT NOT NULL,
                ects INTEGER NOT NULL,
                course_type TEXT NOT NULL,
                schedule TEXT NOT NULL,
                teacher TEXT,
                has_lecture BOOLEAN NOT NULL
            )
            ''')

            # Create schedules table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                total_credits INTEGER NOT NULL,
                conflict_count INTEGER NOT NULL,
                courses TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Create programs table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS programs (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                mandatory_courses TEXT NOT NULL,
                frequency_prefs TEXT NOT NULL,
                include_extra BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Create program_schedules join table (many-to-many)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS program_schedules (
                program_id INTEGER,
                schedule_id INTEGER,
                FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE CASCADE,
                FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE,
                PRIMARY KEY (program_id, schedule_id)
            )
            ''')

            self.conn.commit()
            logger.info("Database schema initialized")
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Database initialization error: {e}")
            raise

    def save_course(self, course: Course) -> int:
        """
        Save a course to the database.

        Args:
            course: Course object to save

        Returns:
            ID of the saved course record
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()

            cursor.execute('''
            INSERT OR REPLACE INTO courses 
            (code, main_code, name, ects, course_type, schedule, teacher, has_lecture)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                course.code,
                course.main_code,
                course.name,
                course.ects,
                course.course_type,
                json.dumps(course.schedule),
                course.teacher,
                course.has_lecture
            ))

            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error saving course {course.code}: {e}")
            raise

    def save_courses(self, courses: List[Course]) -> None:
        """
        Save multiple courses to the database.

        Args:
            courses: List of Course objects to save
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()

            for course in courses:
                cursor.execute('''
                INSERT OR REPLACE INTO courses 
                (code, main_code, name, ects, course_type, schedule, teacher, has_lecture)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    course.code,
                    course.main_code,
                    course.name,
                    course.ects,
                    course.course_type,
                    json.dumps(course.schedule),
                    course.teacher,
                    course.has_lecture
                ))

            self.conn.commit()
            logger.info(f"Saved {len(courses)} courses to database")
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error saving courses batch: {e}")
            raise

    def get_all_courses(self) -> List[Course]:
        """
        Retrieve all courses from the database.

        Returns:
            List of Course objects
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM courses')

            courses = []
            for row in cursor.fetchall():
                course_dict = dict(row)
                course_dict["schedule"] = json.loads(course_dict["schedule"])
                course_dict["ECTS"] = course_dict.pop("ects")
                course_dict["type"] = course_dict.pop("course_type")
                course_dict["hasLecture"] = course_dict.pop("has_lecture")

                courses.append(Course.from_dict(course_dict))

            return courses
        except sqlite3.Error as e:
            logger.error(f"Error retrieving courses: {e}")
            raise

    def get_courses_by_main_code(self, main_code: str) -> List[Course]:
        """
        Retrieve courses with a specific main code.

        Args:
            main_code: Main course code to search for

        Returns:
            List of matching Course objects
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM courses WHERE main_code = ?', (main_code,))

            courses = []
            for row in cursor.fetchall():
                course_dict = dict(row)
                course_dict["schedule"] = json.loads(course_dict["schedule"])
                course_dict["ECTS"] = course_dict.pop("ects")
                course_dict["type"] = course_dict.pop("course_type")
                course_dict["hasLecture"] = course_dict.pop("has_lecture")

                courses.append(Course.from_dict(course_dict))

            return courses
        except sqlite3.Error as e:
            logger.error(f"Error retrieving courses by main code {main_code}: {e}")
            raise

    def save_schedule(self, schedule: Schedule, name: str = "") -> int:
        """
        Save a schedule to the database.

        Args:
            schedule: Schedule object to save
            name: Optional name for the schedule

        Returns:
            ID of the saved schedule record
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()

            if not name:
                name = f"Schedule {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            cursor.execute('''
            INSERT INTO schedules 
            (name, total_credits, conflict_count, courses)
            VALUES (?, ?, ?, ?)
            ''', (
                name,
                schedule.total_credits,
                schedule.conflict_count,
                json.dumps([c.code for c in schedule.courses])
            ))

            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error saving schedule {name}: {e}")
            raise

    def get_schedule(self, schedule_id: int) -> Optional[Schedule]:
        """
        Retrieve a schedule by ID.

        Args:
            schedule_id: ID of the schedule to retrieve

        Returns:
            Schedule object or None if not found
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM schedules WHERE id = ?', (schedule_id,))

            row = cursor.fetchone()
            if not row:
                return None

            schedule_dict = dict(row)
            course_codes = json.loads(schedule_dict["courses"])

            # Retrieve all referenced courses
            course_list = []
            for code in course_codes:
                cursor.execute('SELECT * FROM courses WHERE code = ?', (code,))
                course_row = cursor.fetchone()
                if course_row:
                    course_dict = dict(course_row)
                    course_dict["schedule"] = json.loads(course_dict["schedule"])
                    course_dict["ECTS"] = course_dict.pop("ects")
                    course_dict["type"] = course_dict.pop("course_type")
                    course_dict["hasLecture"] = course_dict.pop("has_lecture")
                    course_list.append(Course.from_dict(course_dict))

            return Schedule(courses=course_list)
        except sqlite3.Error as e:
            logger.error(f"Error retrieving schedule {schedule_id}: {e}")
            raise

    def save_program(self, program: Program) -> int:
        """
        Save a program to the database.

        Args:
            program: Program object to save

        Returns:
            ID of the saved program record
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()

            cursor.execute('''
            INSERT INTO programs 
            (name, mandatory_courses, frequency_prefs, include_extra)
            VALUES (?, ?, ?, ?)
            ''', (
                program.name,
                json.dumps(list(program.mandatory_courses)),
                json.dumps(program.frequency_prefs),
                program.include_extra
            ))

            program_id = cursor.lastrowid

            # Save each schedule and link it to the program
            for schedule in program.schedules:
                schedule_id = self.save_schedule(schedule, f"{program.name} Schedule")

                cursor.execute('''
                INSERT INTO program_schedules (program_id, schedule_id)
                VALUES (?, ?)
                ''', (program_id, schedule_id))

            self.conn.commit()
            return program_id
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error saving program {program.name}: {e}")
            raise

    def get_program(self, program_id: int) -> Optional[Program]:
        """
        Retrieve a program by ID.

        Args:
            program_id: ID of the program to retrieve

        Returns:
            Program object or None if not found
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM programs WHERE id = ?', (program_id,))

            row = cursor.fetchone()
            if not row:
                return None

            program_dict = dict(row)
            name = program_dict["name"]
            mandatory_courses = set(json.loads(program_dict["mandatory_courses"]))
            frequency_prefs = json.loads(program_dict["frequency_prefs"])
            include_extra = bool(program_dict["include_extra"])

            # Create program without schedules
            program = Program(
                name=name,
                mandatory_courses=mandatory_courses,
                frequency_prefs=frequency_prefs,
                include_extra=include_extra
            )

            # Retrieve linked schedules
            cursor.execute('''
            SELECT schedule_id FROM program_schedules
            WHERE program_id = ?
            ''', (program_id,))

            for row in cursor.fetchall():
                schedule_id = row[0]
                schedule = self.get_schedule(schedule_id)
                if schedule:
                    program.add_schedule(schedule)

            return program
        except sqlite3.Error as e:
            logger.error(f"Error retrieving program {program_id}: {e}")
            raise

    def get_all_programs(self) -> List[Program]:
        """
        Retrieve all programs from the database.

        Returns:
            List of Program objects
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM programs ORDER BY created_at DESC')

            programs = []
            for row in cursor.fetchall():
                program_id = row[0]
                program = self.get_program(program_id)
                if program:
                    programs.append(program)

            return programs
        except sqlite3.Error as e:
            logger.error(f"Error retrieving all programs: {e}")
            raise
