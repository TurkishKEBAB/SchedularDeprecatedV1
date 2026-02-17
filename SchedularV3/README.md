# SchedularV3

Advanced Course Scheduling System with PyQt6

## Features

### ✅ Phase 1 & 2 Complete (Data Layer)
- **🎓 Real Işık University Format**: Native support for Işık University Excel files
- **📅 Smart Time Parsing**: Handles "M1, M2, T3, Th5" format automatically
- **🔍 Course Type Detection**: Automatically detects lecture/lab/ps courses
- **💾 Database Integration**: SQLite for persistent storage
- **🎯 Conflict Detection**: Automatic detection of schedule conflicts
- **📊 Excel Import/Export**: Turkish character support, faculty/campus fields
- **✅ Comprehensive Testing**: 19/19 tests passing

### 🚧 Coming in Phase 3 (Scheduling Algorithms)
- **15+ Scheduling Algorithms**: DFS, A*, Genetic Algorithm, Simulated Annealing
- **Smart Optimization**: Multi-objective optimization with constraints
- **Performance Benchmarks**: Algorithm comparison and analytics

### 🚧 Coming in Phase 4+ (GUI & Reporting)
- **Modern GUI**: PyQt6-based desktop interface
- **Multiple Export Formats**: PDF, Excel, JPEG reports
- **Interactive Visualization**: Drag-and-drop schedule builder

## Installation

### Requirements

- Python 3.11 or higher
- Windows, macOS, or Linux

### Setup

1. Clone the repository or extract the archive

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
.\venv\Scripts\activate.bat

# Linux/macOS
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. **Set up environment variables (for JWT/API features):**
```bash
# Copy the example environment file
cp .env.example .env

# Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Edit .env and set SECRET_KEY to the generated value
# IMPORTANT: Never commit .env to version control!
```

**Note:** Environment variables are only required if you plan to use JWT authentication or API features. The desktop application works without them.

## Environment Variables

SchedularV3 supports environment-based configuration for security-sensitive settings. See `.env.example` for all available options.

### Required (for JWT/API features only):
- `SECRET_KEY`: JWT signing secret (minimum 32 characters)

### Optional:
- `JWT_EXPIRATION_MINUTES`: Token expiration time (default: 30)
- `JWT_ALGORITHM`: Signing algorithm (default: HS256)
- `ENVIRONMENT`: development/staging/production (default: development)
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)

### Security Best Practices:
1. **Never hardcode secrets** in source code
2. **Generate unique SECRET_KEY** for each environment (dev/staging/prod)
3. **Rotate secrets periodically** (every 90 days recommended)
4. **Use secret management tools** in production (AWS Secrets Manager, etc.)
5. **Never commit .env** to version control (it's in .gitignore)

For detailed security guidelines, see the [Security](#security) section below.

## Usage

### Quick Demo

```bash
# Run Phase 2 demo (Data Layer)
python demo_phase2.py
```

### Run the Application

```bash
python main.py
```

### Command-line Options

- `--version`: Show version information
- `-v, --verbose`: Enable verbose (DEBUG) logging
- `--no-splash`: Skip the splash screen on startup

## Real Işık University Excel Format

SchedularV3 supports the official Işık University course export format:

**Expected Columns:**
- `Ders Kodu` / Course Code (e.g., "COMP1111.1")
- `Başlık` / Course Name
- `AKTS Kredisi` / ECTS
- `Kampüs` / Campus (Şile, Online)
- `Eğitmen Adı` / Teacher First Name
- `Eğitmen Soyadı` / Teacher Last Name
- `Fakülte Adı` / Faculty Name
- `Ders Saati(leri)` / Schedule (e.g., "M1, M2, T3")

**Time Format:** 
- `M1, M2` = Monday periods 1-2
- `T6, T7, T8` = Tuesday periods 6-8
- `Th5, Th6` = Thursday periods 5-6
- `W1, W2, W3` = Wednesday periods 1-3
- `F7` = Friday period 7

**Example Usage:**

```python
from core.excel_loader import process_excel, save_courses_to_excel
from core.models import Schedule

# Load courses
courses = process_excel("my_courses.xlsx")

# Create schedule
schedule = Schedule(courses=courses[:10])
print(f"Credits: {schedule.total_credits}")
print(f"Conflicts: {schedule.conflict_count}")

# Export
save_courses_to_excel(schedule.courses, "output.xlsx")
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Type checking
mypy .

# Linting
flake8 .
```

## Project Structure

```
SchedularV3/
├── config/          # Configuration settings
├── core/            # Core business logic
├── algorithms/      # Scheduling algorithms
├── gui/             # GUI components
│   └── widgets/     # Custom widgets
├── reporting/       # Report generation
├── utils/           # Utility functions
├── tests/           # Unit tests
├── resources/       # Images, icons, styles
│   ├── icons/
│   ├── images/
│   └── styles/
├── logs/            # Application logs
└── docs/            # Documentation

```

## Security

### JWT Authentication (Future Feature)

SchedularV3 is prepared for secure JWT authentication when the FastAPI backend is implemented. The following security measures are in place:

#### ✅ Implemented Security Features:

1. **Environment-Based Secrets**
   - No hardcoded secrets in source code
   - SECRET_KEY loaded from environment variables only
   - Comprehensive `.env.example` with security guidelines

2. **Fail-Fast Validation**
   - Application validates SECRET_KEY at startup
   - Clear error messages if configuration is missing
   - Minimum length requirements (32+ characters)
   - Detection of insecure default values

3. **Secure Token Handling**
   - JWT utilities with proper error handling (`core/auth.py`)
   - Token expiration support
   - Secure signing algorithms (HS256/HS384/HS512)
   - Type-safe implementations with error types

4. **Configuration Management**
   - Centralized config in `config/settings.py`
   - Environment-specific settings support
   - Optional python-dotenv integration
   - Manual .env parsing fallback

#### 🔐 Security Best Practices:

**For Development:**
```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in .env file
SECRET_KEY=your-generated-key-here

# Never commit .env
git status  # Should not show .env file
```

**For Production:**
```bash
# Use different keys for each environment
SECRET_KEY_DEV=dev-key-here
SECRET_KEY_STAGING=staging-key-here
SECRET_KEY_PROD=prod-key-here

# Use secret management services
# - AWS Secrets Manager
# - Azure Key Vault
# - Google Cloud Secret Manager
# - HashiCorp Vault

# Rotate secrets periodically (every 90 days)
# Monitor access logs
# Use strong algorithms (HS256 minimum)
```

**Validating JWT Configuration:**
```python
from config.settings import validate_jwt_config

# At application startup
try:
    validate_jwt_config()
    print("✓ JWT configuration is secure")
except ValueError as e:
    print(f"✗ Security error: {e}")
    exit(1)
```

#### 📋 Security Checklist:

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

#### 🚀 When Implementing JWT:

1. Install dependencies:
   ```bash
   pip install python-jose[cryptography] passlib[bcrypt] python-dotenv
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY
   ```

3. Validate at startup:
   ```python
   from config.settings import validate_jwt_config
   validate_jwt_config()  # Will raise error if not configured
   ```

4. Use auth utilities:
   ```python
   from core.auth import create_access_token, verify_token
   
   # Create token
   token = create_access_token({"sub": "user123"})
   
   # Verify token
   payload = verify_token(token)
   ```

For complete implementation examples, see `core/auth.py`.

### Reporting Security Issues

If you discover a security vulnerability, please email the security team directly. Do not open a public GitHub issue for security vulnerabilities.

## License

See LICENSE file for details.

## Version

**3.0.0-alpha** - Phase 1 & 2 Complete

**Release Status:**
- ✅ Phase 1: Foundation (Complete)
- ✅ Phase 2: Data Layer (Complete)  
- 🚧 Phase 3: Scheduling Algorithms (In Progress)
- 🚧 Phase 4: GUI Layer (Planned)
- 🚧 Phase 5: Reporting (Planned)

**Test Results:**
```
19/19 tests passing (100%)
Coverage: 80% excel_loader, 60% models
```

## Authors

Course Scheduler Team
