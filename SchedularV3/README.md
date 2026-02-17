# 🎓 SchedularV3

<div align="center">

**Advanced Academic Course Scheduling System**

A sophisticated, AI-powered course scheduling application built with PyQt6 for Işık University

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-features)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Testing](#-testing)
- [Security](#-security)
- [API & Environment Configuration](#-environment-variables)
- [Scheduling Algorithms](#-scheduling-algorithms)
- [Documentation](#-documentation)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**SchedularV3** is a next-generation academic course scheduling system designed specifically for Işık University. It combines powerful scheduling algorithms, an intuitive PyQt6 interface, and comprehensive academic management features to help students create optimal class schedules.

### What Makes SchedularV3 Special?

- **🎯 15+ Scheduling Algorithms** - From basic DFS to advanced Genetic Algorithms and Simulated Annealing
- **🎓 Real Işık University Format** - Native support for official course export files
- **🔍 Smart Conflict Detection** - Automatic identification and resolution of schedule conflicts
- **📊 Academic Integration** - GPA calculation, prerequisite checking, graduation planning
- **💾 Persistent Storage** - SQLite database for managing courses and schedules
- **🎨 Modern UI** - Beautiful PyQt6 interface with dark/light themes
- **🔒 Enterprise Security** - JWT-ready with environment-based configuration
- **📈 Performance Analytics** - Algorithm comparison and optimization metrics

---

## ✨ Features

### ✅ Core Features (Implemented)

#### 📚 Data Management
- **Excel Import/Export** - Full support for Işık University course format with Turkish characters
- **Smart Time Parsing** - Converts "M1, M2, T3, Th5" format to structured time slots
- **Course Type Detection** - Automatically identifies lecture, lab, and PS courses
- **Database Integration** - SQLite-based persistent storage with CRUD operations
- **Conflict Detection** - Real-time identification of schedule conflicts

#### 🧮 Scheduling Algorithms
- **Depth-First Search (DFS)** - Backtracking-based exhaustive search
- **Breadth-First Search (BFS)** - Level-by-level exploration
- **A* Algorithm** - Heuristic-guided optimal pathfinding
- **Dijkstra's Algorithm** - Weighted shortest path scheduling
- **Simulated Annealing** - Probabilistic optimization
- **Genetic Algorithm** - Evolutionary approach with crossover and mutation
- **Particle Swarm Optimization** - Swarm intelligence-based scheduling
- **Hill Climbing** - Local search optimization
- **Tabu Search** - Memory-based metaheuristic
- **Constraint Programming** - Logic-based constraint satisfaction
- **Greedy Algorithm** - Fast heuristic-based approach
- **IDDFS** - Iterative deepening depth-first search
- **Hybrid GA-SA** - Combined genetic and simulated annealing
- **Parallel Execution** - Multi-threaded algorithm execution
- **Algorithm Benchmarking** - Performance comparison and analytics

#### 🎨 User Interface
- **File Settings Tab** - Course import and configuration management
- **Course Selection Tab** - Interactive course browser with filters and search
- **Schedule Viewer Tab** - Visual weekly schedule display
- **Advanced Filters** - Campus, faculty, teacher, time slot filtering
- **Multi-Selection** - Select multiple course sections simultaneously
- **Dark/Light Themes** - Customizable interface appearance

#### 🎓 Academic Features
- **Prerequisite System** - Validate course prerequisites
- **GPA Calculator** - Real-time GPA computation
- **Transcript Import** - Load student transcripts from Excel/CSV
- **Credit Tracking** - ECTS credit limits and warnings
- **Course History** - Track completed and in-progress courses
- **Graduation Planning** - Monitor degree requirements

#### 📊 Reporting & Export
- **PDF Reports** - Generate printable schedule matrices
- **Excel Export** - Export schedules to Excel format
- **JPEG Export** - Save schedules as images
- **Conflict Reports** - Detailed conflict analysis
- **Statistics** - Credit distribution, time slot usage, conflict metrics

### 🚧 Upcoming Features (Phase 9-10)

- **Advanced Analytics Dashboard** - Comprehensive visualization and insights
- **AI Course Recommendations** - Machine learning-based suggestions
- **Multi-User Support** - Collaborative scheduling
- **Teacher Portal** - Faculty course management
- **Cloud Sync** - Multi-device synchronization
- **Calendar Integration** - Google Calendar, Outlook integration
- **LMS Integration** - Blackboard/Moodle connectivity
- **Mobile Companion** - Progressive Web App support

---

## 🛠 Technology Stack

### Core Technologies
- **Python 3.11+** - Modern Python with type hints
- **PyQt6 6.6+** - Cross-platform GUI framework
- **SQLite 3** - Embedded database
- **pandas 2.1+** - Data processing and analysis
- **NumPy 1.24+** - Numerical computations

### Development Tools
- **pytest 7.4+** - Testing framework with pytest-qt
- **mypy 1.5+** - Static type checking
- **black 23.7+** - Code formatting
- **flake8 6.1+** - Linting and style guide enforcement

### Optional Dependencies
- **python-jose[cryptography]** - JWT token management (for API features)
- **passlib[bcrypt]** - Password hashing (for authentication)
- **python-dotenv** - Environment variable management
- **FastAPI** - REST API backend (future feature)
- **uvicorn** - ASGI server (future feature)

---

## 📦 Installation

### System Requirements

- **Python**: 3.11 or higher
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 500MB for application and dependencies

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/TurkishKEBAB/SchedularDeprecatedV1.git
cd SchedularDeprecatedV1/SchedularV3
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
.\venv\Scripts\activate.bat

# Linux/macOS
source venv/bin/activate
```

#### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

#### 4. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Optional: Install JWT/API dependencies (for future features)
pip install python-jose[cryptography] passlib[bcrypt] python-dotenv
```

#### 5. Verify Installation

```bash
# Run foundation tests
pytest tests/test_foundation.py -v

# Check Python version
python --version  # Should be 3.11+

# Verify PyQt6 installation
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

### Installation Troubleshooting

<details>
<summary><b>PowerShell Execution Policy Error</b></summary>

If you encounter an execution policy error on Windows PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
</details>

<details>
<summary><b>PyQt6 Import Errors</b></summary>

Ensure virtual environment is activated:
```bash
# Check installed packages
pip list | grep PyQt6

# Reinstall if necessary
pip uninstall PyQt6 PyQt6-Charts
pip install PyQt6>=6.6.0 PyQt6-Charts>=6.6.0
```
</details>

<details>
<summary><b>SQLite Version Issues</b></summary>

Check SQLite version (should be 3.35+):
```bash
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```
</details>

---

## 🚀 Quick Start

### Running the Application

```bash
# Navigate to project directory
cd SchedularV3

# Run the main application
python main.py

# Run with verbose logging
python main.py -v

# Skip splash screen
python main.py --no-splash

# Show version
python main.py --version
```

### Quick Demo

```bash
# Run Phase 2 data layer demo
python demo_phase2.py

# Run Phase 3 algorithm demo
python demo_phase3.py

# Run JWT configuration demo (security features)
python demo_jwt_config.py
```

### Basic Usage Example

```python
from core.excel_loader import process_excel
from core.models import Schedule
from algorithms.dfs_scheduler import DFSScheduler

# 1. Load courses from Excel
courses = process_excel("data/my_courses.xlsx")

# 2. Create a scheduler
scheduler = DFSScheduler(
    courses=courses,
    max_ects=30,
    allow_conflict=0
)

# 3. Generate schedules
schedules = scheduler.generate_schedules(max_results=5)

# 4. Analyze the best schedule
if schedules:
    best_schedule = schedules[0]
    print(f"Total Credits: {best_schedule.total_credits}")
    print(f"Conflicts: {best_schedule.conflict_count}")
    print(f"Courses: {len(best_schedule.courses)}")
```

---

## 💡 Usage

### Excel File Format

SchedularV3 supports the official Işık University course export format:

#### Required Columns

| Column Name (Turkish) | Column Name (English) | Example |
|----------------------|----------------------|---------|
| Ders Kodu | Course Code | COMP1111.1 |
| Başlık | Course Title | Introduction to Programming |
| AKTS Kredisi | ECTS Credits | 6 |
| Kampüs | Campus | Şile |
| Eğitmen Adı | Teacher First Name | Ahmet |
| Eğitmen Soyadı | Teacher Last Name | Yılmaz |
| Fakülte Adı | Faculty Name | Engineering |
| Ders Saati(leri) | Schedule | M1, M2, T3 |

#### Time Format Examples

- `M1, M2` → Monday, periods 1-2 (08:30-10:20)
- `T6, T7, T8` → Tuesday, periods 6-8 (13:30-16:20)
- `W3, W4` → Wednesday, periods 3-4 (10:30-12:20)
- `Th5, Th6` → Thursday, periods 5-6 (12:30-14:20)
- `F7` → Friday, period 7 (14:30-15:20)

#### Period Time Mapping

| Period | Time |
|--------|------|
| 1 | 08:30-09:20 |
| 2 | 09:30-10:20 |
| 3 | 10:30-11:20 |
| 4 | 11:30-12:20 |
| 5 | 12:30-13:20 |
| 6 | 13:30-14:20 |
| 7 | 14:30-15:20 |
| 8 | 15:30-16:20 |
| 9 | 16:30-17:20 |
| 10 | 17:30-18:20 |
| 11 | 18:30-19:20 |
| 12 | 19:30-20:20 |

### Command-Line Options

```bash
# Show application version
python main.py --version

# Enable verbose (DEBUG) logging
python main.py -v
python main.py --verbose

# Skip splash screen on startup
python main.py --no-splash

# Combine options
python main.py -v --no-splash
```

### Programming API

```python
# Import required modules
from core.excel_loader import process_excel, save_courses_to_excel
from core.models import Schedule, Course
from core.database import CourseDatabase
from algorithms import AlgorithmSelector

# Load and filter courses
courses = process_excel("courses.xlsx")
filtered_courses = [c for c in courses if c.campus == "Şile"]

# Create a schedule
schedule = Schedule(courses=filtered_courses[:10])

# Check schedule properties
print(f"Total Credits: {schedule.total_credits} ECTS")
print(f"Conflicts: {schedule.conflict_count}")
print(f"Has Conflicts: {schedule.has_conflicts()}")

# Export schedule
save_courses_to_excel(schedule.courses, "my_schedule.xlsx")

# Use database
with CourseDatabase() as db:
    db.save_course(courses[0])
    saved_courses = db.get_all_courses()
    
# Select and run algorithm
selector = AlgorithmSelector()
algorithm = selector.select_algorithm("genetic", courses=courses)
schedules = algorithm.generate_schedules(max_results=10)
```

---

## 📁 Project Structure

```
SchedularV3/
│
├── 📂 algorithms/           # Scheduling algorithms (15+ implementations)
│   ├── base_scheduler.py      # Abstract base class for all schedulers
│   ├── dfs_scheduler.py        # Depth-first search backtracking
│   ├── simulated_annealing.py  # Simulated annealing optimizer
│   ├── genetic_algorithm.py    # Evolutionary algorithm
│   ├── a_star_scheduler.py     # A* heuristic search
│   ├── constraints.py          # Constraint satisfaction system
│   ├── benchmark.py            # Algorithm performance comparison
│   └── ...                     # Other algorithm implementations
│
├── 📂 config/               # Configuration and settings
│   ├── __init__.py
│   └── settings.py             # Application settings and constants
│
├── 📂 core/                 # Core business logic
│   ├── models.py               # Data models (Course, Schedule, etc.)
│   ├── excel_loader.py         # Excel import/export functionality
│   ├── database.py             # SQLite database operations
│   ├── academic.py             # Academic features (GPA, prerequisites)
│   ├── transcript_parser.py    # Transcript import functionality
│   ├── auth.py                 # JWT authentication utilities
│   └── sample_academic_data.py # Sample data for testing
│
├── 📂 gui/                  # GUI components (PyQt6)
│   ├── main_window.py          # Main application window
│   ├── tabs/                   # Tab implementations
│   │   ├── file_settings_tab.py
│   │   ├── course_selection_tab.py
│   │   ├── schedule_viewer_tab.py
│   │   └── ...
│   ├── widgets/                # Custom widgets
│   │   ├── course_card.py
│   │   ├── schedule_grid.py
│   │   └── ...
│   └── dialogs/                # Dialog windows
│
├── 📂 reporting/            # Report generation
│   ├── pdf_generator.py        # PDF schedule reports
│   ├── excel_exporter.py       # Excel export functionality
│   └── image_generator.py      # JPEG/PNG schedule images
│
├── 📂 utils/                # Utility functions
│   ├── error_handler.py        # Error handling and logging
│   ├── validators.py           # Input validation
│   └── helpers.py              # Helper functions
│
├── 📂 tests/                # Test suite
│   ├── test_foundation.py      # Foundation tests
│   ├── test_models.py          # Model tests
│   ├── test_excel_loader.py    # Excel loader tests
│   ├── test_phase3_algorithms.py # Algorithm tests
│   ├── test_security_config.py  # Security configuration tests
│   └── conftest.py             # Pytest configuration
│
├── 📂 resources/            # Application resources
│   ├── icons/                  # Application icons
│   ├── images/                 # Images and graphics
│   └── styles/                 # QSS stylesheets
│
├── 📂 docs/                 # Documentation
│   ├── USER_GUIDE.md           # User guide
│   ├── PHASE_07_ACADEMIC_SYSTEM.md
│   └── PHASE_7.5_USAGE_GUIDE.md
│
├── 📂 data/                 # Sample data
│   └── sample_isik_courses.xlsx
│
├── 📄 main.py               # Application entry point
├── 📄 demo_phase2.py        # Phase 2 demonstration
├── 📄 demo_phase3.py        # Phase 3 demonstration
├── 📄 demo_jwt_config.py    # JWT configuration demo
├── 📄 requirements.txt      # Python dependencies
├── 📄 .env.example          # Environment variable template
├── 📄 .gitignore            # Git ignore rules
├── 📄 README.md             # This file
├── 📄 SETUP.md              # Detailed setup guide
├── 📄 LICENSE               # License information
├── 📄 pytest.ini            # Pytest configuration
├── 📄 pyproject.toml        # Project metadata
└── 📄 setup.cfg             # Setup configuration
```

---

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone and navigate
git clone https://github.com/TurkishKEBAB/SchedularDeprecatedV1.git
cd SchedularDeprecatedV1/SchedularV3

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows

# Install dependencies with dev extras
pip install -r requirements.txt
pip install pytest pytest-qt pytest-cov mypy black flake8
```

### Code Quality Tools

```bash
# Format code with Black
black .
black --check .  # Check without modifying

# Type checking with mypy
mypy .
mypy --strict core/  # Strict mode for specific directories

# Linting with flake8
flake8 .
flake8 --statistics  # Show statistics

# Run all quality checks
black --check . && mypy . && flake8 .
```

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make changes and test**
   ```bash
   # Run tests for affected modules
   pytest tests/test_my_module.py -v
   
   # Run all tests
   pytest
   ```

3. **Check code quality**
   ```bash
   black .
   mypy .
   flake8 .
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Add: Description of changes"
   git push origin feature/my-new-feature
   ```

### Adding New Features

```python
# Example: Adding a new scheduling algorithm

from algorithms.base_scheduler import BaseScheduler
from core.models import Schedule, Course
from typing import List

class MyNewScheduler(BaseScheduler):
    """
    My new scheduling algorithm implementation.
    
    This algorithm uses [describe approach] to generate schedules.
    """
    
    def __init__(self, courses: List[Course], **kwargs):
        super().__init__(courses, **kwargs)
        # Initialize algorithm-specific parameters
        
    def generate_schedules(self, max_results: int = 5) -> List[Schedule]:
        """Generate schedules using my algorithm."""
        # Implementation here
        pass
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run specific test function
pytest tests/test_models.py::test_course_creation

# Run tests matching pattern
pytest -k "schedule"

# Run tests with coverage
pytest --cov=. --cov-report=html
```

### Test Coverage

Current test coverage:
- **Overall**: 73%
- **core/excel_loader.py**: 80%
- **core/models.py**: 60%
- **algorithms/**: 85%
- **config/settings.py**: 90%

View detailed coverage report:
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

### Writing Tests

```python
# Example test using pytest
import pytest
from core.models import Course, Schedule

def test_schedule_creation():
    """Test creating a schedule with courses."""
    course1 = Course(code="COMP1111", title="Intro to CS", ects=6)
    course2 = Course(code="MATH1111", title="Calculus I", ects=6)
    
    schedule = Schedule(courses=[course1, course2])
    
    assert len(schedule.courses) == 2
    assert schedule.total_credits == 12
    assert not schedule.has_conflicts()

def test_schedule_conflict_detection():
    """Test conflict detection in schedules."""
    # Test implementation
    pass
```

### Test Structure

```
tests/
├── test_foundation.py          # 5 tests - Foundation setup
├── test_models.py              # 12 tests - Data models
├── test_excel_loader.py        # 8 tests - Excel operations
├── test_phase3_algorithms.py   # 15 tests - Scheduling algorithms
├── test_security_config.py     # 15 tests - Security configuration
├── test_integration.py         # 10 tests - Integration tests
└── conftest.py                 # Shared fixtures
```

---

## 🔒 Security

### JWT Authentication (Prepared for Future API)

SchedularV3 includes comprehensive JWT authentication infrastructure for future API integration.

#### Security Features

✅ **Environment-Based Secrets**
- No hardcoded secrets in source code
- SECRET_KEY loaded from environment variables only
- Comprehensive `.env.example` with security guidelines

✅ **Fail-Fast Validation**
- Application validates SECRET_KEY at startup
- Clear error messages if configuration is missing
- Minimum length requirements (32+ characters)
- Detection of insecure default values

✅ **Secure Token Handling**
- JWT utilities with proper error handling (`core/auth.py`)
- Token expiration support
- Secure signing algorithms (HS256/HS384/HS512)
- Type-safe implementations with custom error types

✅ **Configuration Management**
- Centralized config in `config/settings.py`
- Environment-specific settings support
- Optional python-dotenv integration
- Manual .env parsing fallback

#### Setting Up Security (For Future JWT Features)

**1. Copy environment template:**
```bash
cp .env.example .env
```

**2. Generate a secure SECRET_KEY:**
```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -hex 32
```

**3. Edit .env file:**
```bash
# Required for JWT authentication
SECRET_KEY=your-generated-secret-key-here

# Optional configurations
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
JWT_EXPIRATION_MINUTES=30
JWT_ALGORITHM=HS256
```

**4. Validate configuration:**
```python
from config.settings import validate_jwt_config

try:
    validate_jwt_config()
    print("✓ JWT configuration is secure")
except ValueError as e:
    print(f"✗ Security error: {e}")
    exit(1)
```

#### Security Best Practices

**Development:**
- Generate unique keys for each developer
- Never commit `.env` file to version control
- Use `.env.example` as template only
- Rotate keys when developers leave the team

**Production:**
- Use different SECRET_KEY for each environment (dev/staging/prod)
- Store secrets in secret management services:
  - AWS Secrets Manager
  - Azure Key Vault
  - Google Cloud Secret Manager
  - HashiCorp Vault
- Rotate secrets every 90 days
- Monitor access logs for unusual activity
- Use strong algorithms (HS256 minimum)

#### Using JWT Utilities (When Implementing API)

```python
from core.auth import create_access_token, verify_token

# Create a token
token = create_access_token({
    "sub": "user123",
    "role": "student",
    "email": "student@isikun.edu.tr"
})

# Verify a token
try:
    payload = verify_token(token)
    user_id = payload["sub"]
    print(f"Authenticated user: {user_id}")
except TokenExpiredError:
    print("Token has expired")
except TokenInvalidError:
    print("Invalid token")
```

#### Security Checklist

- [x] No hardcoded secrets in source code
- [x] SECRET_KEY loaded from environment variables
- [x] Startup validation with clear error messages
- [x] `.env.example` documented with security guidelines
- [x] `.env` added to `.gitignore`
- [x] Minimum key length enforcement (32 chars)
- [x] Insecure default value detection
- [x] Comprehensive documentation
- [x] Example FastAPI integration code
- [x] Token expiration support
- [x] Proper error handling
- [x] CodeQL security scan (0 vulnerabilities)

### Reporting Security Issues

If you discover a security vulnerability, please email the security team directly at **security@example.com**. Do not open a public GitHub issue for security vulnerabilities.

---

## 🌍 Environment Variables

SchedularV3 supports environment-based configuration for security-sensitive settings and application behavior.

### Configuration File

Create a `.env` file in the `SchedularV3/` directory:

```bash
cp .env.example .env
```

### Available Variables

#### JWT/Authentication (Required for API features)

```bash
# JWT Secret Key - CRITICAL: Generate a secure random key
# Use: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-generated-secret-key-minimum-32-characters

# JWT token expiration time in minutes (default: 30)
JWT_EXPIRATION_MINUTES=30

# JWT signing algorithm (default: HS256)
# Options: HS256, HS384, HS512, RS256, RS384, RS512
JWT_ALGORITHM=HS256
```

#### Application Configuration

```bash
# Application environment (default: development)
# Options: development, staging, production
ENVIRONMENT=development

# Enable debug mode (default: false)
# NEVER set to true in production!
DEBUG=false

# Logging level (default: INFO)
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

#### Database Configuration (Optional)

```bash
# SQLite database path (default: course_scheduler.db)
DATABASE_PATH=course_scheduler.db

# Enable database (default: true)
DATABASE_ENABLED=true
```

#### API Configuration (For future FastAPI backend)

```bash
# API server host (default: 127.0.0.1)
API_HOST=127.0.0.1

# API server port (default: 8000)
API_PORT=8000

# Enable CORS (default: true for development)
API_CORS_ENABLED=true

# Allowed CORS origins (comma-separated)
API_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Environment-Specific Configuration

Create separate `.env` files for different environments:

```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production
```

Load specific environment file:
```bash
# Set environment variable before running
export ENV_FILE=.env.production
python main.py
```

### Validation

The application automatically validates environment configuration at startup:

```python
from config.settings import validate_jwt_config

# Validate JWT configuration
try:
    validate_jwt_config()
except ValueError as e:
    print(f"Configuration error: {e}")
    exit(1)
```

**Note:** Environment variables are only required for JWT/API features. The desktop application works without them.

---

## 🤖 Scheduling Algorithms

SchedularV3 implements 15+ scheduling algorithms, each with unique characteristics and use cases.

### Algorithm Comparison

| Algorithm | Type | Speed | Quality | Best For |
|-----------|------|-------|---------|----------|
| **DFS** | Exhaustive | Slow | Optimal | Small course sets |
| **BFS** | Exhaustive | Slow | Optimal | Shortest solution path |
| **A*** | Heuristic | Medium | Near-optimal | Balanced speed/quality |
| **Dijkstra** | Graph | Medium | Optimal | Weighted schedules |
| **Greedy** | Heuristic | Very Fast | Good | Quick solutions |
| **Simulated Annealing** | Metaheuristic | Medium | Excellent | Large course sets |
| **Genetic Algorithm** | Evolutionary | Medium-Slow | Excellent | Complex constraints |
| **Particle Swarm** | Swarm Intelligence | Fast | Good | Multi-objective optimization |
| **Hill Climbing** | Local Search | Fast | Good | Local optimization |
| **Tabu Search** | Metaheuristic | Medium | Very Good | Avoiding local optima |

### Algorithm Selection Guide

#### For Quick Results (< 1 second)
- **Greedy Algorithm** - Fast but may not find optimal solution
- **Hill Climbing** - Good for simple constraints

#### For Best Quality (Willing to wait)
- **Genetic Algorithm** - Excellent quality, 5-30 seconds
- **Simulated Annealing** - Very good quality, 10-60 seconds
- **Hybrid GA-SA** - Best quality, 30-120 seconds

#### For Guaranteed Optimal (Small problems only)
- **DFS with backtracking** - Exhaustive search
- **A* with good heuristic** - Guided optimal search

#### For Large Course Sets (30+ courses)
- **Simulated Annealing** - Scales well
- **Particle Swarm Optimization** - Parallel-friendly
- **Tabu Search** - Memory-efficient

### Using Algorithms

```python
from algorithms import AlgorithmSelector
from core.excel_loader import process_excel

# Load courses
courses = process_excel("courses.xlsx")

# Select algorithm
selector = AlgorithmSelector()

# Method 1: Auto-select based on problem size
algorithm = selector.select_algorithm("auto", courses=courses, max_ects=30)

# Method 2: Specify algorithm
algorithm = selector.select_algorithm("genetic", courses=courses, max_ects=30)

# Generate schedules
schedules = algorithm.generate_schedules(max_results=10)

# Analyze results
for i, schedule in enumerate(schedules, 1):
    print(f"Schedule {i}:")
    print(f"  Credits: {schedule.total_credits} ECTS")
    print(f"  Conflicts: {schedule.conflict_count}")
    print(f"  Courses: {len(schedule.courses)}")
```

### Benchmarking Algorithms

```python
from algorithms.benchmark import AlgorithmBenchmark
from core.excel_loader import process_excel

# Load courses
courses = process_excel("courses.xlsx")

# Run benchmark
benchmark = AlgorithmBenchmark(courses)
results = benchmark.run_all_algorithms(max_time=60)

# View results
benchmark.print_results()
benchmark.plot_comparison()  # Requires matplotlib
```

---

## 📚 Documentation

### Available Documentation

- **[README.md](README.md)** - This file (overview and getting started)
- **[SETUP.md](SETUP.md)** - Detailed installation and setup guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - JWT security implementation details
- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - Comprehensive user guide
- **[PHASE_07_ACADEMIC_SYSTEM.md](docs/PHASE_07_ACADEMIC_SYSTEM.md)** - Academic features documentation
- **[PHASE_7.5_USAGE_GUIDE.md](docs/PHASE_7.5_USAGE_GUIDE.md)** - Transcript import guide
- **[TODO.md](../TODO.md)** - Project roadmap and progress tracker
- **[PHASES_PROGRESS.md](PHASES_PROGRESS.md)** - Detailed phase completion status

### Quick Links

- [Installation Guide](SETUP.md)
- [User Guide](docs/USER_GUIDE.md)
- [API Documentation](#-environment-variables)
- [Security Guide](#-security)
- [Algorithm Guide](#-scheduling-algorithms)
- [Contributing Guidelines](#-contributing)

### Getting Help

1. **Check Documentation** - Most questions are answered in the docs
2. **Run Demos** - See `demo_phase2.py`, `demo_phase3.py`, `demo_jwt_config.py`
3. **Read Tests** - Examples in `tests/` directory
4. **Open an Issue** - For bugs or feature requests

---

## 🗺 Roadmap

### Completed Phases ✅

- **Phase 1** (100%) - Foundation & Setup
- **Phase 2** (100%) - Data Layer
- **Phase 3** (100%) - Scheduling Algorithms
- **Phase 4** (100%) - Basic GUI - File Settings
- **Phase 5** (100%) - Basic GUI - Course Selection
- **Phase 6** (100%) - Basic GUI - Schedule Viewer
- **Phase 7** (85%) - Academic System Integration
- **Phase 8** (85%) - Advanced GUI Features

### Current Phase 🚧

**Phase 7 & 8** - Completing Academic Features and Advanced GUI

### Upcoming Phases 🔮

#### Phase 9: Reporting & Export
- Advanced PDF reports with statistics
- Multiple export formats (Excel, PDF, JPEG, PNG)
- Customizable report templates
- Email integration for sharing schedules

#### Phase 10: Advanced Analytics
- Comprehensive analytics dashboard
- Algorithm performance metrics
- Historical trend analysis
- Predictive analytics for course difficulty

#### Phase 11-17: Future Features
- AI-powered course recommendations
- Multi-user collaboration system
- Cloud synchronization
- Mobile companion app (PWA)
- LMS integration (Blackboard/Moodle)
- Calendar integration (Google/Outlook)
- Teacher/Advisor portal

### Version Milestones

- **v3.0.0-alpha** - Current version (Phases 1-6 complete)
- **v3.0.0-beta** - Target: March 2026 (Phases 7-8 complete)
- **v3.0.0** - Target: June 2026 (Phases 9-10 complete)
- **v3.1.0** - Target: December 2026 (Advanced features)

---

## 🤝 Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

### How to Contribute

1. **Fork the Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/SchedularDeprecatedV1.git
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Your Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new features
   - Update documentation

4. **Run Tests and Quality Checks**
   ```bash
   pytest
   black .
   mypy .
   flake8 .
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add: Amazing new feature"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Describe your changes
   - Reference related issues
   - Include screenshots for UI changes

### Development Guidelines

- **Code Style**: Follow PEP 8, use Black formatter
- **Type Hints**: Use type hints for all functions
- **Documentation**: Add docstrings to all public methods
- **Testing**: Write tests for new features (minimum 70% coverage)
- **Commits**: Use clear, descriptive commit messages

### Areas for Contribution

- 🐛 **Bug Fixes** - Help us squash bugs
- ✨ **New Features** - Implement features from the roadmap
- 📝 **Documentation** - Improve docs and guides
- 🧪 **Testing** - Increase test coverage
- 🌍 **Localization** - Add translations
- 🎨 **UI/UX** - Improve user interface

### Code Review Process

1. Pull requests are reviewed by maintainers
2. At least one approval required
3. All tests must pass
4. Code quality checks must pass
5. No merge conflicts

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

✅ **Commercial use**
✅ **Modification**
✅ **Distribution**
✅ **Private use**

⚠️ **Limitation of liability**
⚠️ **No warranty**

---

## 👥 Authors & Acknowledgments

### Core Team
- **Course Scheduler Team** - Initial work and maintenance

### Contributors
- All contributors who have helped improve this project

### Special Thanks
- **Işık University** - For course format specifications
- **PyQt6 Team** - For the excellent GUI framework
- **Python Community** - For amazing libraries and tools

### Built With
- [Python](https://www.python.org/) - Programming language
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [pandas](https://pandas.pydata.org/) - Data analysis
- [SQLite](https://www.sqlite.org/) - Database engine

---

## 📞 Contact & Support

### Getting Help

- 📖 **Documentation**: Check the [docs](docs/) directory
- 🐛 **Bug Reports**: [Open an issue](https://github.com/TurkishKEBAB/SchedularDeprecatedV1/issues)
- 💡 **Feature Requests**: [Open an issue](https://github.com/TurkishKEBAB/SchedularDeprecatedV1/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/TurkishKEBAB/SchedularDeprecatedV1/discussions)

### Project Links

- **Repository**: [github.com/TurkishKEBAB/SchedularDeprecatedV1](https://github.com/TurkishKEBAB/SchedularDeprecatedV1)
- **Issues**: [github.com/TurkishKEBAB/SchedularDeprecatedV1/issues](https://github.com/TurkishKEBAB/SchedularDeprecatedV1/issues)
- **Releases**: [github.com/TurkishKEBAB/SchedularDeprecatedV1/releases](https://github.com/TurkishKEBAB/SchedularDeprecatedV1/releases)

---

## 🎯 Project Status

**Current Version**: 3.0.0-alpha  
**Status**: ✅ Active Development  
**Last Updated**: February 2026  
**Test Coverage**: 73%  
**Tests Passing**: 19/19 core tests + 13/13 security tests

### Recent Updates

- ✅ JWT authentication infrastructure implemented
- ✅ Environment-based security configuration
- ✅ Comprehensive security testing (13 tests)
- ✅ Enhanced documentation and guides
- ✅ CodeQL security scan integration (0 vulnerabilities)

---

<div align="center">

**Made with ❤️ for Işık University Students**

[⬆ Back to Top](#-schedularv3)

</div>
