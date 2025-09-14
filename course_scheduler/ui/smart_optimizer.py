"""
Intelligent Course Optimization System
Advanced features for smart course scheduling and optimization
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json

from ..core.models import Course, FilterProfile, SchedulerConfig

class OptimizationGoal(Enum):
    """Optimization goals for intelligent scheduling."""
    MINIMIZE_GAPS = "minimize_gaps"
    BALANCE_DAILY_LOAD = "balance_daily_load"
    PREFER_MORNING = "prefer_morning"
    PREFER_AFTERNOON = "prefer_afternoon"
    MINIMIZE_CAMPUS_CHANGES = "minimize_campus_changes"
    CLUSTER_BY_FACULTY = "cluster_by_faculty"

@dataclass
class SmartFilterProfile:
    """Enhanced filter profile with intelligent constraints."""
    basic_profile: FilterProfile
    preferred_days: List[str] = None
    avoided_days: List[str] = None
    preferred_time_ranges: List[Tuple[int, int]] = None  # (start_hour, end_hour)
    max_daily_courses: int = 4
    max_gap_hours: int = 2
    preferred_teachers: List[str] = None
    avoided_teachers: List[str] = None
    campus_preferences: Dict[str, int] = None  # campus -> priority (1-10)
    optimization_goals: List[OptimizationGoal] = None

class IntelligentOptimizer:
    """Intelligent course optimization engine."""

    def __init__(self):
        self.weight_factors = {
            OptimizationGoal.MINIMIZE_GAPS: 0.3,
            OptimizationGoal.BALANCE_DAILY_LOAD: 0.25,
            OptimizationGoal.PREFER_MORNING: 0.15,
            OptimizationGoal.PREFER_AFTERNOON: 0.15,
            OptimizationGoal.MINIMIZE_CAMPUS_CHANGES: 0.1,
            OptimizationGoal.CLUSTER_BY_FACULTY: 0.05
        }

    def optimize_course_selection(self, courses: List[Course],
                                profile: SmartFilterProfile) -> List[Course]:
        """Apply intelligent optimization to course selection."""
        optimized_courses = list(courses)

        # Apply time preferences
        if profile.preferred_time_ranges:
            optimized_courses = self._filter_by_time_ranges(
                optimized_courses, profile.preferred_time_ranges
            )

        # Apply day preferences
        if profile.preferred_days or profile.avoided_days:
            optimized_courses = self._filter_by_day_preferences(
                optimized_courses, profile.preferred_days, profile.avoided_days
            )

        # Apply teacher preferences
        if profile.preferred_teachers or profile.avoided_teachers:
            optimized_courses = self._filter_by_teacher_preferences(
                optimized_courses, profile.preferred_teachers, profile.avoided_teachers
            )

        # Score and rank courses based on optimization goals
        if profile.optimization_goals:
            optimized_courses = self._rank_by_optimization_goals(
                optimized_courses, profile.optimization_goals
            )

        return optimized_courses

    def _filter_by_time_ranges(self, courses: List[Course],
                              time_ranges: List[Tuple[int, int]]) -> List[Course]:
        """Filter courses by preferred time ranges."""
        filtered = []
        for course in courses:
            course_times = [hour for _, hour in course.schedule]
            if any(start <= hour <= end for start, end in time_ranges for hour in course_times):
                filtered.append(course)
        return filtered

    def _filter_by_day_preferences(self, courses: List[Course],
                                 preferred: List[str], avoided: List[str]) -> List[Course]:
        """Filter courses by day preferences."""
        filtered = []
        for course in courses:
            course_days = [day for day, _ in course.schedule]

            # Skip if any day is in avoided list
            if avoided and any(day in avoided for day in course_days):
                continue

            # Include if preferred days specified and course has preferred days
            if preferred:
                if any(day in preferred for day in course_days):
                    filtered.append(course)
            else:
                filtered.append(course)

        return filtered

    def _filter_by_teacher_preferences(self, courses: List[Course],
                                     preferred: List[str], avoided: List[str]) -> List[Course]:
        """Filter courses by teacher preferences."""
        filtered = []
        for course in courses:
            teacher_name = course.teacher.lower()

            # Skip if teacher is in avoided list
            if avoided and any(avoid.lower() in teacher_name for avoid in avoided):
                continue

            # Include if preferred teachers specified and course has preferred teacher
            if preferred:
                if any(pref.lower() in teacher_name for pref in preferred):
                    filtered.append(course)
            else:
                filtered.append(course)

        return filtered

    def _rank_by_optimization_goals(self, courses: List[Course],
                                  goals: List[OptimizationGoal]) -> List[Course]:
        """Rank courses based on optimization goals."""
        course_scores = []

        for course in courses:
            score = 0

            for goal in goals:
                weight = self.weight_factors.get(goal, 0.1)
                goal_score = self._calculate_goal_score(course, goal)
                score += weight * goal_score

            course_scores.append((course, score))

        # Sort by score (highest first)
        course_scores.sort(key=lambda x: x[1], reverse=True)

        return [course for course, _ in course_scores]

    def _calculate_goal_score(self, course: Course, goal: OptimizationGoal) -> float:
        """Calculate score for a specific optimization goal."""
        if goal == OptimizationGoal.PREFER_MORNING:
            morning_slots = sum(1 for _, hour in course.schedule if hour <= 6)
            return morning_slots / max(len(course.schedule), 1)

        elif goal == OptimizationGoal.PREFER_AFTERNOON:
            afternoon_slots = sum(1 for _, hour in course.schedule if hour >= 7)
            return afternoon_slots / max(len(course.schedule), 1)

        elif goal == OptimizationGoal.MINIMIZE_CAMPUS_CHANGES:
            # Courses on main campus get higher score
            return 1.0 if 'main' in course.campus.lower() else 0.5

        elif goal == OptimizationGoal.CLUSTER_BY_FACULTY:
            # Engineering courses get slightly higher score for clustering
            return 1.0 if 'engineering' in course.faculty.lower() else 0.8

        return 0.5  # Default score

class SmartSchedulingAssistant:
    """Smart scheduling assistant with AI-like recommendations."""

    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.optimizer = IntelligentOptimizer()
        self.current_profile = SmartFilterProfile(FilterProfile())
        self.courses = []

        self.setup_ui()

    def setup_ui(self):
        """Setup the smart scheduling assistant UI."""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title_label = ttk.Label(main_frame, text="🤖 Akıllı Ders Planlama Asistanı",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Create notebook for different optimization categories
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Time Preferences Tab
        self.setup_time_preferences_tab()

        # Day Preferences Tab
        self.setup_day_preferences_tab()

        # Teacher Preferences Tab
        self.setup_teacher_preferences_tab()

        # Optimization Goals Tab
        self.setup_optimization_goals_tab()

        # Results and Actions
        self.setup_results_section(main_frame)

    def setup_time_preferences_tab(self):
        """Setup time preferences tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⏰ Zaman Tercihleri")

        # Preferred time ranges
        time_frame = ttk.LabelFrame(frame, text="Tercih Edilen Zaman Aralıkları", padding=10)
        time_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(time_frame, text="Sabah (08:00-12:00):").grid(row=0, column=0, sticky="w")
        self.morning_var = tk.BooleanVar()
        ttk.Checkbutton(time_frame, variable=self.morning_var).grid(row=0, column=1)

        ttk.Label(time_frame, text="Öğle (12:00-16:00):").grid(row=1, column=0, sticky="w")
        self.afternoon_var = tk.BooleanVar()
        ttk.Checkbutton(time_frame, variable=self.afternoon_var).grid(row=1, column=1)

        ttk.Label(time_frame, text="Akşam (16:00-20:00):").grid(row=2, column=0, sticky="w")
        self.evening_var = tk.BooleanVar()
        ttk.Checkbutton(time_frame, variable=self.evening_var).grid(row=2, column=1)

        # Daily load settings
        load_frame = ttk.LabelFrame(frame, text="Günlük Yoğunluk", padding=10)
        load_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(load_frame, text="Günlük maksimum ders sayısı:").grid(row=0, column=0, sticky="w")
        self.max_daily_var = tk.IntVar(value=4)
        ttk.Spinbox(load_frame, from_=1, to=8, textvariable=self.max_daily_var,
                   width=10).grid(row=0, column=1, padx=5)

        ttk.Label(load_frame, text="Maksimum boşluk (saat):").grid(row=1, column=0, sticky="w")
        self.max_gap_var = tk.IntVar(value=2)
        ttk.Spinbox(load_frame, from_=0, to=5, textvariable=self.max_gap_var,
                   width=10).grid(row=1, column=1, padx=5)

    def setup_day_preferences_tab(self):
        """Setup day preferences tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📅 Gün Tercihleri")

        # Preferred days
        pref_frame = ttk.LabelFrame(frame, text="Tercih Edilen Günler", padding=10)
        pref_frame.pack(fill="x", padx=10, pady=5)

        self.day_vars = {}
        days = [("Pazartesi", "M"), ("Salı", "T"), ("Çarşamba", "W"),
                ("Perşembe", "Th"), ("Cuma", "F"), ("Cumartesi", "Sa")]

        for i, (day_tr, day_code) in enumerate(days):
            var = tk.BooleanVar(value=True)
            self.day_vars[day_code] = var
            ttk.Checkbutton(pref_frame, text=day_tr, variable=var).grid(
                row=i//3, column=i%3, sticky="w", padx=10, pady=2)

        # Special preferences
        special_frame = ttk.LabelFrame(frame, text="Özel Tercihler", padding=10)
        special_frame.pack(fill="x", padx=10, pady=5)

        self.no_friday_var = tk.BooleanVar()
        ttk.Checkbutton(special_frame, text="Cuma günü ders yok",
                       variable=self.no_friday_var).pack(anchor="w")

        self.no_weekend_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(special_frame, text="Hafta sonu ders yok",
                       variable=self.no_weekend_var).pack(anchor="w")

    def setup_teacher_preferences_tab(self):
        """Setup teacher preferences tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👨‍🏫 Öğretmen Tercihleri")

        # Preferred teachers
        pref_frame = ttk.LabelFrame(frame, text="Tercih Edilen Öğretmenler", padding=10)
        pref_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Label(pref_frame, text="Öğretmen adları (virgülle ayırın):").pack(anchor="w")
        self.preferred_teachers_text = tk.Text(pref_frame, height=4, wrap="word")
        self.preferred_teachers_text.pack(fill="x", pady=5)

        # Avoided teachers
        avoid_frame = ttk.LabelFrame(frame, text="Kaçınılacak Öğretmenler", padding=10)
        avoid_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Label(avoid_frame, text="Öğretmen adları (virgülle ayırın):").pack(anchor="w")
        self.avoided_teachers_text = tk.Text(avoid_frame, height=4, wrap="word")
        self.avoided_teachers_text.pack(fill="x", pady=5)

    def setup_optimization_goals_tab(self):
        """Setup optimization goals tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🎯 Optimizasyon Hedefleri")

        goals_frame = ttk.LabelFrame(frame, text="Akıllı Optimizasyon Seçenekleri", padding=10)
        goals_frame.pack(fill="x", padx=10, pady=5)

        self.goal_vars = {}
        goals = [
            (OptimizationGoal.MINIMIZE_GAPS, "Boşlukları minimize et"),
            (OptimizationGoal.BALANCE_DAILY_LOAD, "Günlük yükü dengele"),
            (OptimizationGoal.PREFER_MORNING, "Sabah derslerini tercih et"),
            (OptimizationGoal.PREFER_AFTERNOON, "Öğleden sonra derslerini tercih et"),
            (OptimizationGoal.MINIMIZE_CAMPUS_CHANGES, "Kampüs değişimini minimize et"),
            (OptimizationGoal.CLUSTER_BY_FACULTY, "Fakülteye göre grupla")
        ]

        for i, (goal, description) in enumerate(goals):
            var = tk.BooleanVar()
            self.goal_vars[goal] = var
            ttk.Checkbutton(goals_frame, text=description, variable=var).grid(
                row=i//2, column=i%2, sticky="w", padx=10, pady=5)

    def setup_results_section(self, parent):
        """Setup results and action buttons."""
        results_frame = ttk.LabelFrame(parent, text="Sonuçlar ve İşlemler", padding=10)
        results_frame.pack(fill="x", pady=(10, 0))

        # Action buttons
        button_frame = ttk.Frame(results_frame)
        button_frame.pack(fill="x")

        ttk.Button(button_frame, text="🤖 Akıllı Optimizasyon Uygula",
                  command=self.apply_smart_optimization,
                  style="Accent.TButton").pack(side="left", padx=(0, 5))

        ttk.Button(button_frame, text="💾 Profili Kaydet",
                  command=self.save_profile).pack(side="left", padx=5)

        ttk.Button(button_frame, text="📂 Profil Yükle",
                  command=self.load_profile).pack(side="left", padx=5)

        ttk.Button(button_frame, text="🔄 Sıfırla",
                  command=self.reset_preferences).pack(side="left", padx=5)

        # Results display
        self.results_text = tk.Text(results_frame, height=8, wrap="word")
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical",
                                 command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.pack(side="left", fill="both", expand=True, pady=(10, 0))
        scrollbar.pack(side="right", fill="y", pady=(10, 0))

    def apply_smart_optimization(self):
        """Apply smart optimization to current courses."""
        if not self.courses:
            messagebox.showwarning("Uyarı", "Önce dersler yüklenmelidir!")
            return

        # Build smart filter profile from UI
        profile = self._build_smart_profile()

        # Apply optimization
        optimized_courses = self.optimizer.optimize_course_selection(self.courses, profile)

        # Display results
        self._display_optimization_results(optimized_courses, profile)

    def _build_smart_profile(self) -> SmartFilterProfile:
        """Build smart filter profile from UI inputs."""
        profile = SmartFilterProfile(FilterProfile())

        # Time preferences
        time_ranges = []
        if self.morning_var.get():
            time_ranges.append((1, 4))  # Slots 1-4 (morning)
        if self.afternoon_var.get():
            time_ranges.append((5, 8))  # Slots 5-8 (afternoon)
        if self.evening_var.get():
            time_ranges.append((9, 12))  # Slots 9-12 (evening)

        profile.preferred_time_ranges = time_ranges
        profile.max_daily_courses = self.max_daily_var.get()
        profile.max_gap_hours = self.max_gap_var.get()

        # Day preferences
        preferred_days = [code for code, var in self.day_vars.items() if var.get()]
        avoided_days = []

        if self.no_friday_var.get():
            avoided_days.append("F")
        if self.no_weekend_var.get():
            avoided_days.extend(["Sa", "Su"])

        profile.preferred_days = preferred_days
        profile.avoided_days = avoided_days

        # Teacher preferences
        pref_text = self.preferred_teachers_text.get("1.0", tk.END).strip()
        avoid_text = self.avoided_teachers_text.get("1.0", tk.END).strip()

        profile.preferred_teachers = [t.strip() for t in pref_text.split(",") if t.strip()]
        profile.avoided_teachers = [t.strip() for t in avoid_text.split(",") if t.strip()]

        # Optimization goals
        goals = [goal for goal, var in self.goal_vars.items() if var.get()]
        profile.optimization_goals = goals

        return profile

    def _display_optimization_results(self, optimized_courses: List[Course],
                                    profile: SmartFilterProfile):
        """Display optimization results."""
        self.results_text.delete("1.0", tk.END)

        original_count = len(self.courses)
        optimized_count = len(optimized_courses)

        # Summary
        summary = f"""
🎯 AKILLI OPTİMİZASYON SONUÇLARI
{'='*50}

📊 Özet:
• Başlangıç ders sayısı: {original_count}
• Optimize edilmiş ders sayısı: {optimized_count}
• Filtrelenen ders sayısı: {original_count - optimized_count}
• Filtreleme oranı: %{((original_count - optimized_count) / original_count * 100):.1f}

🔧 Uygulanan Filtreler:
"""

        if profile.preferred_time_ranges:
            time_desc = ", ".join([f"Slot {start}-{end}" for start, end in profile.preferred_time_ranges])
            summary += f"• Zaman aralıkları: {time_desc}\n"

        if profile.preferred_days:
            summary += f"• Tercih edilen günler: {', '.join(profile.preferred_days)}\n"

        if profile.avoided_days:
            summary += f"• Kaçınılan günler: {', '.join(profile.avoided_days)}\n"

        if profile.preferred_teachers:
            summary += f"• Tercih edilen öğretmenler: {len(profile.preferred_teachers)} kişi\n"

        if profile.avoided_teachers:
            summary += f"• Kaçınılan öğretmenler: {len(profile.avoided_teachers)} kişi\n"

        if profile.optimization_goals:
            goals_desc = ", ".join([goal.value.replace("_", " ").title() for goal in profile.optimization_goals])
            summary += f"• Optimizasyon hedefleri: {goals_desc}\n"

        summary += f"\n📋 İlk 10 Optimize Edilmiş Ders:\n"
        summary += "-" * 50 + "\n"

        for i, course in enumerate(optimized_courses[:10], 1):
            schedule_str = ", ".join([f"{day}{hour}" for day, hour in course.schedule])
            summary += f"{i:2d}. {course.code} - {course.name[:30]}...\n"
            summary += f"    📅 {schedule_str} | 👨‍🏫 {course.teacher} | 🏫 {course.campus}\n\n"

        if len(optimized_courses) > 10:
            summary += f"... ve {len(optimized_courses) - 10} ders daha\n"

        self.results_text.insert("1.0", summary)

        # Store optimized courses for further use
        self.optimized_courses = optimized_courses

    def save_profile(self):
        """Save current optimization profile."""
        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            title="Profili Kaydet",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            profile = self._build_smart_profile()
            profile_data = {
                "preferred_time_ranges": profile.preferred_time_ranges,
                "max_daily_courses": profile.max_daily_courses,
                "max_gap_hours": profile.max_gap_hours,
                "preferred_days": profile.preferred_days,
                "avoided_days": profile.avoided_days,
                "preferred_teachers": profile.preferred_teachers,
                "avoided_teachers": profile.avoided_teachers,
                "optimization_goals": [goal.value for goal in profile.optimization_goals or []]
            }

            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(profile_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Başarılı", f"Profil kaydedildi: {filename}")
            except Exception as e:
                messagebox.showerror("Hata", f"Profil kaydedilemedi: {e}")

    def load_profile(self):
        """Load optimization profile from file."""
        from tkinter import filedialog

        filename = filedialog.askopenfilename(
            title="Profil Yükle",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)

                # Load UI values from profile data
                self._load_profile_to_ui(profile_data)
                messagebox.showinfo("Başarılı", f"Profil yüklendi: {filename}")

            except Exception as e:
                messagebox.showerror("Hata", f"Profil yüklenemedi: {e}")

    def _load_profile_to_ui(self, profile_data: Dict):
        """Load profile data to UI elements."""
        # Reset first
        self.reset_preferences()

        # Time preferences
        time_ranges = profile_data.get("preferred_time_ranges", [])
        for start, end in time_ranges:
            if 1 <= start <= 4:
                self.morning_var.set(True)
            elif 5 <= start <= 8:
                self.afternoon_var.set(True)
            elif 9 <= start <= 12:
                self.evening_var.set(True)

        # Daily settings
        self.max_daily_var.set(profile_data.get("max_daily_courses", 4))
        self.max_gap_var.set(profile_data.get("max_gap_hours", 2))

        # Day preferences
        preferred_days = profile_data.get("preferred_days", [])
        for day_code, var in self.day_vars.items():
            var.set(day_code in preferred_days)

        avoided_days = profile_data.get("avoided_days", [])
        self.no_friday_var.set("F" in avoided_days)
        self.no_weekend_var.set("Sa" in avoided_days or "Su" in avoided_days)

        # Teacher preferences
        preferred_teachers = profile_data.get("preferred_teachers", [])
        self.preferred_teachers_text.delete("1.0", tk.END)
        self.preferred_teachers_text.insert("1.0", ", ".join(preferred_teachers))

        avoided_teachers = profile_data.get("avoided_teachers", [])
        self.avoided_teachers_text.delete("1.0", tk.END)
        self.avoided_teachers_text.insert("1.0", ", ".join(avoided_teachers))

        # Optimization goals
        goal_values = profile_data.get("optimization_goals", [])
        for goal, var in self.goal_vars.items():
            var.set(goal.value in goal_values)

    def reset_preferences(self):
        """Reset all preferences to default."""
        # Time preferences
        self.morning_var.set(False)
        self.afternoon_var.set(False)
        self.evening_var.set(False)

        # Daily settings
        self.max_daily_var.set(4)
        self.max_gap_var.set(2)

        # Day preferences - all true by default
        for var in self.day_vars.values():
            var.set(True)

        self.no_friday_var.set(False)
        self.no_weekend_var.set(True)

        # Teacher preferences
        self.preferred_teachers_text.delete("1.0", tk.END)
        self.avoided_teachers_text.delete("1.0", tk.END)

        # Optimization goals
        for var in self.goal_vars.values():
            var.set(False)

        # Clear results
        self.results_text.delete("1.0", tk.END)

    def set_courses(self, courses: List[Course]):
        """Set courses for optimization."""
        self.courses = courses
