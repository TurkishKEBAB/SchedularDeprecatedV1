"""
Core scheduling algorithms including DFS and Simulated Annealing.
"""

import random
import math
import logging
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict

from .models import Course, CourseGroup, Schedule, SchedulerConfig, UserPreferences, Frequency

logger = logging.getLogger(__name__)


class CourseScheduler:
    """Main scheduler class that handles course scheduling algorithms."""

    def __init__(self, config: SchedulerConfig, preferences: UserPreferences):
        self.config = config
        self.preferences = preferences
        self.course_groups: Dict[str, CourseGroup] = {}
        self.group_valid_selections: Dict[str, List[List[Course]]] = {}
        self.group_options: Dict[str, List[Optional[List[Course]]]] = {}

    def build_course_groups(self, courses: List[Course]) -> None:
        """Build course groups from the course list."""
        groups = defaultdict(list)
        for course in courses:
            groups[course.main_code].append(course)

        self.course_groups = {
            code: CourseGroup(main_code=code, courses=course_list)
            for code, course_list in groups.items()
        }

    def generate_valid_group_selections(self, group: CourseGroup) -> List[List[Course]]:
        """Generate all valid selections for a course group."""
        if not group.has_lecture:
            return []

        valid_selections = []

        for lecture in group.lectures:
            base_selection = [lecture]

            # Get constraints for this course
            constraints = self._get_course_constraints(lecture.main_code)
            must_ps = constraints.get("must_ps", False)
            must_lab = constraints.get("must_lab", False)

            ps_options = group.ps_sections if must_ps else [None] + group.ps_sections
            lab_options = group.lab_sections if must_lab else [None] + group.lab_sections

            # Skip if required sections are missing
            if must_ps and not group.ps_sections:
                continue
            if must_lab and not group.lab_sections:
                continue

            for ps in ps_options:
                for lab in lab_options:
                    selection = base_selection.copy()
                    if ps is not None:
                        selection.append(ps)
                    if lab is not None:
                        selection.append(lab)
                    valid_selections.append(selection)

        return valid_selections

    def build_group_options(self) -> None:
        """Build group options based on user preferences and constraints."""
        self.group_valid_selections = {}
        self.group_options = {}

        for main_code, group in self.course_groups.items():
            selections = self.generate_valid_group_selections(group)
            self.group_valid_selections[main_code] = selections

            if main_code in self.preferences.mandatory_courses:
                self.group_options[main_code] = selections
            else:
                self.group_options[main_code] = [None] + (selections if selections else [])

            # Restrict to first option if replacement target is "course"
            if self.config.replacement_target == "course":
                if self.group_options[main_code] and self.group_options[main_code][0] is not None:
                    self.group_options[main_code] = [self.group_options[main_code][0]]

    def _get_course_constraints(self, main_code: str) -> Dict[str, bool]:
        """Get constraints for a course (PS/Lab requirements)."""
        group = self.course_groups.get(main_code)
        if not group:
            return {"must_ps": False, "must_lab": False}

        return {
            "must_ps": len(group.ps_sections) > 0,
            "must_lab": len(group.lab_sections) > 0
        }

    def calculate_schedule_fitness(self, schedule: Schedule) -> float:
        """Calculate fitness score for a schedule (higher is better)."""
        fitness = 0.0

        # Base fitness from ECTS
        fitness += schedule.total_ects * 10

        # Penalty for conflicts
        fitness -= schedule.conflict_cost * 50

        # Bonus for user preferences
        for course in schedule.courses:
            frequency = self.preferences.get_frequency(course.main_code)
            if frequency == Frequency.ALWAYS:
                fitness += 100
            elif frequency == Frequency.OFTEN:
                fitness += 50
            elif frequency == Frequency.RARELY:
                fitness -= 25
            elif frequency == Frequency.NEVER:
                fitness -= 100

        # Penalty for exceeding ECTS limit
        if schedule.total_ects > self.config.max_ects:
            fitness -= (schedule.total_ects - self.config.max_ects) * 100

        # Bonus for balanced daily schedule
        daily_schedule = schedule.get_daily_schedule()
        daily_counts = [len(daily_schedule.get(day, [])) for day in ["M", "T", "W", "Th", "F"]]
        if daily_counts:
            avg_daily = sum(daily_counts) / len(daily_counts)
            variance = sum((count - avg_daily) ** 2 for count in daily_counts) / len(daily_counts)
            fitness += max(0, 20 - variance)  # Bonus for lower variance

        return fitness

    def generate_schedules_dfs(self, courses: List[Course]) -> List[Schedule]:
        """Generate schedules using Depth-First Search with strict conflict control."""
        logger.info("Starting DFS schedule generation")

        self.build_course_groups(courses)
        self.build_group_options()

        schedules = []
        main_codes = list(self.group_options.keys())

        logger.info(f"DFS Config: max_ects={self.config.max_ects}, allow_conflict={self.config.allow_conflict}")

        def calculate_actual_conflicts(courses_list: List[Course]) -> int:
            """Calculate actual number of time conflicts between courses."""
            conflicts = 0
            for i, course1 in enumerate(courses_list):
                for course2 in courses_list[i+1:]:
                    if course1.conflicts_with(course2):
                        conflicts += 1
            return conflicts

        def dfs(index: int, current_courses: List[Course]):
            # Stop if we have enough schedules
            if len(schedules) >= self.config.max_results:
                return

            # Base case: processed all course groups
            if index == len(main_codes):
                if current_courses:
                    # Calculate actual conflicts
                    actual_conflicts = calculate_actual_conflicts(current_courses)
                    current_ects = sum(c.ects for c in current_courses)

                    # Strict validation
                    if (actual_conflicts <= self.config.allow_conflict and
                        current_ects <= self.config.max_ects):

                        schedule = Schedule(courses=current_courses.copy())
                        schedules.append(schedule)
                        logger.debug(f"Valid schedule found: {len(current_courses)} courses, "
                                   f"{current_ects} ECTS, {actual_conflicts} conflicts")
                return

            main_code = main_codes[index]
            options = self.group_options[main_code]

            # Process each option for this course group
            for option in options:
                if option is None:
                    # Skip this course group
                    dfs(index + 1, current_courses)
                else:
                    # Try adding this course group
                    new_ects = sum(c.ects for c in current_courses) + sum(c.ects for c in option)

                    # Early ECTS check
                    if new_ects > self.config.max_ects:
                        continue

                    # Create temporary course list to check conflicts
                    temp_courses = current_courses + option
                    temp_conflicts = calculate_actual_conflicts(temp_courses)

                    # Early conflict check - strict enforcement
                    if temp_conflicts > self.config.allow_conflict:
                        continue

                    # Validate mandatory courses requirement
                    if main_code in self.preferences.mandatory_courses:
                        # Mandatory course - must include some option
                        current_courses.extend(option)
                        dfs(index + 1, current_courses)
                        # Backtrack
                        for _ in option:
                            current_courses.pop()
                    else:
                        # Optional course - try including it
                        current_courses.extend(option)
                        dfs(index + 1, current_courses)
                        # Backtrack
                        for _ in option:
                            current_courses.pop()

        # Start DFS
        dfs(0, [])

        # Sort schedules by fitness score
        schedules.sort(key=lambda s: self.calculate_schedule_fitness(s), reverse=True)

        # Validate all results one more time (paranoid check)
        valid_schedules = []
        for schedule in schedules:
            actual_conflicts = calculate_actual_conflicts(schedule.courses)
            if (actual_conflicts <= self.config.allow_conflict and
                schedule.total_ects <= self.config.max_ects):
                valid_schedules.append(schedule)
            else:
                logger.warning(f"Invalid schedule filtered out: {actual_conflicts} conflicts, "
                             f"{schedule.total_ects} ECTS")

        logger.info(f"DFS generated {len(valid_schedules)} valid schedules (filtered {len(schedules) - len(valid_schedules)})")
        return valid_schedules[:self.config.max_results]

    def generate_schedules_sa(self, courses: List[Course]) -> List[Schedule]:
        """Generate schedules using Simulated Annealing."""
        logger.info("Starting Simulated Annealing schedule generation")

        self.build_course_groups(courses)
        self.build_group_options()

        if not self.group_options:
            return []

        # Generate initial solution
        current_solution = self._generate_random_solution()
        if not current_solution:
            return []

        best_solution = current_solution
        best_fitness = self.calculate_schedule_fitness(current_solution)

        # SA parameters
        initial_temp = 1000.0
        final_temp = 1.0
        cooling_rate = 0.95
        max_iterations = 1000

        temperature = initial_temp
        solutions = [best_solution]

        for iteration in range(max_iterations):
            # Generate neighbor solution
            neighbor = self._generate_neighbor_solution(current_solution)
            if not neighbor:
                continue

            current_fitness = self.calculate_schedule_fitness(current_solution)
            neighbor_fitness = self.calculate_schedule_fitness(neighbor)

            # Accept or reject neighbor
            if neighbor_fitness > current_fitness:
                current_solution = neighbor
                if neighbor_fitness > best_fitness:
                    best_solution = neighbor
                    best_fitness = neighbor_fitness
                    if len(solutions) < self.config.max_results:
                        solutions.append(neighbor)
            else:
                # Accept worse solution with probability
                probability = math.exp((neighbor_fitness - current_fitness) / temperature)
                if random.random() < probability:
                    current_solution = neighbor

            # Cool down
            temperature *= cooling_rate
            if temperature < final_temp:
                break

        logger.info(f"SA generated {len(solutions)} unique schedules")
        return solutions[:self.config.max_results]

    def _generate_random_solution(self) -> Optional[Schedule]:
        """Generate a random valid solution."""
        courses = []
        total_ects = 0

        for main_code, options in self.group_options.items():
            if not options:
                continue

            # Higher probability for mandatory courses
            if main_code in self.preferences.mandatory_courses:
                prob = 0.9
            else:
                prob = 0.3

            if random.random() < prob and options:
                # Choose random option (skip None if mandatory)
                valid_options = [opt for opt in options if opt is not None] if main_code in self.preferences.mandatory_courses else options
                if valid_options:
                    option = random.choice(valid_options)
                    if option is not None:
                        option_ects = sum(c.ects for c in option)
                        if total_ects + option_ects <= self.config.max_ects + 5:
                            courses.extend(option)
                            total_ects += option_ects

        return Schedule(courses=courses) if courses else None

    def _generate_neighbor_solution(self, current: Schedule) -> Optional[Schedule]:
        """Generate a neighbor solution by modifying current solution."""
        if not current.courses:
            return None

        new_courses = current.courses.copy()

        # Choose modification type
        modification = random.choice(["add", "remove", "replace"])

        if modification == "add":
            # Try to add a new course group
            available_groups = [code for code in self.group_options.keys()
                              if not any(c.main_code == code for c in new_courses)]
            if available_groups:
                group_code = random.choice(available_groups)
                options = [opt for opt in self.group_options[group_code] if opt is not None]
                if options:
                    option = random.choice(options)
                    new_courses.extend(option)

        elif modification == "remove" and len(new_courses) > 1:
            # Remove a random course group
            group_to_remove = random.choice(list(set(c.main_code for c in new_courses)))
            new_courses = [c for c in new_courses if c.main_code != group_to_remove]

        elif modification == "replace":
            # Replace a course group with different sections
            if new_courses:
                group_to_replace = random.choice(list(set(c.main_code for c in new_courses)))
                new_courses = [c for c in new_courses if c.main_code != group_to_replace]

                options = [opt for opt in self.group_options[group_to_replace] if opt is not None]
                if options:
                    option = random.choice(options)
                    new_courses.extend(option)

        return Schedule(courses=new_courses) if new_courses else None

    def generate_schedules(self, courses: List[Course]) -> List[Schedule]:
        """Main method to generate schedules."""
        if not courses:
            logger.warning("No courses provided for scheduling")
            return []

        logger.info(f"Generating schedules with {len(courses)} courses")
        logger.info(f"Config: max_ects={self.config.max_ects}, allow_conflict={self.config.allow_conflict}")
        logger.info(f"Mandatory courses: {len(self.preferences.mandatory_courses)}")

        try:
            if self.config.use_simulated_annealing:
                schedules = self.generate_schedules_sa(courses)
            else:
                schedules = self.generate_schedules_dfs(courses)

            # Filter and validate results
            valid_schedules = []
            for schedule in schedules:
                if schedule.courses:  # Ensure schedule has courses
                    # Validate mandatory courses
                    schedule_main_codes = set(c.main_code for c in schedule.courses)
                    missing_mandatory = self.preferences.mandatory_courses - schedule_main_codes

                    if not missing_mandatory:  # All mandatory courses present
                        valid_schedules.append(schedule)
                    else:
                        logger.debug(f"Schedule missing mandatory courses: {missing_mandatory}")

            logger.info(f"Generated {len(valid_schedules)} valid schedules")
            return valid_schedules

        except Exception as e:
            logger.error(f"Error generating schedules: {e}")
            return []


class AdvancedScheduleOptimizer:
    """Advanced optimization techniques for schedule generation."""

    def __init__(self, config: SchedulerConfig, preferences: UserPreferences):
        self.config = config
        self.preferences = preferences

    def optimize_schedule_diversity(self, schedules: List[Schedule]) -> List[Schedule]:
        """Optimize for diverse schedule options."""
        if len(schedules) <= 1:
            return schedules

        diverse_schedules = [schedules[0]]  # Start with best schedule

        for schedule in schedules[1:]:
            if len(diverse_schedules) >= self.config.max_results:
                break

            # Check diversity with existing schedules
            is_diverse = True
            for existing in diverse_schedules:
                similarity = self._calculate_schedule_similarity(schedule, existing)
                if similarity > 0.8:  # Too similar
                    is_diverse = False
                    break

            if is_diverse:
                diverse_schedules.append(schedule)

        return diverse_schedules

    def _calculate_schedule_similarity(self, schedule1: Schedule, schedule2: Schedule) -> float:
        """Calculate similarity between two schedules (0.0 to 1.0)."""
        codes1 = set(c.code for c in schedule1.courses)
        codes2 = set(c.code for c in schedule2.courses)

        if not codes1 and not codes2:
            return 1.0
        if not codes1 or not codes2:
            return 0.0

        intersection = len(codes1 & codes2)
        union = len(codes1 | codes2)

        return intersection / union if union > 0 else 0.0

    def balance_workload(self, schedules: List[Schedule]) -> List[Schedule]:
        """Optimize schedules for balanced daily workload."""
        for schedule in schedules:
            daily_distribution = schedule.get_daily_schedule()

            # Calculate workload metrics
            daily_hours = {}
            for day, courses in daily_distribution.items():
                daily_hours[day] = len(courses)

            # Add workload metadata
            if not hasattr(schedule, 'metadata'):
                schedule.metadata = {}
            schedule.metadata['daily_hours'] = daily_hours
            schedule.metadata['max_daily_hours'] = max(daily_hours.values()) if daily_hours else 0
            schedule.metadata['workload_variance'] = self._calculate_workload_variance(daily_hours)

        # Sort by balanced workload
        schedules.sort(key=lambda s: (
            s.metadata.get('workload_variance', 0),
            s.metadata.get('max_daily_hours', 0)
        ))

        return schedules

    def _calculate_workload_variance(self, daily_hours: Dict[str, int]) -> float:
        """Calculate variance in daily workload."""
        if not daily_hours:
            return 0.0

        hours = list(daily_hours.values())
        mean = sum(hours) / len(hours)
        variance = sum((h - mean) ** 2 for h in hours) / len(hours)

        return variance
