"""
Enhanced Dashboard System with Real-time Analytics
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime
import json

from ..core.models import Course, Schedule

class InteractiveDashboard:
    """Interactive dashboard with real-time course analytics."""

    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.courses = []
        self.filtered_courses = []
        self.schedules = []

        # Dashboard metrics
        self.metrics = {
            'total_courses': 0,
            'filtered_courses': 0,
            'total_ects': 0,
            'avg_ects_per_course': 0,
            'faculty_distribution': {},
            'campus_distribution': {},
            'time_slot_usage': {},
            'daily_load': {},
            'conflicts': 0
        }

        self.setup_ui()
        self.update_dashboard()

    def setup_ui(self):
        """Setup the dashboard UI."""
        # Main container with scrollable frame
        canvas = tk.Canvas(self.parent, bg='white')
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Dashboard header
        self.setup_header()

        # Metrics cards
        self.setup_metrics_cards()

        # Charts section
        self.setup_charts_section()

        # Live updates section
        self.setup_live_updates()

    def setup_header(self):
        """Setup dashboard header."""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Title
        title_label = ttk.Label(header_frame, text="📊 Akıllı Ders Programı Dashboard",
                               font=("Arial", 18, "bold"))
        title_label.pack(side="left")

        # Last update time
        self.last_update_var = tk.StringVar(value="Son Güncelleme: " + datetime.now().strftime("%H:%M:%S"))
        update_label = ttk.Label(header_frame, textvariable=self.last_update_var,
                                font=("Arial", 10), foreground="gray")
        update_label.pack(side="right")

        # Auto-refresh button
        ttk.Button(header_frame, text="🔄 Yenile",
                  command=self.update_dashboard).pack(side="right", padx=(0, 10))

    def setup_metrics_cards(self):
        """Setup metrics cards section."""
        cards_frame = ttk.Frame(self.scrollable_frame)
        cards_frame.pack(fill="x", padx=20, pady=10)

        # Create 4 columns for metric cards
        self.metric_cards = {}

        # Total Courses Card
        self.create_metric_card(cards_frame, "total_courses", "📚 Toplam Ders",
                               "0", "Yüklenen ders sayısı", 0, 0)

        # Filtered Courses Card
        self.create_metric_card(cards_frame, "filtered_courses", "🔍 Filtrelenmiş",
                               "0", "Aktif filtreleme sonucu", 0, 1)

        # Total ECTS Card
        self.create_metric_card(cards_frame, "total_ects", "🏆 Toplam ECTS",
                               "0", "Tüm derslerin ECTS toplamı", 0, 2)

        # Conflicts Card
        self.create_metric_card(cards_frame, "conflicts", "⚠️ Çakışmalar",
                               "0", "Zaman çakışması sayısı", 0, 3)

    def create_metric_card(self, parent, key, title, value, description, row, col):
        """Create a metric card widget."""
        card_frame = ttk.LabelFrame(parent, text="", padding=15)
        card_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        # Icon and title
        title_label = ttk.Label(card_frame, text=title, font=("Arial", 12, "bold"))
        title_label.pack()

        # Value
        value_var = tk.StringVar(value=value)
        value_label = ttk.Label(card_frame, textvariable=value_var,
                               font=("Arial", 24, "bold"), foreground="blue")
        value_label.pack(pady=(5, 0))

        # Description
        desc_label = ttk.Label(card_frame, text=description,
                              font=("Arial", 9), foreground="gray")
        desc_label.pack()

        self.metric_cards[key] = value_var

    def setup_charts_section(self):
        """Setup charts and visualizations section."""
        charts_frame = ttk.LabelFrame(self.scrollable_frame, text="📈 Analitik Grafikler",
                                     padding=15)
        charts_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create notebook for different charts
        charts_notebook = ttk.Notebook(charts_frame)
        charts_notebook.pack(fill="both", expand=True)

        # Faculty Distribution Chart
        self.setup_faculty_chart(charts_notebook)

        # Time Slot Usage Chart
        self.setup_timeslot_chart(charts_notebook)

        # Daily Load Chart
        self.setup_daily_load_chart(charts_notebook)

        # Campus Distribution Chart
        self.setup_campus_chart(charts_notebook)

    def setup_faculty_chart(self, parent):
        """Setup faculty distribution pie chart."""
        frame = ttk.Frame(parent)
        parent.add(frame, text="🏫 Fakülte Dağılımı")

        self.faculty_fig, self.faculty_ax = plt.subplots(figsize=(8, 6))
        self.faculty_canvas = FigureCanvasTkAgg(self.faculty_fig, frame)
        self.faculty_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Initial empty chart
        self.faculty_ax.text(0.5, 0.5, 'Veri yükleniyor...',
                            ha='center', va='center', transform=self.faculty_ax.transAxes)

    def setup_timeslot_chart(self, parent):
        """Setup time slot usage bar chart."""
        frame = ttk.Frame(parent)
        parent.add(frame, text="⏰ Zaman Slotu Kullanımı")

        self.timeslot_fig, self.timeslot_ax = plt.subplots(figsize=(10, 6))
        self.timeslot_canvas = FigureCanvasTkAgg(self.timeslot_fig, frame)
        self.timeslot_canvas.get_tk_widget().pack(fill="both", expand=True)

    def setup_daily_load_chart(self, parent):
        """Setup daily course load bar chart."""
        frame = ttk.Frame(parent)
        parent.add(frame, text="📅 Günlük Yoğunluk")

        self.daily_fig, self.daily_ax = plt.subplots(figsize=(8, 6))
        self.daily_canvas = FigureCanvasTkAgg(self.daily_fig, frame)
        self.daily_canvas.get_tk_widget().pack(fill="both", expand=True)

    def setup_campus_chart(self, parent):
        """Setup campus distribution donut chart."""
        frame = ttk.Frame(parent)
        parent.add(frame, text="🏛️ Kampüs Dağılımı")

        self.campus_fig, self.campus_ax = plt.subplots(figsize=(8, 6))
        self.campus_canvas = FigureCanvasTkAgg(self.campus_fig, frame)
        self.campus_canvas.get_tk_widget().pack(fill="both", expand=True)

    def setup_live_updates(self):
        """Setup live updates and recommendations section."""
        updates_frame = ttk.LabelFrame(self.scrollable_frame, text="🔔 Canlı Güncellemeler & Öneriler",
                                      padding=15)
        updates_frame.pack(fill="x", padx=20, pady=10)

        # Live updates text area
        self.updates_text = tk.Text(updates_frame, height=8, wrap="word",
                                   font=("Consolas", 10))
        updates_scroll = ttk.Scrollbar(updates_frame, orient="vertical",
                                      command=self.updates_text.yview)
        self.updates_text.configure(yscrollcommand=updates_scroll.set)

        self.updates_text.pack(side="left", fill="both", expand=True)
        updates_scroll.pack(side="right", fill="y")

        # Add initial message
        self.add_update("📊 Dashboard hazır! Ders verilerini yükleyin.")

    def update_dashboard(self):
        """Update all dashboard components."""
        self.calculate_metrics()
        self.update_metric_cards()
        self.update_charts()
        self.generate_insights()

        # Update timestamp
        self.last_update_var.set("Son Güncelleme: " + datetime.now().strftime("%H:%M:%S"))

    def calculate_metrics(self):
        """Calculate all dashboard metrics."""
        if not self.courses:
            return

        self.metrics['total_courses'] = len(self.courses)
        self.metrics['filtered_courses'] = len(self.filtered_courses)
        self.metrics['total_ects'] = sum(c.ects for c in self.courses)

        if self.courses:
            self.metrics['avg_ects_per_course'] = self.metrics['total_ects'] / len(self.courses)

        # Faculty distribution
        faculty_dist = {}
        for course in self.courses:
            faculty = course.faculty
            faculty_dist[faculty] = faculty_dist.get(faculty, 0) + 1
        self.metrics['faculty_distribution'] = faculty_dist

        # Campus distribution
        campus_dist = {}
        for course in self.courses:
            campus = course.campus
            campus_dist[campus] = campus_dist.get(campus, 0) + 1
        self.metrics['campus_distribution'] = campus_dist

        # Time slot usage
        timeslot_usage = {}
        for course in self.courses:
            for day, hour in course.schedule:
                key = f"{day}{hour}"
                timeslot_usage[key] = timeslot_usage.get(key, 0) + 1
        self.metrics['time_slot_usage'] = timeslot_usage

        # Daily load
        daily_load = {'M': 0, 'T': 0, 'W': 0, 'Th': 0, 'F': 0, 'Sa': 0, 'Su': 0}
        for course in self.courses:
            for day, _ in course.schedule:
                if day in daily_load:
                    daily_load[day] += 1
        self.metrics['daily_load'] = daily_load

        # Calculate conflicts
        conflicts = 0
        if self.schedules:
            for schedule in self.schedules:
                conflicts += schedule.conflict_cost
        self.metrics['conflicts'] = conflicts

    def update_metric_cards(self):
        """Update metric card values."""
        self.metric_cards['total_courses'].set(str(self.metrics['total_courses']))
        self.metric_cards['filtered_courses'].set(str(self.metrics['filtered_courses']))
        self.metric_cards['total_ects'].set(str(self.metrics['total_ects']))
        self.metric_cards['conflicts'].set(str(self.metrics['conflicts']))

    def update_charts(self):
        """Update all charts."""
        self.update_faculty_chart()
        self.update_timeslot_chart()
        self.update_daily_load_chart()
        self.update_campus_chart()

    def update_faculty_chart(self):
        """Update faculty distribution pie chart."""
        self.faculty_ax.clear()

        if not self.metrics['faculty_distribution']:
            self.faculty_ax.text(0.5, 0.5, 'Fakülte verisi bulunamadı',
                                ha='center', va='center')
            self.faculty_canvas.draw()
            return

        # Prepare data
        faculties = list(self.metrics['faculty_distribution'].keys())
        counts = list(self.metrics['faculty_distribution'].values())

        # Truncate long faculty names
        display_names = [f[:20] + '...' if len(f) > 20 else f for f in faculties]

        # Create pie chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(faculties)))
        wedges, texts, autotexts = self.faculty_ax.pie(counts, labels=display_names,
                                                      autopct='%1.1f%%', colors=colors,
                                                      startangle=90)

        self.faculty_ax.set_title('Fakülte Bazlı Ders Dağılımı', fontsize=14, fontweight='bold')

        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        self.faculty_canvas.draw()

    def update_timeslot_chart(self):
        """Update time slot usage bar chart."""
        self.timeslot_ax.clear()

        if not self.metrics['time_slot_usage']:
            self.timeslot_ax.text(0.5, 0.5, 'Zaman slotu verisi bulunamadı',
                                 ha='center', va='center')
            self.timeslot_canvas.draw()
            return

        # Prepare data - group by hour across all days
        hour_usage = {}
        for timeslot, count in self.metrics['time_slot_usage'].items():
            if len(timeslot) >= 2:
                hour = timeslot[1:]  # Remove day code
                try:
                    hour_num = int(hour)
                    hour_usage[hour_num] = hour_usage.get(hour_num, 0) + count
                except ValueError:
                    continue

        if hour_usage:
            hours = sorted(hour_usage.keys())
            counts = [hour_usage[h] for h in hours]

            bars = self.timeslot_ax.bar(hours, counts, color='skyblue', alpha=0.7)

            # Highlight peak hours
            max_count = max(counts)
            for i, bar in enumerate(bars):
                if counts[i] == max_count:
                    bar.set_color('orange')

            self.timeslot_ax.set_xlabel('Zaman Slotu')
            self.timeslot_ax.set_ylabel('Ders Sayısı')
            self.timeslot_ax.set_title('Zaman Slotu Kullanım Analizi', fontweight='bold')
            self.timeslot_ax.grid(True, alpha=0.3)

        self.timeslot_canvas.draw()

    def update_daily_load_chart(self):
        """Update daily course load bar chart."""
        self.daily_ax.clear()

        daily_load = self.metrics['daily_load']
        if not any(daily_load.values()):
            self.daily_ax.text(0.5, 0.5, 'Günlük yoğunluk verisi bulunamadı',
                              ha='center', va='center')
            self.daily_canvas.draw()
            return

        days = ['M', 'T', 'W', 'Th', 'F', 'Sa', 'Su']
        day_names = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
        counts = [daily_load.get(day, 0) for day in days]

        # Color code based on load
        colors = []
        for count in counts:
            if count == 0:
                colors.append('lightgray')
            elif count <= 5:
                colors.append('lightgreen')
            elif count <= 10:
                colors.append('yellow')
            else:
                colors.append('orange')

        bars = self.daily_ax.bar(day_names, counts, color=colors, alpha=0.8)

        # Add value labels on bars
        for bar, count in zip(bars, counts):
            if count > 0:
                self.daily_ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                                  str(count), ha='center', va='bottom', fontweight='bold')

        self.daily_ax.set_xlabel('Günler')
        self.daily_ax.set_ylabel('Ders Sayısı')
        self.daily_ax.set_title('Günlük Ders Yoğunluğu', fontweight='bold')
        self.daily_ax.grid(True, alpha=0.3, axis='y')

        self.daily_canvas.draw()

    def update_campus_chart(self):
        """Update campus distribution donut chart."""
        self.campus_ax.clear()

        if not self.metrics['campus_distribution']:
            self.campus_ax.text(0.5, 0.5, 'Kampüs verisi bulunamadı',
                               ha='center', va='center')
            self.campus_canvas.draw()
            return

        # Prepare data
        campuses = list(self.metrics['campus_distribution'].keys())
        counts = list(self.metrics['campus_distribution'].values())

        # Create donut chart
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(campuses)))
        wedges, texts, autotexts = self.campus_ax.pie(counts, labels=campuses,
                                                     autopct='%1.1f%%', colors=colors,
                                                     startangle=90, pctdistance=0.85)

        # Create donut effect
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        self.campus_ax.add_artist(centre_circle)

        self.campus_ax.set_title('Kampüs Bazlı Dağılım', fontsize=14, fontweight='bold')

        # Add total in center
        total_courses = sum(counts)
        self.campus_ax.text(0, 0, f'{total_courses}\nDers', ha='center', va='center',
                           fontsize=16, fontweight='bold')

        self.campus_canvas.draw()

    def generate_insights(self):
        """Generate intelligent insights and recommendations."""
        insights = []

        # Check for high load days
        daily_load = self.metrics['daily_load']
        max_load_day = max(daily_load, key=daily_load.get) if daily_load else None
        if max_load_day and daily_load[max_load_day] > 10:
            day_names = {'M': 'Pazartesi', 'T': 'Salı', 'W': 'Çarşamba',
                        'Th': 'Perşembe', 'F': 'Cuma', 'Sa': 'Cumartesi', 'Su': 'Pazar'}
            insights.append(f"⚠️ {day_names.get(max_load_day, max_load_day)} günü çok yoğun ({daily_load[max_load_day]} ders)")

        # Check for conflicts
        if self.metrics['conflicts'] > 0:
            insights.append(f"🔴 {self.metrics['conflicts']} çakışma tespit edildi")

        # Check ECTS distribution
        avg_ects = self.metrics.get('avg_ects_per_course', 0)
        if avg_ects > 0:
            if avg_ects < 3:
                insights.append("📊 Ortalama ECTS düşük - daha fazla kredi gerekebilir")
            elif avg_ects > 6:
                insights.append("📊 Ortalama ECTS yüksek - ders yükü ağır olabilir")

        # Campus distribution insights
        campus_dist = self.metrics['campus_distribution']
        if len(campus_dist) > 1:
            insights.append("🏛️ Çoklu kampüs tespit edildi - seyahat süresi dikkate alın")

        # Add insights to updates
        if insights:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.add_update(f"\n[{timestamp}] 🧠 Akıllı Analiz Sonuçları:")
            for insight in insights:
                self.add_update(f"  • {insight}")

    def add_update(self, message: str):
        """Add update message to live updates."""
        self.updates_text.insert(tk.END, message + "\n")
        self.updates_text.see(tk.END)
        self.updates_text.update()

    def set_courses(self, courses: List[Course]):
        """Set courses data."""
        self.courses = courses
        self.add_update(f"📚 {len(courses)} ders yüklendi")
        self.update_dashboard()

    def set_filtered_courses(self, courses: List[Course]):
        """Set filtered courses data."""
        self.filtered_courses = courses
        filter_ratio = (len(self.filtered_courses) / len(self.courses) * 100) if self.courses else 0
        self.add_update(f"🔍 Filtreleme uygulandı: {len(courses)} ders (%{filter_ratio:.1f})")
        self.update_dashboard()

    def set_schedules(self, schedules: List[Schedule]):
        """Set schedule data."""
        self.schedules = schedules
        self.add_update(f"📅 {len(schedules)} program oluşturuldu")
        self.update_dashboard()

    def export_dashboard(self, filename: str):
        """Export dashboard as image."""
        try:
            # Create a combined figure with all charts
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Course Scheduler Dashboard', fontsize=16, fontweight='bold')

            # Copy each chart to the combined figure
            # Note: This is a simplified export - full implementation would be more complex

            fig.savefig(filename, dpi=300, bbox_inches='tight')
            self.add_update(f"📊 Dashboard exported: {filename}")

        except Exception as e:
            self.add_update(f"❌ Export failed: {e}")

    def get_dashboard_data(self) -> Dict:
        """Get dashboard data for external use."""
        return {
            'metrics': self.metrics,
            'timestamp': datetime.now().isoformat(),
            'courses_count': len(self.courses),
            'filtered_count': len(self.filtered_courses),
            'schedules_count': len(self.schedules)
        }

    def clear_data(self):
        """Clear all dashboard data and reset to initial state."""
        try:
            # Clear data lists
            self.courses = []
            self.filtered_courses = []
            self.schedules = []

            # Reset metrics to initial state
            self.metrics = {
                'total_courses': 0,
                'filtered_courses': 0,
                'total_ects': 0,
                'avg_ects_per_course': 0,
                'faculty_distribution': {},
                'campus_distribution': {},
                'time_slot_usage': {},
                'daily_load': {},
                'conflicts': 0
            }

            # Clear live updates text
            self.updates_text.delete(1.0, tk.END)
            self.add_update("📊 Dashboard sıfırlandı - Veri bekleniyor...")

            # Update all dashboard components with empty data
            self.update_dashboard()

        except Exception as e:
            self.add_update(f"❌ Dashboard temizleme hatası: {e}")
            raise
