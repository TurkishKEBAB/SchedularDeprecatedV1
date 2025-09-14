"""
SQLite persistence layer for course snapshots and planner runs.
Handles saving/loading filtered course sets and filter profiles.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

from ..core.models import Course, FilterProfile, SnapshotInfo

logger = logging.getLogger(__name__)

# Schema version for future migrations
SCHEMA_VERSION = 1


class SnapshotManager:
    """Manages course snapshots and planner run persistence."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()

    def init_database(self) -> None:
        """Initialize SQLite database with required schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Create schema without parameters
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
                """)

                # Insert schema version separately with parameters
                conn.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
                conn.commit()

            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def save_snapshot(self, courses: List[Course], filter_profile: FilterProfile) -> int:
        """Save a snapshot of filtered courses and filter profile."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Upsert courses into courses table
                for course in courses:
                    schedule_json = json.dumps(course.schedule)
                    conn.execute("""
                        INSERT OR REPLACE INTO courses 
                        (code, main_code, name, ects, course_type, schedule_json, teacher, faculty, department, campus)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        course.code,
                        course.main_code,
                        course.name,
                        course.ects,
                        course.course_type.value,
                        schedule_json,
                        course.teacher,
                        course.faculty,
                        course.department,
                        course.campus
                    ))

                # Insert snapshot
                profile_json = json.dumps(filter_profile.to_dict())
                cursor = conn.execute("""
                    INSERT INTO snapshots (profile_json) VALUES (?)
                """, (profile_json,))

                snapshot_id = cursor.lastrowid

                # Insert snapshot-course associations
                for course in courses:
                    conn.execute("""
                        INSERT INTO snapshot_courses (snapshot_id, code) VALUES (?, ?)
                    """, (snapshot_id, course.code))

                conn.commit()
                logger.info(f"Saved snapshot {snapshot_id} with {len(courses)} courses")
                return snapshot_id

        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            raise

    def load_snapshot(self, snapshot_id: int) -> Tuple[List[Course], FilterProfile]:
        """Load a snapshot by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load filter profile
                cursor = conn.execute("""
                    SELECT profile_json FROM snapshots WHERE id = ?
                """, (snapshot_id,))

                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Snapshot {snapshot_id} not found")

                profile_data = json.loads(row[0])
                filter_profile = FilterProfile.from_dict(profile_data)

                # Load courses
                cursor = conn.execute("""
                    SELECT c.code, c.main_code, c.name, c.ects, c.course_type, 
                           c.schedule_json, c.teacher, c.faculty, c.department, c.campus
                    FROM courses c
                    JOIN snapshot_courses sc ON c.code = sc.code
                    WHERE sc.snapshot_id = ?
                """, (snapshot_id,))

                courses = []
                for row in cursor.fetchall():
                    from ..core.models import CourseType
                    schedule = json.loads(row[5])
                    course = Course(
                        code=row[0],
                        main_code=row[1],
                        name=row[2],
                        ects=row[3],
                        course_type=CourseType(row[4]),
                        schedule=schedule,
                        teacher=row[6],
                        faculty=row[7],
                        department=row[8],
                        campus=row[9]
                    )
                    courses.append(course)

                logger.info(f"Loaded snapshot {snapshot_id} with {len(courses)} courses")
                return courses, filter_profile

        except Exception as e:
            logger.error(f"Failed to load snapshot {snapshot_id}: {e}")
            raise

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available snapshots."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT s.id, s.created_at, s.profile_json, COUNT(sc.code) as course_count
                    FROM snapshots s
                    LEFT JOIN snapshot_courses sc ON s.id = sc.snapshot_id
                    GROUP BY s.id
                    ORDER BY s.created_at DESC
                """)

                snapshots = []
                for row in cursor.fetchall():
                    profile_data = json.loads(row[2])
                    snapshots.append({
                        'id': row[0],
                        'created_at': row[1],
                        'course_count': row[3],
                        'filter_profile': profile_data,
                        'description': self._generate_snapshot_description(profile_data, row[3])
                    })

                return snapshots

        except Exception as e:
            logger.error(f"Failed to list snapshots: {e}")
            return []

    def delete_snapshot(self, snapshot_id: int) -> bool:
        """Delete a snapshot by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM snapshots WHERE id = ?", (snapshot_id,))
                deleted = cursor.rowcount > 0
                conn.commit()

                if deleted:
                    logger.info(f"Deleted snapshot {snapshot_id}")
                else:
                    logger.warning(f"Snapshot {snapshot_id} not found for deletion")

                return deleted

        except Exception as e:
            logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")
            return False

    def save_results_snapshot(self, schedule_codes: List[List[str]],
                            preferences: Any, filter_profile: FilterProfile) -> int:
        """Save results from a planner run."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Prepare data for storage
                profile_json = json.dumps(filter_profile.to_dict())
                preferences_dict = {
                    'mandatory_courses': list(preferences.mandatory_courses) if hasattr(preferences, 'mandatory_courses') else [],
                    'frequency_prefs': {k: v.value for k, v in preferences.frequency_prefs.items()} if hasattr(preferences, 'frequency_prefs') else {},
                    'include_extra': getattr(preferences, 'include_extra', True)
                }
                config_json = json.dumps(preferences_dict)

                # Insert run record
                cursor = conn.execute("""
                    INSERT INTO runs (profile_json, planner_config_json) VALUES (?, ?)
                """, (profile_json, config_json))

                run_id = cursor.lastrowid

                # Insert schedule data
                for idx, schedule in enumerate(schedule_codes):
                    for course_code in schedule:
                        conn.execute("""
                            INSERT INTO schedules (run_id, idx, course_code) VALUES (?, ?, ?)
                        """, (run_id, idx, course_code))

                conn.commit()
                logger.info(f"Saved results snapshot {run_id} with {len(schedule_codes)} schedules")
                return run_id

        except Exception as e:
            logger.error(f"Failed to save results snapshot: {e}")
            raise

    def load_results_snapshot(self, run_id: int) -> Dict[str, Any]:
        """Load results from a planner run."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load run metadata
                cursor = conn.execute("""
                    SELECT created_at, profile_json, planner_config_json FROM runs WHERE id = ?
                """, (run_id,))

                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Results snapshot {run_id} not found")

                created_at, profile_json, config_json = row
                filter_profile = json.loads(profile_json)
                planner_config = json.loads(config_json)

                # Load schedules
                cursor = conn.execute("""
                    SELECT idx, course_code FROM schedules WHERE run_id = ? ORDER BY idx, course_code
                """, (run_id,))

                schedules_dict = {}
                for idx, course_code in cursor.fetchall():
                    if idx not in schedules_dict:
                        schedules_dict[idx] = []
                    schedules_dict[idx].append(course_code)

                schedules = [schedules_dict[i] for i in sorted(schedules_dict.keys())]

                return {
                    'run_id': run_id,
                    'created_at': created_at,
                    'filter_profile': filter_profile,
                    'planner_config': planner_config,
                    'schedules': schedules
                }

        except Exception as e:
            logger.error(f"Failed to load results snapshot {run_id}: {e}")
            raise

    def list_results_snapshots(self) -> List[Dict[str, Any]]:
        """List all results snapshots."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT r.id, r.created_at, r.profile_json, r.planner_config_json,
                           COUNT(DISTINCT s.idx) as schedule_count,
                           COUNT(s.course_code) as total_courses
                    FROM runs r
                    LEFT JOIN schedules s ON r.id = s.run_id
                    GROUP BY r.id
                    ORDER BY r.created_at DESC
                """)

                results = []
                for row in cursor.fetchall():
                    filter_profile = json.loads(row[2])
                    planner_config = json.loads(row[3])

                    results.append({
                        'id': row[0],
                        'created_at': row[1],
                        'schedule_count': row[4],
                        'total_courses': row[5],
                        'filter_profile': filter_profile,
                        'planner_config': planner_config,
                        'description': f"Run with {row[4]} schedules, {row[5]} total course selections"
                    })

                return results

        except Exception as e:
            logger.error(f"Failed to list results snapshots: {e}")
            return []

    def cleanup_old_snapshots(self, keep_count: int = 50) -> int:
        """Clean up old snapshots, keeping only the most recent ones."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Delete old snapshots
                cursor = conn.execute("""
                    DELETE FROM snapshots WHERE id NOT IN (
                        SELECT id FROM snapshots ORDER BY created_at DESC LIMIT ?
                    )
                """, (keep_count,))

                deleted_snapshots = cursor.rowcount

                # Delete old results
                cursor = conn.execute("""
                    DELETE FROM runs WHERE id NOT IN (
                        SELECT id FROM runs ORDER BY created_at DESC LIMIT ?
                    )
                """, (keep_count,))

                deleted_runs = cursor.rowcount

                # Clean up orphaned courses
                cursor = conn.execute("""
                    DELETE FROM courses WHERE code NOT IN (
                        SELECT DISTINCT code FROM snapshot_courses
                    )
                """)

                deleted_courses = cursor.rowcount

                conn.commit()

                total_deleted = deleted_snapshots + deleted_runs
                logger.info(f"Cleanup completed: {deleted_snapshots} snapshots, {deleted_runs} runs, {deleted_courses} orphaned courses")

                return total_deleted

        except Exception as e:
            logger.error(f"Failed to cleanup snapshots: {e}")
            return 0

    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}

                # Count snapshots
                cursor = conn.execute("SELECT COUNT(*) FROM snapshots")
                stats['snapshots'] = cursor.fetchone()[0]

                # Count runs
                cursor = conn.execute("SELECT COUNT(*) FROM runs")
                stats['runs'] = cursor.fetchone()[0]

                # Count courses
                cursor = conn.execute("SELECT COUNT(*) FROM courses")
                stats['courses'] = cursor.fetchone()[0]

                # Count total schedules
                cursor = conn.execute("SELECT COUNT(DISTINCT run_id, idx) FROM schedules")
                stats['total_schedules'] = cursor.fetchone()[0]

                return stats

        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

    def _generate_snapshot_description(self, profile_data: Dict, course_count: int) -> str:
        """Generate a human-readable description for a snapshot."""
        parts = []

        if profile_data.get('query'):
            parts.append(f"Query: '{profile_data['query']}'")

        if profile_data.get('faculty') != 'All':
            parts.append(f"Faculty: {profile_data['faculty']}")

        if profile_data.get('department') != 'All':
            parts.append(f"Dept: {profile_data['department']}")

        ects_min, ects_max = profile_data.get('ects_min', 0), profile_data.get('ects_max', 50)
        if ects_min > 0 or ects_max < 50:
            parts.append(f"ECTS: {ects_min}-{ects_max}")

        if parts:
            description = f"{course_count} courses - " + ", ".join(parts)
        else:
            description = f"{course_count} courses - No filters"

        return description

    def export_database(self, export_path: str) -> bool:
        """Export database to SQL file."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                with open(export_path, 'w', encoding='utf-8') as f:
                    for line in conn.iterdump():
                        f.write(f"{line}\n")

            logger.info(f"Database exported to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export database: {e}")
            return False

    def close(self) -> None:
        """Close database connections and clean up."""
        try:
            # Perform any cleanup operations
            self.cleanup_old_snapshots()
            logger.info("Snapshot manager closed successfully")
        except Exception as e:
            logger.error(f"Error during snapshot manager cleanup: {e}")


# Compatibility classes for backward compatibility
class SnapshotInfo:
    """Information about a saved snapshot."""
    def __init__(self, snapshot_id: int, created_at: str, course_count: int, description: str):
        self.id = snapshot_id
        self.created_at = created_at
        self.course_count = course_count
        self.description = description
