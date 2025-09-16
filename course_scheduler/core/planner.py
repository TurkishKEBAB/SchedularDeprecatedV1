"""
Core scheduling algorithms including DFS and Simulated Annealing.
"""

import random
import math
import logging
from typing import List, Dict, Optional
from collections import defaultdict

from .models import Course, CourseGroup, Schedule, SchedulerConfig, UserPreferences, Frequency
from . import rules  # integrate legacy rules usage

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

    def _get_course_constraints(self, main_code: str) -> Dict[str, bool]:
        """Get constraints for a course (PS/Lab requirements) honoring config.

        If config.require_all_sections is False, PS/Lab become optional even if they exist.
        """
        group = self.course_groups.get(main_code)
        if not group:
            return {"must_ps": False, "must_lab": False}

        if self.config.require_all_sections:
            return {
                "must_ps": len(group.ps_sections) > 0,
                "must_lab": len(group.lab_sections) > 0
            }
        else:
            return {"must_ps": False, "must_lab": False}

    def generate_valid_group_selections(self, group: CourseGroup) -> List[List[Course]]:
        """Generate all valid selections for a course group with optional sections.

        Enhancement:
        - If no lecture present, treat each non-lecture course as a standalone selectable unit.
        - Avoid duplicate selections.
        """
        if not group.has_lecture:
            unique = []
            seen_codes = set()
            for c in group.courses:
                if c.code not in seen_codes:
                    seen_codes.add(c.code)
                    unique.append([c])
            return unique

        valid_selections: List[List[Course]] = []
        seen_signature = set()

        for lecture in group.lectures:
            base_selection = [lecture]
            constraints = self._get_course_constraints(lecture.main_code)
            must_ps = constraints.get("must_ps", False)
            must_lab = constraints.get("must_lab", False)

            ps_options = group.ps_sections if must_ps else [None] + group.ps_sections
            lab_options = group.lab_sections if must_lab else [None] + group.lab_sections

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
                    sig = tuple(sorted(c.code for c in selection))
                    if sig not in seen_signature:
                        seen_signature.add(sig)
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

    def calculate_schedule_fitness(self, schedule: Schedule) -> float:
        """Calculate fitness score for a schedule (higher is better).

        Adjusted weights, includes slot conflict penalties and mild weekend balancing.
        """
        fitness = 0.0

        # Base fitness from ECTS (prefer near but not over limit)
        distance = max(0, self.config.max_ects - schedule.total_ects)
        fitness += max(0, 500 - distance * 15)  # non-linear diminishing

        # Pairwise conflict penalty
        fitness -= schedule.conflict_cost * 80
        # Slot overlap penalty (harsher for stacking same slot)
        fitness -= schedule.slot_conflict_cost * 40

        # Preference weighting
        for course in schedule.courses:
            frequency = self.preferences.get_frequency(course.main_code)
            if frequency == Frequency.ALWAYS:
                fitness += 60
            elif frequency == Frequency.OFTEN:
                fitness += 30
            elif frequency == Frequency.RARELY:
                fitness -= 20
            elif frequency == Frequency.NEVER:
                fitness -= 80

        # Over-limit harsh penalty
        if schedule.total_ects > self.config.max_ects:
            fitness -= (schedule.total_ects - self.config.max_ects) * 120

        # Workload balance (weekdays only)
        daily_schedule = schedule.get_daily_schedule()
        weekday_order = ["M", "T", "W", "Th", "F"]
        daily_counts = [len(daily_schedule.get(day, [])) for day in weekday_order]
        if daily_counts:
            avg_daily = sum(daily_counts) / len(daily_counts)
            variance = sum((c - avg_daily) ** 2 for c in daily_counts) / len(daily_counts)
            fitness += max(0, 100 - variance * 10)

        # Weekend usage moderation (optional future flag)
        if self.config.auto_limit_weekend_bias:
            weekend_load = len(daily_schedule.get("Sa", [])) + len(daily_schedule.get("Su", []))
            if weekend_load > 0:
                fitness -= weekend_load * 10

        return fitness

    def generate_schedules_dfs(self, courses: List[Course]) -> List[Schedule]:
        """Generate schedules using Depth-First Search with strict conflict control and rules validation."""
        logger.info("Starting DFS schedule generation")
        self.build_course_groups(courses)
        self.build_group_options()

        schedules: List[Schedule] = []
        main_codes = list(self.group_options.keys())

        logger.info(f"DFS Config: max_ects={self.config.max_ects}, allow_conflict={self.config.allow_conflict}")

        def calculate_actual_conflicts(courses_list: List[Course]) -> int:
            conflicts = 0
            for i, course1 in enumerate(courses_list):
                for course2 in courses_list[i+1:]:
                    if course1.conflicts_with(course2):
                        conflicts += 1
            return conflicts

        def dfs(index: int, current_courses: List[Course]):
            # Stop if we have enough schedules
            if len(schedules) >= self.config.max_results * 4:  # generate surplus for optimizer diversity
                return

            # Base case: processed all course groups
            if index == len(main_codes):
                if not current_courses:
                    return

                # Calculate actual conflicts
                actual_conflicts = calculate_actual_conflicts(current_courses)
                current_ects = sum(c.ects for c in current_courses)

                # Strict validation
                if (actual_conflicts <= self.config.allow_conflict and
                    current_ects <= self.config.max_ects):

                    schedule = Schedule(courses=current_courses.copy())

                    # Legacy rules validation
                    valid, violations = rules.validate_schedule_constraints(schedule.courses, self.config)
                    if valid:
                        score = rules.calculate_schedule_score(schedule.courses, self.config)
                        if not hasattr(schedule, 'metadata'):
                            schedule.metadata = {}
                        schedule.metadata['rule_score'] = score
                        schedules.append(schedule)
                    else:
                        logger.debug(f"Rules rejected schedule: {violations}")
                return

            main_code = main_codes[index]
            options = self.group_options[main_code]

            # Process each option for this course group
            for option in options:
                if option is None:
                    # Skip this course group
                    dfs(index + 1, current_courses)
                else:
                    added_ects = sum(c.ects for c in option)
                    new_ects = sum(c.ects for c in current_courses) + added_ects

                    # Early ECTS check
                    if new_ects > self.config.max_ects:
                        continue

                    # Create temporary course list to check conflicts
                    temp_courses = current_courses + option
                    if calculate_actual_conflicts(temp_courses) > self.config.allow_conflict:
                        continue

                    current_courses.extend(option)
                    dfs(index + 1, current_courses)
                    for _ in option:
                        current_courses.pop()

        dfs(0, [])

        # Sort by combined fitness (modern) then legacy rule score if present
        schedules.sort(key=lambda s: (self.calculate_schedule_fitness(s), getattr(s.metadata, 'rule_score', 0)), reverse=True)

        # De-duplicate by code signature
        unique: Dict[frozenset, Schedule] = {}
        for s in schedules:
            sig = frozenset(c.code for c in s.courses)
            if sig not in unique:
                unique[sig] = s
        final_list = list(unique.values())
        logger.info(f"DFS produced {len(final_list)} unique rule-valid schedules (raw {len(schedules)})")
        return final_list[: max(self.config.max_results * 2, self.config.max_results)]

    def generate_schedules_sa(self, courses: List[Course]) -> List[Schedule]:
        """Generate schedules using Simulated Annealing with constraint enforcement and rules validation."""
        logger.info("Starting Simulated Annealing schedule generation")
        self.build_course_groups(courses)
        self.build_group_options()
        if not self.group_options:
            return []
        current_solution = self._generate_random_solution()
        if not current_solution:
            return []
        best_solution = current_solution
        best_fitness = self.calculate_schedule_fitness(current_solution)
        if not hasattr(best_solution, 'metadata'):
            best_solution.metadata = {}
        best_solution.metadata['rule_score'] = rules.calculate_schedule_score(best_solution.courses, self.config)
        initial_temp = 300.0
        final_temp = 1.0
        cooling_rate = 0.92
        max_iterations = 800
        temperature = initial_temp
        solutions = [best_solution]
        seen_signatures = {frozenset(c.code for c in best_solution.courses)}
        for _ in range(max_iterations):
            neighbor = self._generate_neighbor_solution(current_solution)
            if not neighbor:
                temperature *= cooling_rate
                if temperature < final_temp:
                    break
                continue
            if (neighbor.total_ects > self.config.max_ects or
                neighbor.conflict_cost > self.config.allow_conflict or
                neighbor.slot_conflict_cost > self.config.allow_conflict):
                temperature *= cooling_rate
                if temperature < final_temp:
                    break
                continue
            valid, violations = rules.validate_schedule_constraints(neighbor.courses, self.config)
            if not valid:
                temperature *= cooling_rate
                if temperature < final_temp:
                    break
                continue
            if not hasattr(neighbor, 'metadata'):
                neighbor.metadata = {}
            neighbor.metadata['rule_score'] = rules.calculate_schedule_score(neighbor.courses, self.config)
            current_fitness = self.calculate_schedule_fitness(current_solution)
            neighbor_fitness = self.calculate_schedule_fitness(neighbor)
            accept = False
            if neighbor_fitness >= current_fitness:
                accept = True
            else:
                try:
                    delta = neighbor_fitness - current_fitness
                    probability = math.exp(delta / max(0.001, temperature))
                    if random.random() < probability:
                        accept = True
                except OverflowError:
                    accept = False
            if accept:
                current_solution = neighbor
                if neighbor_fitness > best_fitness:
                    best_solution = neighbor
                    best_fitness = neighbor_fitness
                    sig = frozenset(c.code for c in neighbor.courses)
                    if sig not in seen_signatures:
                        seen_signatures.add(sig)
                        if len(solutions) < self.config.max_results * 3:
                            solutions.append(neighbor)
            temperature *= cooling_rate
            if temperature < final_temp:
                break
        filtered = [s for s in solutions if s.total_ects <= self.config.max_ects and s.conflict_cost <= self.config.allow_conflict and s.slot_conflict_cost <= self.config.allow_conflict]
        logger.info(f"SA generated {len(filtered)} valid schedules (kept {len(filtered)}/{len(solutions)})")
        return filtered[: max(self.config.max_results * 2, self.config.max_results)]

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
        """Main method to generate schedules with post-optimization."""
        if not courses:
            logger.warning("No courses provided for scheduling")
            return []

        logger.info(f"Generating schedules with {len(courses)} courses")
        logger.info(f"Config: max_ects={self.config.max_ects}, allow_conflict={self.config.allow_conflict}")
        logger.info(f"Mandatory courses: {len(self.preferences.mandatory_courses)}")

        try:
            if self.config.use_simulated_annealing:
                base_schedules = self.generate_schedules_sa(courses)
            else:
                base_schedules = self.generate_schedules_dfs(courses)

            validated: List[Schedule] = []
            for schedule in base_schedules:
                schedule_main_codes = {c.main_code for c in schedule.courses}
                if not (self.preferences.mandatory_courses - schedule_main_codes):
                    validated.append(schedule)

            validated.sort(key=lambda s: (self.calculate_schedule_fitness(s), getattr(getattr(s, 'metadata', {}), 'rule_score', 0)), reverse=True)

            optimizer = AdvancedScheduleOptimizer(self.config, self.preferences)
            optimized = validated
            if self.config.optimize_diversity:
                optimized = optimizer.optimize_schedule_diversity(optimized)
            if self.config.balance_workload:
                optimized = optimizer.balance_workload(optimized)

            optimized = optimized[: self.config.max_results]

            logger.info(f"Generated {len(optimized)} optimized schedules")
            return optimized

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
