"""
Splash screen implementation for the course scheduler application.

This module provides a splash screen that appears during application startup.
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional
import threading
import time


def show_splash(parent: ctk.CTk) -> Optional[ctk.CTkToplevel]:
    """
    Show the application splash screen.

    Args:
        parent: Parent window

    Returns:
        Splash window object or None
    """
    try:
        # Create splash window
        splash = ctk.CTkToplevel(parent)
        splash.title("Course Scheduler")
        splash.geometry("400x300")
        splash.resizable(False, False)

        # Center the splash screen
        splash.update_idletasks()
        x = (splash.winfo_screenwidth() // 2) - (400 // 2)
        y = (splash.winfo_screenheight() // 2) - (300 // 2)
        splash.geometry(f"400x300+{x}+{y}")

        # Remove window decorations
        splash.overrideredirect(True)

        # Create splash content
        main_frame = ctk.CTkFrame(splash, corner_radius=0)
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎓 Course Scheduler",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(50, 20))

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="University Course Scheduling Application",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=10)

        # Loading indicator
        loading_label = ctk.CTkLabel(
            main_frame,
            text="Loading...",
            font=ctk.CTkFont(size=12)
        )
        loading_label.pack(pady=20)

        # Progress bar
        progress = ctk.CTkProgressBar(main_frame, width=300)
        progress.pack(pady=20)
        progress.set(0)

        # Version info
        version_label = ctk.CTkLabel(
            main_frame,
            text="Version 1.0.0",
            font=ctk.CTkFont(size=10)
        )
        version_label.pack(side="bottom", pady=10)

        # Animate progress bar
        def animate_progress():
            for i in range(101):
                progress.set(i / 100)
                splash.update()
                time.sleep(0.02)

        # Run animation in thread
        animation_thread = threading.Thread(target=animate_progress)
        animation_thread.daemon = True
        animation_thread.start()

        return splash

    except Exception as e:
        print(f"Error creating splash screen: {e}")
        return None
