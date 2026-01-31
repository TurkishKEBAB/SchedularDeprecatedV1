"""
Schedule Database System for caching and analyzing generated schedules.

This module provides persistent storage and advanced filtering capabilities
for generated schedules, enabling data analysis and smart filtering.
"""
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

from ..data.models import Schedule, Course
from ..utils.schedule_metrics import compute_schedule_stats

logger = logging.getLogger(__name__)


class ScheduleDatabase:
    """
    Database system for storing and analyzing generated schedules.

    Features:
    - Persistent storage of schedules and their metadata
    - Hash-based duplicate detection
    - Advanced filtering and search capabilities
    - Statistical analysis of schedule patterns
    - Export capabilities (PDF, Excel, JPEG)
    """

    def __init__(self, db_path: str = "schedules.db"):
        """
        Initialize the schedule database.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Schedules table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS schedules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        schedule_hash TEXT UNIQUE NOT NULL,
                        course_codes TEXT NOT NULL,
                        total_credits INTEGER NOT NULL,
                        conflict_count INTEGER NOT NULL,
                        days_used INTEGER NOT NULL,
                        total_gaps INTEGER NOT NULL,
                        free_days TEXT NOT NULL,
                        schedule_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        generation_params TEXT
                    )
                ''')

                # Course statistics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS course_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        course_code TEXT NOT NULL,
                        course_name TEXT NOT NULL,
                        course_type TEXT NOT NULL,
                        faculty TEXT NOT NULL,
                        department TEXT NOT NULL,
                        usage_count INTEGER DEFAULT 0,
                        avg_conflicts REAL DEFAULT 0,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Schedule analysis table for patterns
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS schedule_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_type TEXT NOT NULL,
                        pattern_data TEXT NOT NULL,
                        frequency INTEGER DEFAULT 1,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("Schedule database tables created/verified")

        except Exception as e:
            logger.error(f"Error creating database tables: {e}")

    def add_schedules(self, schedules: List[Schedule], generation_params: Dict[str, Any] = None) -> int:
        """
        Add multiple schedules to the database.

        Args:
            schedules: List of Schedule objects to add
            generation_params: Parameters used to generate these schedules

        Returns:
            Number of new schedules added (excluding duplicates)
        """
        added_count = 0
        params_json = json.dumps(generation_params) if generation_params else None

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for schedule in schedules:
                    if self._add_single_schedule(cursor, schedule, params_json):
                        added_count += 1

                conn.commit()
                logger.info(f"Added {added_count} new schedules to database")

        except Exception as e:
            logger.error(f"Error adding schedules to database: {e}")

        return added_count

    def _add_single_schedule(self, cursor, schedule: Schedule, params_json: str = None) -> bool:
        """
        Add a single schedule to the database.

        Args:
            cursor: Database cursor
            schedule: Schedule to add
            params_json: Generation parameters as JSON string

        Returns:
            True if added, False if duplicate
        """
        try:
            # Calculate schedule hash for duplicate detection
            schedule_hash = self._calculate_schedule_hash(schedule)

            # Check if schedule already exists
            cursor.execute('SELECT id FROM schedules WHERE schedule_hash = ?', (schedule_hash,))
            if cursor.fetchone():
                return False  # Duplicate

            # Calculate schedule statistics
            stats = compute_schedule_stats(schedule)

            # Prepare data
            course_codes = json.dumps([course.code for course in schedule.courses])
            schedule_data = self._serialize_schedule(schedule)
            free_days = json.dumps(stats.free_days)

            # Insert schedule
            cursor.execute('''
                INSERT INTO schedules (
                    schedule_hash, course_codes, total_credits, conflict_count,
                    days_used, total_gaps, free_days, schedule_data, generation_params
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                schedule_hash, course_codes, schedule.total_credits, schedule.conflict_count,
                stats.days_used, sum(stats.gaps_per_day.values()), free_days,
                schedule_data, params_json
            ))

            # Update course statistics
            self._update_course_stats(cursor, schedule)

            return True

        except Exception as e:
            logger.error(f"Error adding single schedule: {e}")
            return False

    def _calculate_schedule_hash(self, schedule: Schedule) -> str:
        """Calculate a unique hash for the schedule based on course codes and times."""
        import hashlib

        # Create a consistent string representation
        course_data = []
        for course in sorted(schedule.courses, key=lambda c: c.code):
            schedule_str = ','.join(f"{day}{slot}" for day, slot in sorted(course.schedule))
            course_data.append(f"{course.code}:{schedule_str}")

        combined = '|'.join(course_data)
        return hashlib.md5(combined.encode()).hexdigest()

    def _serialize_schedule(self, schedule: Schedule) -> str:
        """Serialize schedule to JSON string."""
        schedule_dict = {
            'courses': [
                {
                    'code': course.code,
                    'name': course.name,
                    'ects': course.ects,
                    'course_type': course.course_type,
                    'schedule': course.schedule,
                    'teacher': course.teacher,
                    'faculty': getattr(course, 'faculty', ''),
                    'department': getattr(course, 'department', ''),
                    'campus': getattr(course, 'campus', '')
                }
                for course in schedule.courses
            ],
            'total_credits': schedule.total_credits,
            'conflict_count': schedule.conflict_count
        }
        return json.dumps(schedule_dict)

    def _update_course_stats(self, cursor, schedule: Schedule):
        """Update course usage statistics."""
        try:
            for course in schedule.courses:
                # Insert or update course stats
                cursor.execute('''
                    INSERT OR REPLACE INTO course_stats (
                        course_code, course_name, course_type, faculty, department,
                        usage_count, last_used
                    ) VALUES (?, ?, ?, ?, ?, 
                        COALESCE((SELECT usage_count FROM course_stats WHERE course_code = ?) + 1, 1),
                        CURRENT_TIMESTAMP
                    )
                ''', (
                    course.code, course.name, course.course_type,
                    getattr(course, 'faculty', ''), getattr(course, 'department', ''),
                    course.code
                ))

        except Exception as e:
            logger.error(f"Error updating course stats: {e}")

    def get_schedules_with_filters(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get schedules with advanced filtering.

        Args:
            filters: Dictionary of filter criteria

        Returns:
            List of schedule dictionaries matching the criteria
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()

                # Build WHERE clause based on filters
                where_conditions = []
                params = []

                if 'min_credits' in filters:
                    where_conditions.append('total_credits >= ?')
                    params.append(filters['min_credits'])

                if 'max_credits' in filters:
                    where_conditions.append('total_credits <= ?')
                    params.append(filters['max_credits'])

                if 'max_conflicts' in filters:
                    where_conditions.append('conflict_count <= ?')
                    params.append(filters['max_conflicts'])

                if 'required_free_days' in filters:
                    # Filter schedules that have all required free days
                    free_days_filter = filters['required_free_days']
                    if free_days_filter:
                        for day in free_days_filter:
                            where_conditions.append('free_days LIKE ?')
                            params.append(f'%"{day}"%')

                if 'max_days_used' in filters:
                    where_conditions.append('days_used <= ?')
                    params.append(filters['max_days_used'])

                if 'course_codes' in filters:
                    # Filter schedules containing specific courses
                    for code in filters['course_codes']:
                        where_conditions.append('course_codes LIKE ?')
                        params.append(f'%"{code}"%')

                # Build and execute query
                query = 'SELECT * FROM schedules'
                if where_conditions:
                    query += ' WHERE ' + ' AND '.join(where_conditions)

                query += ' ORDER BY created_at DESC'

                if 'limit' in filters:
                    query += f' LIMIT {filters["limit"]}'

                cursor.execute(query, params)
                rows = cursor.fetchall()

                # Convert to list of dictionaries
                results = []
                for row in rows:
                    result = dict(row)
                    # Parse JSON fields
                    result['course_codes'] = json.loads(result['course_codes'])
                    result['free_days'] = json.loads(result['free_days'])
                    if result['generation_params']:
                        result['generation_params'] = json.loads(result['generation_params'])
                    results.append(result)

                logger.info(f"Retrieved {len(results)} schedules with filters")
                return results

        except Exception as e:
            logger.error(f"Error filtering schedules: {e}")
            return []

    def get_schedule_by_id(self, schedule_id: int) -> Optional[Schedule]:
        """
        Retrieve a specific schedule by ID.

        Args:
            schedule_id: Database ID of the schedule

        Returns:
            Schedule object or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT schedule_data FROM schedules WHERE id = ?', (schedule_id,))
                row = cursor.fetchone()

                if row:
                    schedule_data = json.loads(row[0])
                    return self._deserialize_schedule(schedule_data)

        except Exception as e:
            logger.error(f"Error retrieving schedule {schedule_id}: {e}")

        return None

    def _deserialize_schedule(self, schedule_data: Dict[str, Any]) -> Schedule:
        """Deserialize schedule from dictionary."""
        courses = []
        for course_data in schedule_data['courses']:
            course = Course(
                code=course_data['code'],
                main_code=course_data['code'].split('-')[0],  # Extract main code
                name=course_data['name'],
                ects=course_data['ects'],
                course_type=course_data['course_type'],
                schedule=course_data['schedule'],
                teacher=course_data['teacher'],
                faculty=course_data.get('faculty', ''),
                department=course_data.get('department', ''),
                campus=course_data.get('campus', '')
            )
            courses.append(course)

        return Schedule(courses)

    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Basic counts
                cursor.execute('SELECT COUNT(*) FROM schedules')
                total_schedules = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(DISTINCT course_code) FROM course_stats')
                unique_courses = cursor.fetchone()[0]

                # Schedule statistics
                cursor.execute('''
                    SELECT 
                        AVG(total_credits) as avg_credits,
                        MIN(total_credits) as min_credits,
                        MAX(total_credits) as max_credits,
                        AVG(conflict_count) as avg_conflicts,
                        AVG(days_used) as avg_days_used,
                        COUNT(*) as conflict_free_count
                    FROM schedules 
                    WHERE conflict_count = 0
                ''')
                schedule_stats = cursor.fetchone()

                # Most popular courses
                cursor.execute('''
                    SELECT course_code, course_name, usage_count
                    FROM course_stats
                    ORDER BY usage_count DESC
                    LIMIT 10
                ''')
                popular_courses = cursor.fetchall()

                return {
                    'total_schedules': total_schedules,
                    'unique_courses': unique_courses,
                    'avg_credits': round(schedule_stats[0] or 0, 2),
                    'credit_range': (schedule_stats[1] or 0, schedule_stats[2] or 0),
                    'avg_conflicts': round(schedule_stats[3] or 0, 2),
                    'avg_days_used': round(schedule_stats[4] or 0, 2),
                    'conflict_free_schedules': schedule_stats[5] or 0,
                    'popular_courses': [
                        {'code': row[0], 'name': row[1], 'usage': row[2]}
                        for row in popular_courses
                    ]
                }

        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

    def export_schedules_analysis(self, output_path: str, filters: Dict[str, Any] = None) -> bool:
        """
        Export schedule analysis to Excel file.

        Args:
            output_path: Path for the output Excel file
            filters: Optional filters to apply

        Returns:
            True if successful
        """
        try:
            import pandas as pd

            # Get filtered schedules
            schedules = self.get_schedules_with_filters(filters or {})

            if not schedules:
                logger.warning("No schedules to export")
                return False

            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Schedule summary
                summary_data = []
                for i, schedule in enumerate(schedules, 1):
                    summary_data.append({
                        'Schedule_ID': schedule['id'],
                        'Total_Credits': schedule['total_credits'],
                        'Conflicts': schedule['conflict_count'],
                        'Days_Used': schedule['days_used'],
                        'Total_Gaps': schedule['total_gaps'],
                        'Free_Days': ', '.join(schedule['free_days']),
                        'Course_Count': len(schedule['course_codes']),
                        'Created_At': schedule['created_at']
                    })

                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Schedule_Summary', index=False)

                # Database statistics
                stats = self.get_database_stats()
                stats_df = pd.DataFrame([stats])
                stats_df.to_excel(writer, sheet_name='Database_Stats', index=False)

            logger.info(f"Exported {len(schedules)} schedules to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting schedules: {e}")
            return False

    def clear_old_schedules(self, days_old: int = 30) -> int:
        """
        Clear schedules older than specified days.

        Args:
            days_old: Number of days to keep

        Returns:
            Number of deleted schedules
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    DELETE FROM schedules 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days_old))

                deleted_count = cursor.rowcount
                conn.commit()

                logger.info(f"Cleared {deleted_count} old schedules")
                return deleted_count

        except Exception as e:
            logger.error(f"Error clearing old schedules: {e}")
            return 0
