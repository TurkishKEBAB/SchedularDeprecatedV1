"""
Core data models for the course scheduler application.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Set
from enum import Enum


class CourseType(Enum):
    """Course type enumeration."""
    LECTURE = "lecture"
    PS = "ps"
    LAB = "lab"


class Frequency(Enum):
    """Frequency preference enumeration."""
    NEVER = 0
    RARELY = 1
    OFTEN = 2
    ALWAYS = 3


@dataclass
class Course:
    """Represents a single course with all its properties."""
    code: str
    main_code: str
    name: str
    ects: int
    course_type: CourseType
    schedule: List[Tuple[str, int]]  # List of (day, hour) tuples
    teacher: str = "Default"
    faculty: str = "Unknown Faculty"
    department: str = "Unknown Department"
    campus: str = "Main Campus"

    @property
    def has_lecture(self) -> bool:
        """Check if this is a lecture course."""
        return self.course_type == CourseType.LECTURE

    @property
    def type(self):  # legacy compatibility for rules.py expecting .type
        return self.course_type

    def conflicts_with(self, other: 'Course') -> bool:
        """Check if this course conflicts with another course."""
        return bool(set(self.schedule) & set(other.schedule))

    def to_dict(self) -> Dict:
        """Convert to dictionary format for backward compatibility."""
        return {
            "code": self.code,
            "main_code": self.main_code,
            "name": self.name,
            "ECTS": self.ects,
            "type": self.course_type.value,
            "schedule": self.schedule,
            "hasLecture": self.has_lecture,
            "teacher": self.teacher,
            "faculty": self.faculty,
            "department": self.department,
            "campus": self.campus
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Course':
        """Create Course from dictionary format."""
        return cls(
            code=data.get("code", ""),
            main_code=data.get("main_code", ""),
            name=data.get("name", ""),
            ects=data.get("ECTS", 0),
            course_type=CourseType(data.get("type", "lecture")),
            schedule=data.get("schedule", []),
            teacher=data.get("teacher", "Default"),
            faculty=data.get("faculty", "Unknown Faculty"),
            department=data.get("department", "Unknown Department"),
            campus=data.get("campus", "Main Campus")
        )


@dataclass
class CourseGroup:
    """Represents a group of related courses (lecture, PS, lab sections)."""
    main_code: str
    courses: List[Course] = field(default_factory=list)

    @property
    def lectures(self) -> List[Course]:
        """Get all lecture courses in this group."""
        return [c for c in self.courses if c.course_type == CourseType.LECTURE]

    @property
    def ps_sections(self) -> List[Course]:
        """Get all PS sections in this group."""
        return [c for c in self.courses if c.course_type == CourseType.PS]

    @property
    def lab_sections(self) -> List[Course]:
        """Get all lab sections in this group."""
        return [c for c in self.courses if c.course_type == CourseType.LAB]

    @property
    def has_lecture(self) -> bool:
        """Check if this group has any lecture courses."""
        return len(self.lectures) > 0


@dataclass
class FilterProfile:
    """Represents a set of course filters."""
    query: str = ""
    faculty: str = "All"
    department: str = "All"
    campus: str = "All"
    ects_min: int = 0
    ects_max: int = 50
    days: List[str] = field(default_factory=lambda: ["M", "T", "W", "Th", "F", "Sa", "Su"])
    slots: List[int] = field(default_factory=lambda: list(range(1, 13)))
    restricted: bool = True

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            "query": self.query,
            "faculty": self.faculty,
            "department": self.department,
            "campus": self.campus,
            "ects_min": self.ects_min,
            "ects_max": self.ects_max,
            "days": self.days,
            "slots": self.slots,
            "restricted": self.restricted
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'FilterProfile':
        """Create FilterProfile from dictionary."""
        return cls(
            query=data.get("query", ""),
            faculty=data.get("faculty", "All"),
            department=data.get("department", "All"),
            campus=data.get("campus", "All"),
            ects_min=data.get("ects_min", 0),
            ects_max=data.get("ects_max", 50),
            days=data.get("days", ["M", "T", "W", "Th", "F", "Sa", "Su"]),
            slots=data.get("slots", list(range(1, 13))),
            restricted=data.get("restricted", True)
        )


class SelectionState(Enum):
    """Tri-state selection for legacy rules integration."""
    INCLUDE = "include"
    EXCLUDE = "exclude"
    NEUTRAL = "neutral"


@dataclass
class CourseSelection:
    """Represents a user's selection state for a course group (legacy compatibility)."""
    main_code: str
    state: SelectionState = SelectionState.NEUTRAL
    frequency: int = 3  # Default to "Always" (0=Never, 1=Rarely, 2=Often, 3=Always)
    teacher_preference: str = "Any"  # Preferred teacher or "Any"


@dataclass
class SchedulerConfig:
    """Configuration for the scheduler."""
    max_ects: int = 31
    allow_conflict: int = 1  # Pairwise conflict count allowed
    max_results: int = 5
    priority: List[str] = field(default_factory=lambda: ["lecture", "ps", "lab"])
    replacement_target: str = "sections"  # "sections" or "course"
    use_simulated_annealing: bool = False
    count_optional: bool = False

    # New configuration flags
    require_all_sections: bool = False  # If True, PS/Lab required when present (old behavior)
    optimize_diversity: bool = True     # Enable diversity filtering
    balance_workload: bool = True       # Enable workload balancing
    auto_limit_weekend_bias: bool = True  # Future use: scoring adjustment

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            "MAX_ECTS": self.max_ects,
            "ALLOW_CONFLICT": self.allow_conflict,
            "MAX_RESULTS": self.max_results,
            "replacement_target": self.replacement_target,
            "priority": self.priority,
            "use_simulated_annealing": self.use_simulated_annealing,
            "count_optional": self.count_optional,
            "require_all_sections": self.require_all_sections,
            "optimize_diversity": self.optimize_diversity,
            "balance_workload": self.balance_workload,
            "auto_limit_weekend_bias": self.auto_limit_weekend_bias,
        }


# Backward compatibility alias for legacy rules module
Config = SchedulerConfig


@dataclass
class Schedule:
    """Represents a complete course schedule."""
    courses: List[Course]
    total_ects: int = 0
    conflict_cost: int = 0  # Pairwise conflict count
    slot_conflict_cost: int = 0  # Overlapping slot overage count

    def __post_init__(self):
        """Calculate totals after initialization."""
        self.total_ects = sum(c.ects for c in self.courses)
        self.conflict_cost = self.calculate_conflict_cost()
        self.slot_conflict_cost = self.calculate_slot_conflict_cost()

    def calculate_conflict_cost(self) -> int:
        """Calculate the pairwise conflict cost of this schedule."""
        conflicts = 0
        for i, course1 in enumerate(self.courses):
            for course2 in self.courses[i+1:]:
                if course1.conflicts_with(course2):
                    conflicts += 1
        return conflicts

    def calculate_slot_conflict_cost(self) -> int:
        """Calculate slot-based overlaps (sum over max(0, count-1) per slot)."""
        slot_counts: Dict[Tuple[str, int], int] = {}
        for course in self.courses:
            for slot in course.schedule:
                slot_counts[slot] = slot_counts.get(slot, 0) + 1
        return sum(max(0, c - 1) for c in slot_counts.values())

    def get_daily_schedule(self) -> Dict[str, List[Tuple[int, Course]]]:
        """Get courses organized by day and time."""
        daily = {}
        for course in self.courses:
            for day, hour in course.schedule:
                if day not in daily:
                    daily[day] = []
                daily[day].append((hour, course))

        # Sort by hour for each day
        for day in daily:
            daily[day].sort(key=lambda x: x[0])

        return daily

    def has_conflicts(self) -> bool:
        """Check if schedule has any conflicts."""
        return self.conflict_cost > 0

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            "courses": [c.to_dict() for c in self.courses],
            "total_ects": self.total_ects,
            "conflict_cost": self.conflict_cost,
            "slot_conflict_cost": self.slot_conflict_cost,
            "has_conflicts": self.has_conflicts()
        }


@dataclass
class ScheduleStats:
    """Statistics for a set of schedules."""
    total_schedules: int = 0
    avg_ects: float = 0.0
    min_ects: int = 0
    max_ects: int = 0
    conflict_free_schedules: int = 0
    most_common_courses: List[Tuple[str, int]] = field(default_factory=list)
    faculty_distribution: Dict[str, int] = field(default_factory=dict)
    time_distribution: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_schedules(cls, schedules: List[Schedule]) -> 'ScheduleStats':
        """Calculate statistics from a list of schedules."""
        if not schedules:
            return cls()

        total_schedules = len(schedules)
        ects_values = [s.total_ects for s in schedules]
        avg_ects = sum(ects_values) / len(ects_values)
        min_ects = min(ects_values)
        max_ects = max(ects_values)

        conflict_free = sum(1 for s in schedules if not s.has_conflicts())

        # Course frequency analysis
        course_counts = {}
        faculty_counts = {}
        time_counts = {}

        for schedule in schedules:
            for course in schedule.courses:
                course_counts[course.code] = course_counts.get(course.code, 0) + 1
                faculty_counts[course.faculty] = faculty_counts.get(course.faculty, 0) + 1

                for day, hour in course.schedule:
                    time_key = f"{day}-{hour}"
                    time_counts[time_key] = time_counts.get(time_key, 0) + 1

        most_common = sorted(course_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return cls(
            total_schedules=total_schedules,
            avg_ects=avg_ects,
            min_ects=min_ects,
            max_ects=max_ects,
            conflict_free_schedules=conflict_free,
            most_common_courses=most_common,
            faculty_distribution=faculty_counts,
            time_distribution=time_counts
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            "total_schedules": self.total_schedules,
            "avg_ects": round(self.avg_ects, 2),
            "min_ects": self.min_ects,
            "max_ects": self.max_ects,
            "conflict_free_schedules": self.conflict_free_schedules,
            "conflict_free_percentage": round((self.conflict_free_schedules / max(1, self.total_schedules)) * 100, 2),
            "most_common_courses": self.most_common_courses,
            "faculty_distribution": self.faculty_distribution,
            "time_distribution": self.time_distribution
        }


@dataclass
class ConflictReport:
    """Detailed conflict analysis for schedules."""
    total_conflicts: int = 0
    conflict_pairs: List[Tuple[str, str]] = field(default_factory=list)
    time_conflicts: Dict[str, List[str]] = field(default_factory=dict)
    severity_breakdown: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> 'ConflictReport':
        """Generate conflict report from a schedule."""
        total_conflicts = 0
        conflict_pairs = []
        time_conflicts = {}

        for i, course1 in enumerate(schedule.courses):
            for course2 in schedule.courses[i+1:]:
                if course1.conflicts_with(course2):
                    total_conflicts += 1
                    conflict_pairs.append((course1.code, course2.code))

                    # Find specific time conflicts
                    common_times = set(course1.schedule) & set(course2.schedule)
                    for day, hour in common_times:
                        time_key = f"{day}-{hour}"
                        if time_key not in time_conflicts:
                            time_conflicts[time_key] = []
                        time_conflicts[time_key].extend([course1.code, course2.code])

        # Categorize severity
        severity = {
            "low": 0,
            "medium": 0,
            "high": 0
        }

        if total_conflicts <= 1:
            severity["low"] = total_conflicts
        elif total_conflicts <= 3:
            severity["medium"] = total_conflicts
        else:
            severity["high"] = total_conflicts

        return cls(
            total_conflicts=total_conflicts,
            conflict_pairs=conflict_pairs,
            time_conflicts=time_conflicts,
            severity_breakdown=severity
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            "total_conflicts": self.total_conflicts,
            "conflict_pairs": self.conflict_pairs,
            "time_conflicts": self.time_conflicts,
            "severity_breakdown": self.severity_breakdown
        }


@dataclass
class UserPreferences:
    """User preferences for course selection and automatic section assignment."""
    mandatory_courses: Set[str] = field(default_factory=set)
    frequency_prefs: Dict[str, Frequency] = field(default_factory=dict)
    teacher_prefs: Dict[str, str] = field(default_factory=dict)

    # New fields for automatic section selection
    auto_select_sections: bool = True
    prefer_early_times: bool = True
    avoid_friday_classes: bool = False
    prefer_morning_classes: bool = True
    avoid_evening_classes: bool = False
    max_daily_courses: int = 4
    min_break_between_courses: int = 0  # Hours
    prefer_compact_schedule: bool = True

    # Legacy compatibility
    include_extra: bool = True

    def get_frequency(self, main_code: str) -> Frequency:
        """Get frequency preference for a course."""
        return self.frequency_prefs.get(main_code, Frequency.OFTEN)

    def get_teacher_preference(self, main_code: str) -> str:
        """Get teacher preference for a course."""
        return self.teacher_prefs.get(main_code, "")

    def should_auto_select_sections(self) -> bool:
        """Check if automatic section selection is enabled."""
        return self.auto_select_sections

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            "mandatory_courses": list(self.mandatory_courses),
            "frequency_prefs": {k: v.value for k, v in self.frequency_prefs.items()},
            "teacher_prefs": self.teacher_prefs,
            "auto_select_sections": self.auto_select_sections,
            "prefer_early_times": self.prefer_early_times,
            "avoid_friday_classes": self.avoid_friday_classes,
            "prefer_morning_classes": self.prefer_morning_classes,
            "avoid_evening_classes": self.avoid_evening_classes,
            "max_daily_courses": self.max_daily_courses,
            "min_break_between_courses": self.min_break_between_courses,
            "prefer_compact_schedule": self.prefer_compact_schedule,
            "include_extra": self.include_extra
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserPreferences':
        """Create UserPreferences from dictionary."""
        frequency_prefs = {}
        for k, v in data.get("frequency_prefs", {}).items():
            frequency_prefs[k] = Frequency(v) if isinstance(v, int) else Frequency[v]

        return cls(
            mandatory_courses=set(data.get("mandatory_courses", [])),
            frequency_prefs=frequency_prefs,
            teacher_prefs=data.get("teacher_prefs", {}),
            auto_select_sections=data.get("auto_select_sections", True),
            prefer_early_times=data.get("prefer_early_times", True),
            avoid_friday_classes=data.get("avoid_friday_classes", False),
            prefer_morning_classes=data.get("prefer_morning_classes", True),
            avoid_evening_classes=data.get("avoid_evening_classes", False),
            max_daily_courses=data.get("max_daily_courses", 4),
            min_break_between_courses=data.get("min_break_between_courses", 0),
            prefer_compact_schedule=data.get("prefer_compact_schedule", True),
            include_extra=data.get("include_extra", True)
        )


# Compatibility class for backward compatibility
@dataclass
class SnapshotInfo:
    """Information about a saved snapshot."""
    id: int
    created_at: str
    course_count: int
    description: str
