# Course Scheduler

A comprehensive course scheduling application for university timetable optimization.

## Overview

This application helps university students and administrators create optimized course schedules. It loads course data from Excel files, uses advanced algorithms (DFS and Simulated Annealing) to generate conflict-free schedules, and produces detailed reports and visualizations.

## Features

- **Data Import:** Load course data from Excel files or SQLite database
- **Interactive GUI:** User-friendly interface with searchable course listings
- **Flexible Course Selection:** Select mandatory courses with frequency preferences
- **Advanced Scheduling:** Uses DFS and Simulated Annealing for optimization
- **Conflict Resolution:** Automatically minimizes course time conflicts
- **Rich Visualization:** 
  - Interactive schedule grid view
  - Analytics charts (day distribution, course types)
  - PDF reports with selection matrices
  - JPEG exports of schedules

## Project Structure

```
course_scheduler/
├── app/
│   ├── config.py               # Configuration settings
│   ├── data/
│   │   ├── excel_loader.py     # Excel data processing
│   │   ├── database.py         # SQLite integration
│   │   └── models.py           # Data models (Course, Schedule, Program)
│   ├── gui/
│   │   ├── main_window.py      # Main application window
│   │   ├── file_settings.py    # File & Settings tab
│   │   ├── course_preview.py   # Course Preview tab
│   │   ├── course_selection.py # Course Selection tab
│   │   └── schedule_report.py  # Schedule Report tab
│   ├── scheduler/
│   │   ├── dfs.py              # DFS scheduling algorithm
│   │   ├── annealing.py        # Simulated annealing optimization
│   │   └── constraints.py      # Constraint handling
│   └── reporting/
│       ├── grid.py             # Schedule grid generation
│       ├── jpeg.py             # JPEG visualization
│       ├── pdf.py              # PDF report generation
│       └── charts.py           # Analytics charts
├── main.py                     # Application entry point
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Installation

1. Clone the repository or download the source code
2. Create and activate a virtual environment (recommended)
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

Run the application using:

```
python -m course_scheduler.main
```

### Step-by-Step Usage

1. **Load Course Data**
   - In the "File & Settings" tab, browse for an Excel file containing course data
   - Configure scheduling parameters (ECTS limits, conflict allowance, etc.)
   - Click "Load Courses" to import the data

2. **Preview Courses**
   - Use the search functionality to explore available courses
   - View course details including code, name, credits, and schedule

3. **Select Courses**
   - Choose mandatory courses by clicking on them (green = included, red = excluded)
   - Set frequency preferences for each course (Always, Often, Rarely, Never)
   - Select whether to include extra courses to fill the schedule

4. **View Generated Schedules**
   - After processing, multiple schedule options will be displayed
   - Use the "Live Schedule Chart" to compare generated schedules
   - View "Detailed Schedule Report" for a visual grid representation
   - Analyze course distribution across days and by type

5. **Export and Save**
   - Schedule images are automatically saved as JPEG files
   - A PDF report with selection matrices is generated
   - View conflict reports for each schedule

## Data Format Requirements

The Excel file should contain columns for:
- **Code**: Course code (e.g., "CS101" or "CS101-PS1")
- **Lecture Name**: Course title
- **Credit**: ECTS credits (integer or decimal)
- **Hour**: Schedule in format like "M1,W2,F3" (Day+Hour)
- **Lecture Instructor** (optional): Teacher name

### Turkish Data Format Support

The application fully supports the Turkish data format with columns like:

```
Ders Kodu, Başlık, AKTS Kredisi, Kampüs, Eğitmen Adı, Eğitmen Soyadı, Fakülte Adı, Ders Saati(leri)
```

Example data format:
```
BIOL1101.1,Biyoloji (3),3,5,60,60,Şile,SİBEL,YILMAZ,"M1, M2, M3",Mühendislik ve Doğa Bilimleri Fakültesi,3,YES
```

- The application will automatically detect and map these Turkish column names
- Faculty filtering will use values from "Fakülte Adı" 
- Campus filtering will use values from "Kampüs"
- Instructor names will be combined from "Eğitmen Adı" and "Eğitmen Soyadı"

If any columns are missing, default values will be used:
- Faculty: "Unknown Faculty"
- Department: "Unknown Department"
- Campus: "Main"

## Testing

Run the test suite using pytest:

```
pytest tests/
```

## SQLite Integration

By default, the application uses Excel files for data input. To enable SQLite integration:

1. Set `DATABASE_ENABLED = True` in `app/config.py`
2. Use the "Import to Database" option in the File Settings tab
3. Once courses are imported, they can be loaded from the database for future sessions

## Development

### Adding New Features

The modular structure makes it easy to extend the application:
- Add new algorithms in the `scheduler/` package
- Create additional visualization types in `reporting/`
- Extend the data model in `data/models.py`

### Type Hints

All functions include proper type hints for better IDE integration and code checking. Use a tool like mypy to validate:

```
mypy course_scheduler
```

## Troubleshooting

Common issues:
- **Excel file not loading**: Ensure the column names match expected format
- **No schedules generated**: Try increasing ALLOW_CONFLICT or reducing mandatory courses
- **Application crashes**: Check the logs in the `logs/` directory

## License

This software is provided for educational purposes. Use and modify as needed.
