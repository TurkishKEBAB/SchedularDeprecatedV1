"""
Course deletion and selection utilities for the course preview tab.
"""
from typing import List, Set
import logging

logger = logging.getLogger(__name__)


def add_course_deletion_methods(course_preview_tab):
    """Add course deletion methods to the CoursePreviewTab class."""

    def _delete_selected_courses(self):
        """Delete selected courses from the cache (not from database)."""
        selected_items = self.courses_tree.selection()
        if not selected_items:
            from tkinter import messagebox
            messagebox.showwarning("No Selection", "Please select courses to delete.")
            return

        # Get codes of selected courses
        selected_codes = []
        for item in selected_items:
            values = self.courses_tree.item(item, "values")
            if values:
                selected_codes.append(values[0])  # Course code is first column

        # Remove from main app's course list (cache only)
        if hasattr(self.main_app, 'courses'):
            original_count = len(self.main_app.courses)
            self.main_app.courses = [
                course for course in self.main_app.courses
                if course.code not in selected_codes
            ]
            deleted_count = original_count - len(self.main_app.courses)

            # Update the preview with remaining courses
            self.update_courses(self.main_app.courses)

            logger.info(f"Deleted {deleted_count} courses from cache")
            self.status_label.configure(text=f"Deleted {deleted_count} courses. {len(self.main_app.courses)} remaining.")

    def _select_all_visible(self):
        """Select all visible courses in the treeview."""
        self.courses_tree.selection_set(self.courses_tree.get_children())

    def _deselect_all(self):
        """Deselect all courses in the treeview."""
        self.courses_tree.selection_remove(self.courses_tree.get_children())

    # Add methods to the class
    course_preview_tab._delete_selected_courses = _delete_selected_courses.__get__(course_preview_tab)
    course_preview_tab._select_all_visible = _select_all_visible.__get__(course_preview_tab)
    course_preview_tab._deselect_all = _deselect_all.__get__(course_preview_tab)


def add_deletion_buttons_to_preview(course_preview_tab):
    """Add deletion buttons to the course preview tab."""
    import customtkinter as ctk

    # Find the button frame
    button_frame = None
    for child in course_preview_tab.parent.winfo_children():
        if isinstance(child, ctk.CTkFrame):
            # Check if this frame contains the proceed button
            for grandchild in child.winfo_children():
                if isinstance(grandchild, ctk.CTkButton) and "Proceed" in grandchild.cget("text"):
                    button_frame = child
                    break
            if button_frame:
                break

    if button_frame:
        # Add deletion button
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Delete Selected",
            command=course_preview_tab._delete_selected_courses,
            width=150,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red")
        )
        delete_btn.pack(side="right", padx=(0, 15))

        # Add select all button
        select_all_btn = ctk.CTkButton(
            button_frame,
            text="✅ Select All Visible",
            command=course_preview_tab._select_all_visible,
            width=150,
            fg_color=("orange", "darkorange"),
            hover_color=("darkorange", "orange")
        )
        select_all_btn.pack(side="right", padx=5)
