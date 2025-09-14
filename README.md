# Course Scheduler Enhancement

## Migration Notes

This project has been refactored from a single-file application to a clean, modular architecture with the following improvements:

### Breaking Changes
- Moved from single `sef.py` to modular package structure
- All imports updated to use new module paths
- Configuration now passed as parameters instead of global variables
- Thread-safe UI updates with proper progress dialogs

### New Features
- SQLite-based persistence with snapshot system
- Turkish/English Excel header support
- Realistic overlap policy (max 1 hour per course, max 2 courses with overlaps)
- Teacher preference filtering
- Fixed tri-state course selection (Include/Exclude/Neutral)
- Improved exports with legends and summaries
- Comprehensive unit tests

### File Structure
```
course_scheduler/
├── core/
│   ├── models.py          # Data classes (Course, Schedule, Config)
│   ├── parser.py          # Excel parsing with TR/EN support
│   ├── rules.py           # Conflict detection, overlap policy
│   ├── planner.py         # DFS/SA planning algorithms
│   └── export.py          # JPEG/PDF/CSV export utilities
├── ui/
│   ├── app.py             # Main application window
│   ├── wizard.py          # Course selection wizard
│   ├── dialogs.py         # Snapshot and other dialogs
│   ├── charts.py          # Analytics charts
│   └── report.py          # Detailed schedule reports
├── utils/
│   └── snapshot.py        # SQLite persistence layer
└── tests/
    └── test_*.py          # Unit tests
```

### Running the Application
```bash
python -m course_scheduler.main
```

### Testing
```bash
python -m pytest tests/ -v
```

### Headless Mode
```bash
python -m course_scheduler.headless --input courses.xlsx --mandatory "COMP101,MATH201" --output schedules/
```
