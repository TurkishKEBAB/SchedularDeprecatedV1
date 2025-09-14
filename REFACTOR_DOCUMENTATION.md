# Course Scheduler - Refactored Architecture Documentation

## Overview
Successfully refactored the monolithic `sef.py` file (2000+ lines) into a clean, modular architecture with proper separation of concerns, enhanced functionality, and maintainable code structure.

## 🏗️ Architecture

### Core Modules (`course_scheduler/core/`)
- **`models.py`** - Data models with proper type hints and enums
  - `Course`, `Schedule`, `FilterProfile`, `SchedulerConfig`, `UserPreferences`
  - Proper dataclasses with validation and conversion methods
  
- **`parser.py`** - Robust Excel parsing with Turkish/English support
  - Header normalization (TR/EN synonyms)
  - Turkish day name mapping (`"Pzt"→"M"`, `"Per"→"Th"`)
  - Safe credit parsing with comma decimals
  - Comprehensive validation

- **`planner.py`** - Core scheduling algorithms
  - `CourseScheduler` class with DFS algorithms
  - Simulated Annealing optimization
  - Conflict detection and resolution
  - Schedule repair functionality

- **`export.py`** - Schedule output functionality
  - JPEG schedule generation
  - PDF selection matrix creation
  - Conflict report generation
  - Batch export capabilities

### Utilities (`course_scheduler/utils/`)
- **`snapshot.py`** - SQLite persistence layer
  - `SnapshotManager` for clean API
  - Snapshot saving/loading with filter profiles
  - Run result persistence
  - Legacy function compatibility

### User Interface (`course_scheduler/ui/`)
- **`app.py`** - Main application controller (MVC pattern)
- **`preview.py`** - Enhanced course preview with filtering
- **`dialogs.py`** - Course selection and snapshot dialogs
- **`charts.py`** - Analytics dashboard with matplotlib
- **`report.py`** - Interactive detailed schedule reports

## 🎯 Key Features Implemented

### Filter-First Workflow
1. **Load Excel** → Robust TR/EN parser
2. **Apply Filters** → Faculty, Department, Campus, ECTS, Days, Time slots
3. **Auto-Save Snapshot** → When proceeding with filters enabled
4. **Course Selection** → Works with filtered subset
5. **Planning** → DFS/SA operates on correct data source
6. **Auto-Save Results** → Run metadata stored in SQLite

### Enhanced Course Preview
- ✅ Rich filtering system with real-time updates
- ✅ Visual restrict indicator (red/green checkbox)
- ✅ Manual snapshot save/load with dialog
- ✅ Auto-save on proceed when restriction enabled
- ✅ Sortable columns and comprehensive search
- ✅ Time slot filters (collapsible)

### SQLite Persistence
- ✅ Snapshots table with filter profiles
- ✅ Courses table with full metadata
- ✅ Runs table with planner results
- ✅ Schedules table for generated solutions
- ✅ Data validation and cleanup utilities

### Robust Excel Parser
- ✅ Turkish header normalization: `"Ders Kodu"→"Code"`, `"AKTS"→"ECTS"`
- ✅ Turkish day mapping: `"Pzt"→"M"`, `"Çrş"→"W"`, `"Per"→"Th"`
- ✅ Comma decimal parsing: `"3,5"→3.5`
- ✅ Fallback parsing for unknown formats
- ✅ Duplicate detection and handling

## 📊 Analytics & Reporting

### Live Analytics Dashboard
- Overview charts (ECTS, conflicts, distributions)
- Detailed analysis (time slots, faculties, departments)
- Statistics summary with comprehensive metrics
- Export capabilities (PNG, data export)

### Interactive Schedule Report
- Grid-based weekly view
- Course click for detailed information
- Related sections highlighting
- Navigation between multiple schedules
- Export individual or all schedules

## 🔧 Technical Improvements

### Code Quality
- ✅ Type hints throughout
- ✅ Proper error handling
- ✅ Comprehensive logging
- ✅ Thread-safe UI updates
- ✅ Clean separation of concerns

### Performance
- ✅ Worker threads for long operations
- ✅ Efficient SQLite operations
- ✅ Optimized filtering algorithms
- ✅ Memory-efficient data structures

### Maintainability
- ✅ Modular architecture
- ✅ Clear documentation
- ✅ Consistent naming conventions
- ✅ Minimal coupling between modules

## 🚀 Usage

### Running the Application
```bash
cd C:\Users\PC\PycharmProjects\pythonProject3
python main.py
```

### Workflow
1. **File & Settings** → Load Excel file, configure scheduler
2. **Course Preview** → Apply filters, save/load snapshots
3. **Course Selection** → Choose mandatory courses with preferences
4. **Results & Analytics** → View schedules, analytics, export results

## 📁 File Structure
```
course_scheduler/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── models.py      # Data models
│   ├── parser.py      # Excel parsing
│   ├── planner.py     # Scheduling algorithms
│   └── export.py      # Output generation
├── utils/
│   ├── __init__.py
│   └── snapshot.py    # SQLite persistence
└── ui/
    ├── __init__.py
    ├── app.py         # Main application
    ├── preview.py     # Course preview tab
    ├── dialogs.py     # Dialog windows
    ├── charts.py      # Analytics charts
    └── report.py      # Detailed reports
```

## 🎯 Achievements

### Functional Requirements Met
- ✅ Filter-first workflow with auto-save
- ✅ SQLite persistence for snapshots and runs
- ✅ Turkish/English Excel parsing
- ✅ Enhanced course preview with filtering
- ✅ Interactive analytics and reporting
- ✅ Thread-safe UI with proper logging

### Code Quality Improvements
- ✅ Reduced from 2000+ lines in single file to modular structure
- ✅ Proper MVC architecture
- ✅ Type safety with dataclasses and enums
- ✅ Comprehensive error handling
- ✅ Clean API design with backwards compatibility

### User Experience Enhancements
- ✅ Modern tabbed interface
- ✅ Real-time filter updates
- ✅ Visual status indicators
- ✅ Progress feedback for long operations
- ✅ Interactive charts and reports
- ✅ Comprehensive logging display

## 🔮 Future Enhancements
- Add REST API for external integrations
- Implement user authentication and profiles
- Add course recommendation engine
- Enhanced conflict resolution algorithms
- Mobile-responsive web interface
- Advanced analytics with ML insights

---

**Migration Completed Successfully!** 
The application maintains full backwards compatibility while providing a modern, maintainable, and extensible architecture.
