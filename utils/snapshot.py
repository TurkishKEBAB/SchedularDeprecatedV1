"""
SQLite persistence layer for course snapshots and planner runs.
Handles saving/loading filtered course sets and filter profiles.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Schema version for future migrations
SCHEMA_VERSION = 1

def init_database(db_path: str) -> None:
    """Initialize SQLite database with required schema."""
    try:
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT DEFAULT (datetime('now')),
                    profile_json TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS snapshot_courses (
                    snapshot_id INTEGER,
                    code TEXT,
                    PRIMARY KEY (snapshot_id, code),
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS courses (
                    code TEXT PRIMARY KEY,
                    main_code TEXT,
                    name TEXT,
                    ects INTEGER,
                    course_type TEXT,
                    schedule_json TEXT,
                    teacher TEXT,
                    faculty TEXT,
                    department TEXT,
                    campus TEXT
                );
                
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT DEFAULT (datetime('now')),
                    profile_json TEXT,
                    planner_config_json TEXT
                );
                
                CREATE TABLE IF NOT EXISTS schedules (
                    run_id INTEGER,
                    idx INTEGER,
                    course_code TEXT,
                    PRIMARY KEY (run_id, idx, course_code),
                    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                );
                
                INSERT OR REPLACE INTO schema_version (version) VALUES (?);
            """, (SCHEMA_VERSION,))

        logger.info(f"Database initialized at {db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def save_snapshot_sqlite(db_path: str, courses: List[Dict], filter_profile: Dict) -> int:
    """
    Save a snapshot of filtered courses and filter profile.

    Args:
        db_path: Path to SQLite database
        courses: List of course dictionaries
        filter_profile: Filter configuration used

    Returns:
        snapshot_id: ID of created snapshot
    """
    try:
        with sqlite3.connect(db_path) as conn:
            # Ensure database exists
            init_database(db_path)

            # Upsert courses into courses table
            for course in courses:
                schedule_json = json.dumps(course.get("schedule", []))
                conn.execute("""
                    INSERT OR REPLACE INTO courses 
                    (code, main_code, name, ects, course_type, schedule_json, teacher, faculty, department, campus)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    course.get("code", ""),
                    course.get("main_code", ""),
                    course.get("name", ""),
                    course.get("ECTS", 0),
                    course.get("type", ""),
                    schedule_json,
                    course.get("teacher", ""),
                    course.get("faculty", "Unknown Faculty"),
                    course.get("department", "Unknown Department"),
                    course.get("campus", "Main Campus")
                ))

            # Insert snapshot
            profile_json = json.dumps(filter_profile)
            cursor = conn.execute("""
                INSERT INTO snapshots (profile_json) VALUES (?)
            """, (profile_json,))

            snapshot_id = cursor.lastrowid

            # Insert snapshot_courses relationships
            for course in courses:
                conn.execute("""
                    INSERT INTO snapshot_courses (snapshot_id, code) VALUES (?, ?)
                """, (snapshot_id, course.get("code", "")))

            conn.commit()
            logger.info(f"Snapshot saved with ID {snapshot_id}, {len(courses)} courses")
            return snapshot_id

    except Exception as e:
        logger.error(f"Failed to save snapshot: {e}")
        raise


def list_snapshots(db_path: str) -> List[Tuple[int, str, Dict]]:
    """
    List all saved snapshots.

    Returns:
        List of tuples: (id, created_at, profile_dict)
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("""
                SELECT id, created_at, profile_json FROM snapshots 
                ORDER BY created_at DESC
            """)

            results = []
            for row in cursor.fetchall():
                snapshot_id, created_at, profile_json = row
                try:
                    profile_dict = json.loads(profile_json)
                except json.JSONDecodeError:
                    profile_dict = {}
                results.append((snapshot_id, created_at, profile_dict))

            return results

    except Exception as e:
        logger.error(f"Failed to list snapshots: {e}")
        return []


def load_snapshot_sqlite(db_path: str, snapshot_id: int) -> Tuple[List[Dict], Dict]:
    """
    Load a snapshot by ID.

    Args:
        db_path: Path to SQLite database
        snapshot_id: ID of snapshot to load

    Returns:
        Tuple of (courses_list, profile_dict)
    """
    try:
        with sqlite3.connect(db_path) as conn:
            # Get snapshot profile
            cursor = conn.execute("""
                SELECT profile_json FROM snapshots WHERE id = ?
            """, (snapshot_id,))

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Snapshot {snapshot_id} not found")

            profile_dict = json.loads(row[0])

            # Get courses in this snapshot
            cursor = conn.execute("""
                SELECT c.code, c.main_code, c.name, c.ects, c.course_type, 
                       c.schedule_json, c.teacher, c.faculty, c.department, c.campus
                FROM courses c
                JOIN snapshot_courses sc ON c.code = sc.code
                WHERE sc.snapshot_id = ?
            """, (snapshot_id,))

            courses = []
            for row in cursor.fetchall():
                code, main_code, name, ects, course_type, schedule_json, teacher, faculty, department, campus = row

                try:
                    schedule = json.loads(schedule_json) if schedule_json else []
                except json.JSONDecodeError:
                    schedule = []

                course = {
                    "code": code,
                    "main_code": main_code,
                    "name": name,
                    "ECTS": ects,
                    "type": course_type,
                    "schedule": schedule,
                    "hasLecture": course_type == "lecture",
                    "teacher": teacher,
                    "faculty": faculty,
                    "department": department,
                    "campus": campus
                }
                courses.append(course)

            logger.info(f"Loaded snapshot {snapshot_id} with {len(courses)} courses")
            return courses, profile_dict

    except Exception as e:
        logger.error(f"Failed to load snapshot {snapshot_id}: {e}")
        raise


def save_run_result_sqlite(db_path: str, schedules: List[List[str]], profile: Dict, planner_config: Dict) -> int:
    """
    Save planner run results.

    Args:
        db_path: Path to SQLite database
        schedules: List of schedules, each schedule is a list of course codes
        profile: Filter profile used
        planner_config: Planner configuration

    Returns:
        run_id: ID of created run
    """
    try:
        with sqlite3.connect(db_path) as conn:
            # Ensure database exists
            init_database(db_path)

            # Insert run
            profile_json = json.dumps(profile)
            config_json = json.dumps(planner_config)

            cursor = conn.execute("""
                INSERT INTO runs (profile_json, planner_config_json) VALUES (?, ?)
            """, (profile_json, config_json))

            run_id = cursor.lastrowid

            # Insert schedules
            for idx, schedule in enumerate(schedules):
                for course_code in schedule:
                    conn.execute("""
                        INSERT INTO schedules (run_id, idx, course_code) VALUES (?, ?, ?)
                    """, (run_id, idx, course_code))

            conn.commit()
            logger.info(f"Run saved with ID {run_id}, {len(schedules)} schedules")
            return run_id

    except Exception as e:
        logger.error(f"Failed to save run: {e}")
        raise


def get_snapshot_brief(profile: Dict) -> str:
    """Generate a brief description of a snapshot's filter profile."""
    parts = []

    if profile.get("query"):
        parts.append(f"Query: '{profile['query']}'")

    if profile.get("faculty") and profile["faculty"] != "All":
        parts.append(f"Faculty: {profile['faculty']}")

    if profile.get("department") and profile["department"] != "All":
        parts.append(f"Dept: {profile['department']}")

    if profile.get("campus") and profile["campus"] != "All":
        parts.append(f"Campus: {profile['campus']}")

    ects_min = profile.get("ects_min", 0)
    ects_max = profile.get("ects_max", 50)
    if ects_min > 0 or ects_max < 50:
        parts.append(f"ECTS: {ects_min}-{ects_max}")

    days = profile.get("days", [])
    if days and len(days) < 7:
        parts.append(f"Days: {','.join(days)}")

    slots = profile.get("slots", [])
    if slots and len(slots) < 12:
        parts.append(f"Slots: {len(slots)} selected")

    restricted = profile.get("restricted", False)
    if restricted:
        parts.append("FILTERED")

    return " | ".join(parts) if parts else "No filters"
