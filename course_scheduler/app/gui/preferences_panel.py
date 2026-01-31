"""
Advanced preferences panel for the course scheduler.

This module provides an advanced preferences panel where users can configure
detailed scheduling preferences and constraints.
"""
import customtkinter as ctk
from typing import Any, Callable
import logging

from ..utils.schedule_metrics import SchedulerPrefs

# Set up logging
logger = logging.getLogger(__name__)


class AdvancedPreferencesPanel:
    """
    Advanced preferences panel for detailed scheduling configuration.

    This panel allows users to set:
    1. Day compression preferences
    2. Free day requirements
    3. Weekly and daily hour limits
    4. Scoring weights for optimization
    """

    def __init__(self, parent: ctk.CTkFrame, update_callback: Callable[[SchedulerPrefs], None]):
        """
        Initialize the advanced preferences panel.

        Args:
            parent: Parent frame (tab container)
            update_callback: Function to call when preferences are updated
        """
        self.parent = parent
        self.update_callback = update_callback
        self.scheduler_prefs = SchedulerPrefs()

        # Create UI components
        self._create_compression_section()
        self._create_limits_section()
        self._create_weights_section()
        self._create_buttons_section()
        self._create_course_type_priorities_section()

    def _create_compression_section(self):
        """Create the day compression preferences section."""
        # Compression frame
        compression_frame = ctk.CTkFrame(self.parent)
        compression_frame.pack(fill="x", padx=20, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            compression_frame,
            text="📅 Day Preferences",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # Compression checkbox
        self.compress_var = ctk.BooleanVar(value=False)
        self.compress_check = ctk.CTkCheckBox(
            compression_frame,
            text="Compress classes into fewer days",
            variable=self.compress_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_preferences_changed
        )
        self.compress_check.pack(pady=5, padx=15, anchor="w")

        # Free days frame
        free_days_frame = ctk.CTkFrame(compression_frame)
        free_days_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            free_days_frame,
            text="Desired Free Days:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=10)

        # Day checkboxes
        self.day_vars = {}
        days = [("M", "Monday"), ("T", "Tuesday"), ("W", "Wednesday"),
                ("Th", "Thursday"), ("F", "Friday"), ("Sa", "Saturday"), ("Su", "Sunday")]

        for day_code, day_name in days:
            var = ctk.BooleanVar(value=False)
            self.day_vars[day_code] = var

            check = ctk.CTkCheckBox(
                free_days_frame,
                text=day_name[:3],
                variable=var,
                command=self._on_preferences_changed,
                font=ctk.CTkFont(size=10)
            )
            check.pack(side="left", padx=5)

        # Strict free days
        self.strict_free_var = ctk.BooleanVar(value=True)
        self.strict_free_check = ctk.CTkCheckBox(
            compression_frame,
            text="Strict free days (no classes at all on selected days)",
            variable=self.strict_free_var,
            font=ctk.CTkFont(size=11),
            command=self._on_preferences_changed
        )
        self.strict_free_check.pack(pady=5, padx=15, anchor="w")

    def _create_limits_section(self):
        """Create the hour limits section."""
        # Limits frame
        limits_frame = ctk.CTkFrame(self.parent)
        limits_frame.pack(fill="x", padx=20, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            limits_frame,
            text="⏰ Hour Limits",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # Grid for limits
        grid_frame = ctk.CTkFrame(limits_frame)
        grid_frame.pack(fill="x", padx=15, pady=10)

        # Max weekly hours
        ctk.CTkLabel(
            grid_frame,
            text="Maximum Weekly Hours:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.max_weekly_var = ctk.IntVar(value=60)
        self.max_weekly_slider = ctk.CTkSlider(
            grid_frame,
            from_=10, to=60,
            variable=self.max_weekly_var,
            command=self._on_weekly_changed,
            width=200
        )
        self.max_weekly_slider.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.max_weekly_label = ctk.CTkLabel(
            grid_frame,
            text="60 hours",
            font=ctk.CTkFont(size=11)
        )
        self.max_weekly_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        # Max daily hours
        ctk.CTkLabel(
            grid_frame,
            text="Maximum Daily Hours:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.max_daily_var = ctk.IntVar(value=8)
        self.max_daily_slider = ctk.CTkSlider(
            grid_frame,
            from_=3, to=12,
            variable=self.max_daily_var,
            command=self._on_daily_changed,
            width=200
        )
        self.max_daily_slider.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.max_daily_label = ctk.CTkLabel(
            grid_frame,
            text="8 hours",
            font=ctk.CTkFont(size=11)
        )
        self.max_daily_label.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Enable daily limit
        self.enable_daily_var = ctk.BooleanVar(value=False)
        self.enable_daily_check = ctk.CTkCheckBox(
            limits_frame,
            text="Enable daily hour limit",
            variable=self.enable_daily_var,
            font=ctk.CTkFont(size=11),
            command=self._on_preferences_changed
        )
        self.enable_daily_check.pack(pady=5, padx=15, anchor="w")

        # Conflict settings
        conflict_frame = ctk.CTkFrame(limits_frame)
        conflict_frame.pack(fill="x", padx=15, pady=10)

        # Allow conflicts checkbox
        self.allow_conflicts_var = ctk.BooleanVar(value=False)
        self.allow_conflicts_check = ctk.CTkCheckBox(
            conflict_frame,
            text="Allow course time conflicts",
            variable=self.allow_conflicts_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_conflicts_changed
        )
        self.allow_conflicts_check.pack(pady=5, padx=10, anchor="w")

        # Max conflict hours
        conflict_limit_frame = ctk.CTkFrame(conflict_frame)
        conflict_limit_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            conflict_limit_frame,
            text="Maximum Conflict Hours:",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=10)

        self.max_conflict_var = ctk.IntVar(value=2)
        self.max_conflict_slider = ctk.CTkSlider(
            conflict_limit_frame,
            from_=1, to=8,
            variable=self.max_conflict_var,
            command=self._on_conflict_hours_changed,
            width=150
        )
        self.max_conflict_slider.pack(side="left", padx=10)

        self.max_conflict_label = ctk.CTkLabel(
            conflict_limit_frame,
            text="2 hours",
            font=ctk.CTkFont(size=10)
        )
        self.max_conflict_label.pack(side="left", padx=5)

        # Initially disable conflict hours slider
        self.max_conflict_slider.configure(state="disabled")
        self.max_conflict_label.configure(text_color="gray")

    def _create_weights_section(self):
        """Create the optimization weights section."""
        # Weights frame
        weights_frame = ctk.CTkFrame(self.parent)
        weights_frame.pack(fill="x", padx=20, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            weights_frame,
            text="⚖️ Optimization Weights",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # Grid for weights
        grid_frame = ctk.CTkFrame(weights_frame)
        grid_frame.pack(fill="x", padx=15, pady=10)

        # Weight variables and sliders
        self.weight_vars = {}
        self.weight_labels = {}

        weights = [
            ("free_days", "Free Days Importance", 1.0),
            ("compression", "Day Compression", 1.0),
            ("gaps", "Minimize Gaps", 0.5),
            ("consecutive", "Consecutive Blocks", 0.5)
        ]

        for i, (key, label, default) in enumerate(weights):
            ctk.CTkLabel(
                grid_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=11, weight="bold")
            ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

            var = ctk.DoubleVar(value=default)
            self.weight_vars[key] = var

            slider = ctk.CTkSlider(
                grid_frame,
                from_=0.0, to=2.0,
                variable=var,
                command=lambda v, k=key: self._on_weight_changed(k, v),
                width=150
            )
            slider.grid(row=i, column=1, padx=10, pady=5, sticky="w")

            label_widget = ctk.CTkLabel(
                grid_frame,
                text=f"{default:.1f}",
                font=ctk.CTkFont(size=10)
            )
            label_widget.grid(row=i, column=2, padx=10, pady=5, sticky="w")
            self.weight_labels[key] = label_widget

    def _create_buttons_section(self):
        """Create the action buttons section."""
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.parent)
        buttons_frame.pack(fill="x", padx=20, pady=10)

        # Reset button
        reset_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Reset to Defaults",
            command=self._reset_to_defaults,
            width=150,
            fg_color=("gray60", "gray40"),
            hover_color=("gray50", "gray30")
        )
        reset_btn.pack(side="left", padx=15, pady=10)

        # Apply button
        apply_btn = ctk.CTkButton(
            buttons_frame,
            text="✅ Apply Preferences",
            command=self._apply_preferences,
            width=150,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green")
        )
        apply_btn.pack(side="right", padx=15, pady=10)

    def _create_course_type_priorities_section(self):
        """Create course type priorities section."""
        # Course type priorities frame
        priorities_frame = ctk.CTkFrame(self.parent)
        priorities_frame.pack(fill="x", padx=20, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            priorities_frame,
            text="📚 Course Type Priorities",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        ctk.CTkLabel(
            priorities_frame,
            text="Set priority order for course types (higher priority = scheduled first):",
            font=ctk.CTkFont(size=11)
        ).pack(pady=5, padx=15, anchor="w")

        # Priority order frame
        priority_frame = ctk.CTkFrame(priorities_frame)
        priority_frame.pack(fill="x", padx=15, pady=10)

        # Course type variables and controls
        self.course_type_priorities = ["lecture", "ps", "lab"]
        self.priority_vars = {}

        course_types = [
            ("lecture", "Lectures"),
            ("ps", "Problem Sessions"),
            ("lab", "Laboratory")
        ]

        for i, (type_code, type_name) in enumerate(course_types):
            row_frame = ctk.CTkFrame(priority_frame)
            row_frame.pack(fill="x", padx=10, pady=2)

            ctk.CTkLabel(
                row_frame,
                text=f"{i+1}. {type_name}:",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=120
            ).pack(side="left", padx=10, pady=5)

            # Priority slider (1-3, where 1 is highest priority)
            var = ctk.IntVar(value=i+1)
            self.priority_vars[type_code] = var

            slider = ctk.CTkSlider(
                row_frame,
                from_=1, to=3,
                variable=var,
                command=lambda val, t=type_code: self._on_priority_changed(t, val),
                width=150,
                number_of_steps=2
            )
            slider.pack(side="left", padx=10, pady=5)

            priority_label = ctk.CTkLabel(
                row_frame,
                text="Priority 1",
                font=ctk.CTkFont(size=10)
            )
            priority_label.pack(side="left", padx=5, pady=5)

            # Store label reference for updates
            setattr(self, f"{type_code}_priority_label", priority_label)

    def _on_weekly_changed(self, value):
        """Handle weekly hours slider change."""
        hours = int(float(value))
        self.max_weekly_label.configure(text=f"{hours} hours")
        self._on_preferences_changed()

    def _on_daily_changed(self, value):
        """Handle daily hours slider change."""
        hours = int(float(value))
        self.max_daily_label.configure(text=f"{hours} hours")
        self._on_preferences_changed()

    def _on_conflict_hours_changed(self, value):
        """Handle max conflict hours slider change."""
        hours = int(float(value))
        self.max_conflict_label.configure(text=f"{hours} hours")
        self._on_preferences_changed()

    def _on_weight_changed(self, key, value):
        """Handle weight slider change."""
        weight = float(value)
        self.weight_labels[key].configure(text=f"{weight:.1f}")
        self._on_preferences_changed()

    def _on_preferences_changed(self):
        """Handle any preference change."""
        # Update the scheduler preferences object
        self._update_scheduler_prefs()

    def _on_conflicts_changed(self):
        """Handle changes to conflict allowance setting."""
        allow_conflicts = self.allow_conflicts_var.get()
        if allow_conflicts:
            # Enable conflict hours slider
            self.max_conflict_slider.configure(state="normal")
            self.max_conflict_label.configure(text_color="black")
        else:
            # Disable conflict hours slider
            self.max_conflict_slider.configure(state="disabled")
            self.max_conflict_label.configure(text_color="gray")

        self._on_preferences_changed()

    def _on_priority_changed(self, type_code, value):
        """Handle priority slider change."""
        priority = int(float(value))
        label = getattr(self, f"{type_code}_priority_label")
        label.configure(text=f"Priority {priority}")
        self._on_preferences_changed()

    def _update_scheduler_prefs(self):
        """Update the SchedulerPrefs object with current values."""
        # Get selected free days
        desired_free_days = [day for day, var in self.day_vars.items() if var.get()]

        # Update preferences
        self.scheduler_prefs.compress_classes = self.compress_var.get()
        self.scheduler_prefs.desired_free_days = desired_free_days
        self.scheduler_prefs.strict_free_days = self.strict_free_var.get()
        self.scheduler_prefs.max_weekly_slots = self.max_weekly_var.get()

        if self.enable_daily_var.get():
            self.scheduler_prefs.max_daily_slots = self.max_daily_var.get()
        else:
            self.scheduler_prefs.max_daily_slots = None

        # Update conflict settings
        self.scheduler_prefs.allow_conflicts = self.allow_conflicts_var.get()
        self.scheduler_prefs.max_conflict_hours = self.max_conflict_var.get()

        # Update weights
        self.scheduler_prefs.weight_free_days = self.weight_vars["free_days"].get()
        self.scheduler_prefs.weight_compression = self.weight_vars["compression"].get()
        self.scheduler_prefs.weight_gaps = self.weight_vars["gaps"].get()
        self.scheduler_prefs.weight_consecutive = self.weight_vars["consecutive"].get()

        # Update course type priorities
        for type_code in self.course_type_priorities:
            priority = self.priority_vars[type_code].get()
            setattr(self.scheduler_prefs, f"priority_{type_code}", priority)

    def _reset_to_defaults(self):
        """Reset all preferences to default values."""
        # Reset checkboxes
        self.compress_var.set(False)
        self.strict_free_var.set(True)
        self.enable_daily_var.set(False)
        self.allow_conflicts_var.set(False)

        # Reset day selections
        for var in self.day_vars.values():
            var.set(False)

        # Reset sliders
        self.max_weekly_var.set(60)
        self.max_daily_var.set(8)
        self.max_conflict_var.set(2)

        # Reset weights
        default_weights = {"free_days": 1.0, "compression": 1.0, "gaps": 0.5, "consecutive": 0.5}
        for key, value in default_weights.items():
            self.weight_vars[key].set(value)
            self.weight_labels[key].configure(text=f"{value:.1f}")

        # Reset priority sliders
        for i, type_code in enumerate(self.course_type_priorities):
            self.priority_vars[type_code].set(i+1)
            label = getattr(self, f"{type_code}_priority_label")
            label.configure(text="Priority {}".format(i+1))

        # Update labels
        self.max_weekly_label.configure(text="60 hours")
        self.max_daily_label.configure(text="8 hours")
        self.max_conflict_label.configure(text="2 hours", text_color="gray")

        # Update preferences
        self._on_preferences_changed()

        logger.info("Preferences reset to defaults")

    def _apply_preferences(self):
        """Apply the current preferences."""
        self._update_scheduler_prefs()
        self.update_callback(self.scheduler_prefs)
        logger.info("Advanced preferences applied")

    def get_preferences(self) -> SchedulerPrefs:
        """
        Get the current scheduler preferences.

        Returns:
            SchedulerPrefs object with current settings
        """
        self._update_scheduler_prefs()
        return self.scheduler_prefs
