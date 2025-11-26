# 📋 SchedularV3 - PyQt6 Edition - TODO List

> **Proje Başlangıç Tarihi:** 10 Kasım 2025  
> **Son Güncelleme:** 11 Kasım 2025  
> **Hedef Süre:** 3 Hafta  
> **Durum:** � Aktif Geliştirme - %73 Tamamlandı

---

## 🎉 SON DURUM ÖZET (11 Kasım 2025)

### ✅ TAMAMLANAN FAZLAR (6/10)

| Faz | Tamamlanma | Açıklama |
|-----|------------|----------|
| **Faz 1: Temel Yapı** | ✅ 100% | Proje yapısı, dependencies, config, main.py |
| **Faz 2: Data Katmanı** | ✅ 100% | Models, Excel loader, Database, Tests |
| **Faz 3: Algoritmalar** | ✅ 100% | 15+ scheduling algoritması implement edildi |
| **Faz 4: GUI - File Settings** | ✅ 100% | File loading, algorithm selection |
| **Faz 5: GUI - Course Selection** | ✅ 100% | Tri-state selection, course browser |
| **Faz 6: GUI - Schedule Viewer** | ✅ 100% | Schedule display, conflict highlighting |

### 🟡 DEVAM EDEN FAZLAR (2/10)

| Faz | Tamamlanma | Bekleyen Görevler |
|-----|------------|-------------------|
| **Faz 7: Academic System** | 🟡 92% | Phase 7.5: Transcript Import (60% complete) |
| **Faz 8: Advanced GUI** | 🟡 95% | Filter presets (5%), Column persistence (5%) |

### �🔴 BAŞLANMAMIŞ FAZLAR (2/10)

| Faz | Açıklama |
|-----|----------|
| **Faz 9: Reporting** | PDF/JPEG/Excel export, Charts |
| **Faz 10: Polish** | Testing, Documentation, Deployment |

---

## 📊 İMPLEMENTE EDİLEN ÖZELLİKLER

### Core Features ✅
- ✅ **Excel Import/Export**: Işık University format desteği
- ✅ **SQLite Database**: Course + Transcript persistence
- ✅ **15+ Scheduling Algorithms**:
  - DFS, BFS, IDDFS
  - A*, Greedy, Dijkstra
  - Simulated Annealing, Hill Climbing, Tabu Search
  - Genetic Algorithm, PSO, ACO
  - Hybrid GA+SA, Constraint Programming
- ✅ **Conflict Detection**: Automatic time slot conflict checking
- ✅ **Multi-objective Optimization**: Credits, conflicts, preferences

### GUI Features ✅
- ✅ **Main Window**: 5 tabs (File Settings, Browser, Selector, Viewer, Academic)
- ✅ **Course Browser Tab**:
  - Advanced filtering (Faculty, Department, Campus, Type, Teacher)
  - Quick filters (Search, Sort)
  - Multi-select & bulk operations
  - Smart group deletion
  - CSV export
  - Keyboard shortcuts
- ✅ **Course Selector Tab**:
  - Tri-state checkboxes (✅ Mandatory, ❌ Optional, Excluded)
  - Visual indicators with color coding
  - Cross-tab synchronization
- ✅ **Schedule Viewer Tab**:
  - Weekly grid (Mon-Fri, 14 periods)
  - Conflict highlighting (RED color)
  - Course details panel
  - Export buttons (PDF, JPEG, Excel)
- ✅ **Algorithm Selector**:
  - 15+ algorithms available
  - Algorithm-specific parameters
  - Performance benchmarking

### Academic Features ✅
- ✅ **Prerequisite System**:
  - Prerequisite chain visualization
  - Circular dependency detection
  - Available courses calculator
- ✅ **GPA Calculator**:
  - Current/Cumulative GPA
  - What-if simulation
  - Required GPA calculator
  - Grade scale: AA (4.0) → FF (0.0)
- ✅ **Graduation Planner**:
  - ECTS progress tracking (150/240)
  - Core courses completion
  - Timeline estimation
  - Recommended courses
- ✅ **Transcript Import** (60% complete):
  - ✅ Excel import with auto-column detection
  - ✅ Manual grade entry dialog
  - ✅ Database persistence
  - ✅ GPA visualization
  - ⏳ Auto-save/load (pending)
  - ⏳ Enhanced validation (pending)

### Performance Optimizations ✅
- ✅ **Debouncing**: 300ms delay for responsive filtering
- ✅ **Batch Updates**: Table performance optimization
- ✅ **Signal-Slot Architecture**: Cross-tab communication
- ✅ **Smart Caching**: Result caching for algorithms

---

## 📈 PROJE İSTATİSTİKLERİ

```
Toplam Kod Satırı:    ~15,000+
Python Dosyaları:     60+
Algoritma Sayısı:     15+
GUI Tabs:             5
Test Coverage:        60-80%
Commits:              50+
Branches:             1 (master)
```

---

## 🚀 ÖNCELİKLİ SONRAKI ADIMLAR

### Acil (This Week)
1. ✅ **Phase 7.5'i tamamla** (2-3 saat kaldı)
   - Auto-save/load functionality
   - Enhanced validation
   - Advanced Excel export
   
2. **Phase 9'a başla** (High Priority)
   - PDF export (reportlab)
   - JPEG export (PIL)
   - Excel export improvements
   - Charts generation

### Kısa Vadeli (Next 2 Weeks)
3. **Phase 9'u tamamla**
   - Professional reports
   - Custom templates
   - Export options
   
4. **Phase 10'a başla**
   - Comprehensive testing
   - Documentation completion
   - Bug fixes
   - Performance profiling

### Orta Vadeli (Next Month)
5. **v3.0.0 Release**
   - Beta testing
   - User feedback
   - Final polish
   - Deployment

---

## 📂 DOSYA YAPISI

```
SchedularV3/
├── core/                    ✅ 100%
│   ├── models.py           (Course, Schedule, Program, Grade, Transcript)
│   ├── database.py         (SQLite CRUD + Transcript tables)
│   ├── excel_loader.py     (Işık University format support)
│   ├── academic.py         (PrerequisiteChecker, GPACalculator, GraduationPlanner)
│   └── transcript_parser.py (Excel transcript import)
│
├── algorithms/              ✅ 100%
│   ├── base_scheduler.py   (Abstract base class)
│   ├── dfs_scheduler.py
│   ├── bfs_scheduler.py
│   ├── a_star_scheduler.py
│   ├── genetic_algorithm.py
│   ├── simulated_annealing.py
│   └── ... (15+ total)
│
├── gui/                     🟡 95%
│   ├── main_window.py      ✅
│   ├── tabs/
│   │   ├── file_settings_tab.py        ✅
│   │   ├── course_browser_tab.py       ✅
│   │   ├── course_selector_tab.py      ✅
│   │   ├── schedule_viewer_tab.py      ✅
│   │   ├── academic_tab.py             ✅
│   │   └── graduation_planner_widget.py ✅
│   ├── dialogs/
│   │   ├── transcript_import_dialog.py ✅
│   │   ├── add_grade_dialog.py         ✅
│   │   └── algorithm_comparison.py     ✅
│   └── widgets/
│       ├── schedule_grid.py            ✅
│       ├── algorithm_selector.py       ✅
│       └── progress_dialog.py          ✅
│
├── reporting/               🔴 0% (Phase 9)
│   ├── pdf_generator.py    ⏳
│   ├── jpeg_exporter.py    ⏳
│   └── charts.py           ⏳
│
├── tests/                   🟡 60%
│   ├── test_models.py      ✅
│   ├── test_excel_loader.py ✅
│   ├── test_algorithms.py   ✅
│   ├── test_academic.py     ✅
│   └── test_gui.py          ⏳
│
├── docs/                    🟡 80%
│   ├── README.md           ✅
│   ├── PHASES_PROGRESS.md  ✅
│   ├── PHASE_07_ACADEMIC_SYSTEM.md ✅
│   └── USER_GUIDE.md       ⏳
│
└── sample_transcript_yigit_okur.xlsx ✅
```

---

## 🎯 PROJE GENEL BAKIŞ

### Amaç
Üç farklı versiyon (V1.1, yedek, V2) birleştirilerek PyQt6 tabanlı modern, profesyonel bir ders çizelgeleme uygulaması oluşturmak.

### Temel Prensipler
- ✅ V2'nin profesyonel kod yapısı
- ✅ yedek'in performans optimizasyonları
- ✅ V1.1'in analytics özellikleri
- ✅ PyQt6 ile modern UI/UX

---

## 📊 İLERLEME TABLOSU

| Faz | Görev | Tahmini Süre | Durum | Tamamlanma |
|-----|-------|--------------|-------|------------|
| **Faz 1** | Temel Yapı | 1 hafta | ✅ Tamamlandı | 100% |
| **Faz 2** | Data Katmanı | 3 gün | ✅ Tamamlandı | 100% |
| **Faz 3** | Algoritmalar | 5 gün | ✅ Tamamlandı | 100% |
| **Faz 4** | GUI Geliştirme | 1.5 hafta | ✅ Tamamlandı | 100% |
| **Faz 5** | Reporting | 3 gün | 🔴 Bekliyor | 0% |
| **Faz 6** | Polish & Testing | 3 gün | 🟡 Kısmi | 40% |
| **Faz 7** | Academic System | 1 hafta | 🟡 Devam Ediyor | 92% |
| **Faz 8** | Advanced GUI | 1 hafta | � Devam Ediyor | 95% |

**Toplam İlerleme:** 73/100 ✨

---

## 🏗️ FAZ 1: TEMEL YAPI (1 Hafta) ✅ TAMAMLANDI

### 1.1 Proje Yapısı Oluşturma ✅
- [x] **SchedularV3 ana dizini oluştur**
  - [x] `SchedularV3/` klasörü
  - [x] `.gitignore` dosyası
  - [x] `README.md` dosyası
  - [x] `LICENSE` dosyası

- [x] **Alt dizin yapısını kur**
  ```
  SchedularV3/
  ├── config/
  ├── core/
  ├── algorithms/
  ├── gui/
  │   └── widgets/
  ├── reporting/
  ├── utils/
  ├── tests/
  ├── docs/
  ├── resources/
  │   ├── icons/
  │   ├── images/
  │   └── styles/
  └── logs/
  ```

### 1.2 Dependency Management ✅
- [x] **requirements.txt oluştur**
  - [x] PyQt6==6.6.1
  - [x] pandas==2.0.0
  - [x] numpy==1.24.3
  - [x] openpyxl==3.1.2
  - [x] reportlab==4.0.7
  - [x] matplotlib==3.7.1
  - [x] Pillow==10.1.0
  - [x] pytest==7.4.3
  - [x] pytest-qt==4.2.0
  - [x] pytest-cov==4.1.0
  - [x] mypy==1.7.1
  - [x] black==23.11.0
  - [x] flake8==6.1.0

- [x] **Virtual environment setup**
  - [x] Python venv oluştur
  - [x] Dependencies yükle
  - [x] Test et

### 1.3 Configuration System ✅
- [x] **config/__init__.py**
  - [x] Paket olarak işaretle

- [x] **config/settings.py**
  - [x] DEFAULT_MAX_ECTS
  - [x] DEFAULT_ALLOW_CONFLICT
  - [x] DEFAULT_MAX_RESULTS
  - [x] PERIOD_TIMES
  - [x] DAYS, DAY_FULL_NAMES
  - [x] COURSE_COLORS
  - [x] FREQUENCY_OPTIONS
  - [x] DATABASE_PATH
  - [x] Theme settings
  - [x] Window settings

### 1.4 Main Entry Point ✅
- [x] **main.py oluştur**
  - [x] Argument parser (debug, theme, vb.)
  - [x] Logging setup
  - [x] PyQt6 QApplication init
  - [x] Main window launch
  - [x] Exception handling

---

## 📦 FAZ 2: DATA KATMANI (3 Gün) ✅ TAMAMLANDI

### 2.1 Core Models ✅
- [x] **core/__init__.py**

- [x] **core/models.py**
  - [x] `Course` dataclass
    - [x] code, main_code, name
    - [x] ects, course_type
    - [x] schedule, teacher
    - [x] faculty, department, campus
    - [x] Methods: from_dict(), to_dict(), conflicts_with()
  
  - [x] `Schedule` dataclass
    - [x] courses: List[Course]
    - [x] Properties: total_credits, conflict_count
    - [x] Methods: add_course(), has_conflict_with()
  
  - [x] `CourseGroup` dataclass
    - [x] main_code, courses
    - [x] Properties: lecture_courses, ps_courses, lab_courses
  
  - [x] `Program` dataclass
    - [x] name, schedules, metadata
    - [x] Properties: best_schedule, conflict_free_schedules
    - [x] Methods: get_statistics()
  
  - [x] Helper functions
    - [x] build_course_groups()
    - [x] filter_courses_by_type()
    - [x] get_unique_main_codes()

### 2.2 Excel Loader ✅
- [x] **core/excel_loader.py**
  - [x] `process_excel()` function
  - [x] `normalize_columns()` - Türkçe/İngilizce kolon isimlerini normalize et
  - [x] `add_missing_columns()` - Faculty/Department/Campus default değerleri
  - [x] `parse_schedule()` - Zaman aralığı parsing
  - [x] `get_main_code()` - Ana ders kodunu çıkar
  - [x] `get_course_type()` - lecture/ps/lab ayırma
  - [x] Error handling ve logging

### 2.3 Database Integration ✅
- [x] **core/database.py**
  - [x] SQLite connection management
  - [x] Course CRUD operations
  - [x] Schedule persistence
  - [x] Import/Export functions
  - [x] Migration system
  - [x] Transcript tables (Phase 7.5)
  - [x] Grade persistence

### 2.4 Testing ✅
- [x] **tests/test_models.py**
  - [x] Test Course creation
  - [x] Test Schedule operations
  - [x] Test conflict detection
  - [x] Test data validation

- [x] **tests/test_excel_loader.py**
  - [x] Test Excel parsing
  - [x] Test Turkish data support
  - [x] Test error handling

---

## 🧮 FAZ 3: ALGORITMALAR (5 Gün) ✅ TAMAMLANDI

> **Başarı:** 15+ farklı scheduling algoritması implement edildi!  
> **Kullanıcı:** GUI'den algoritma seçimi yapılabiliyor  
> **Performans:** Benchmark ve karşılaştırma sistemi çalışıyor

### 3.1 Base Algorithm Interface ✅
- [x] **algorithms/__init__.py**
  - [x] Algorithm registry system
  - [x] Common imports

- [x] **algorithms/base_scheduler.py**
  - [x] `BaseScheduler` abstract class
  - [x] `AlgorithmMetadata` dataclass
  - [x] Performance tracking decorator
  - [x] Abstract methods: generate_schedules(), get_algorithm_info()

### 3.2 Complete Search Algorithms ✅

#### 3.2.1 Depth-First Search (DFS) ✅
- [x] **algorithms/dfs_scheduler.py**
  - [x] `DFSScheduler(BaseScheduler)` class
  - [x] Backtracking implementation
  - [x] Branch pruning optimization

#### 3.2.2 Breadth-First Search (BFS) ✅
- [x] **algorithms/bfs_scheduler.py**
  - [x] `BFSScheduler(BaseScheduler)` class
  - [x] Level-by-level exploration
  - [x] Queue-based implementation

#### 3.2.3 Iterative Deepening DFS (IDDFS) ✅
- [x] **algorithms/iddfs_scheduler.py**
  - [x] `IDDFSScheduler(BaseScheduler)` class
  - [x] DFS + BFS avantajlarını birleştirir

### 3.3 Informed Search Algorithms (Heuristic-Based) ✅

#### 3.3.1 A* (A-Star) ✅
- [x] **algorithms/astar_scheduler.py**
  - [x] `AStarScheduler(BaseScheduler)` class
  - [x] Priority queue (heap) kullanımı
  - [x] Heuristic functions

#### 3.3.2 Greedy Best-First Search ✅
- [x] **algorithms/greedy_scheduler.py**
  - [x] `GreedyScheduler(BaseScheduler)` class

#### 3.3.3 Dijkstra's Algorithm ✅
- [x] **algorithms/dijkstra_scheduler.py**
  - [x] `DijkstraScheduler(BaseScheduler)` class

### 3.4 Local Search & Optimization Algorithms ✅

#### 3.4.1 Simulated Annealing ✅
- [x] **algorithms/simulated_annealing.py**
  - [x] `SimulatedAnnealingScheduler(BaseScheduler)` class
  - [x] Temperature scheduling strategies

#### 3.4.2 Hill Climbing ✅
- [x] **algorithms/hill_climbing.py**
  - [x] `HillClimbingScheduler(BaseScheduler)` class

#### 3.4.3 Tabu Search ✅
- [x] **algorithms/tabu_search.py**
  - [x] `TabuSearchScheduler(BaseScheduler)` class

### 3.5 Evolutionary & Population-Based Algorithms ✅

#### 3.5.1 Genetic Algorithm ✅
- [x] **algorithms/genetic_algorithm.py**
  - [x] `GeneticAlgorithmScheduler(BaseScheduler)` class
  - [x] Selection, Crossover, Mutation operators

#### 3.5.2 Particle Swarm Optimization (PSO) ✅
- [x] **algorithms/particle_swarm.py**
  - [x] `ParticleSwarmScheduler(BaseScheduler)` class

#### 3.5.3 Ant Colony Optimization (ACO) ⏳
- [ ] **algorithms/ant_colony.py** (Planned for future)

### 3.6 Hybrid & Advanced Algorithms ✅

#### 3.6.1 Hybrid Genetic + Simulated Annealing ✅
- [x] **algorithms/hybrid_ga_sa.py**
  - [x] `HybridGASAScheduler(BaseScheduler)` class

#### 3.6.2 Memetic Algorithm ⏳
- [ ] **algorithms/memetic_algorithm.py** (Planned)

#### 3.6.3 Constraint Programming ✅
- [x] **algorithms/constraint_programming.py**
  - [x] `ConstraintProgrammingScheduler(BaseScheduler)` class

### 3.7 Machine Learning Based (Bonus) ⏳
- [ ] **algorithms/rl_scheduler.py** (Future enhancement)

### 3.8 Constraint & Utility Modules ✅

- [x] **algorithms/constraints.py**
  - [x] `ConstraintManager` class
  - [x] Hard/Soft constraints
  - [x] Constraint validation

- [x] **algorithms/heuristics.py**
  - [x] Heuristic function library
  - [x] conflict_heuristic(), credit_heuristic()

- [x] **algorithms/evaluator.py**
  - [x] `ScheduleEvaluator` class
  - [x] Multi-objective evaluation

### 3.9 Algorithm Comparison & Benchmarking ✅

- [x] **algorithms/benchmark.py**
  - [x] `AlgorithmBenchmark` class
  - [x] Performance metrics
  - [x] Comparison reports

- [x] **algorithms/algorithm_selector.py**
  - [x] `AlgorithmSelector` class
  - [x] Auto-select best algorithm

### 3.10 Multi-threading & Parallel Execution ✅

- [x] **algorithms/parallel_executor.py**
  - [x] `ParallelScheduler` class
  - [x] Thread pool management

### 3.11 Testing & Validation ✅

- [x] **tests/test_algorithms.py**
  - [x] Test each algorithm
  - [x] Performance tests
  - [x] Correctness validation
  - [ ] Best for: Karmaşık optimization, local minima'dan kaçış
  - [ ] Time: O(iterations)
  - [ ] Space: O(1) - Very memory efficient

#### 3.4.2 Hill Climbing
- [ ] **algorithms/hill_climbing.py** (YENİ)
  - [ ] `HillClimbingScheduler(BaseScheduler)` class
  - [ ] Variants:
    - [ ] Simple Hill Climbing
    - [ ] Steepest Ascent Hill Climbing
    - [ ] Stochastic Hill Climbing
    - [ ] Random-Restart Hill Climbing
  - [ ] Best for: Basit, hızlı yerel optimizasyon
  - [ ] Time: O(iterations)
  - [ ] Space: O(1)

#### 3.4.3 Tabu Search
- [ ] **algorithms/tabu_search.py** (YENİ)
  - [ ] `TabuSearchScheduler(BaseScheduler)` class
  - [ ] Tabu list management
  - [ ] Aspiration criteria
  - [ ] Short-term vs long-term memory
  - [ ] Best for: Local minima'dan kaçış, çeşitlilik
  - [ ] Time: O(iterations × neighbors)
  - [ ] Space: O(tabu_size)

### 3.5 Evolutionary & Population-Based Algorithms

#### 3.5.1 Genetic Algorithm
- [ ] **algorithms/genetic_algorithm.py** (YENİ)
  - [ ] `GeneticAlgorithmScheduler(BaseScheduler)` class
  - [ ] Chromosome encoding (schedule representation)
  - [ ] Genetic operators:
    - [ ] Selection: Tournament, Roulette Wheel, Rank-based
    - [ ] Crossover: Single-point, Two-point, Uniform
    - [ ] Mutation: Swap, Inversion, Scramble
  - [ ] Fitness function (conflict + credits + preferences)
  - [ ] Elitism support
  - [ ] Population diversity tracking
  - [ ] Best for: Geniş arama uzayı, multiple objectives
  - [ ] Time: O(generations × population × fitness)
  - [ ] Space: O(population_size)

#### 3.5.2 Particle Swarm Optimization (PSO)
- [ ] **algorithms/particle_swarm.py** (YENİ)
  - [ ] `ParticleSwarmScheduler(BaseScheduler)` class
  - [ ] Particle velocity and position
  - [ ] Personal best (pbest) tracking
  - [ ] Global best (gbest) tracking
  - [ ] Inertia weight adjustment
  - [ ] Best for: Continuous optimization (discrete'e adapt)
  - [ ] Time: O(iterations × particles)
  - [ ] Space: O(particles)

#### 3.5.3 Ant Colony Optimization (ACO)
- [ ] **algorithms/ant_colony.py** (YENİ)
  - [ ] `AntColonyScheduler(BaseScheduler)` class
  - [ ] Pheromone trails
  - [ ] Ant path construction
  - [ ] Pheromone evaporation
  - [ ] Pheromone update rules
  - [ ] Best for: Combinatorial optimization, path problems
  - [ ] Time: O(iterations × ants × graph_size)
  - [ ] Space: O(graph_size^2)

### 3.6 Hybrid & Advanced Algorithms

#### 3.6.1 Hybrid Genetic + Simulated Annealing
- [ ] **algorithms/hybrid_ga_sa.py** (YENİ)
  - [ ] `HybridGASAScheduler(BaseScheduler)` class
  - [ ] GA for global search
  - [ ] SA for local refinement
  - [ ] Best of both worlds
  - [ ] Best for: En iyi sonuçlar (biraz daha yavaş)

#### 3.6.2 Memetic Algorithm
- [ ] **algorithms/memetic_algorithm.py** (YENİ)
  - [ ] `MemeticAlgorithmScheduler(BaseScheduler)` class
  - [ ] GA + Local search combination
  - [ ] Cultural evolution simulation
  - [ ] Best for: Hard optimization problems

#### 3.6.3 Constraint Programming (CP)
- [ ] **algorithms/constraint_programming.py** (YENİ)
  - [ ] `ConstraintProgrammingScheduler(BaseScheduler)` class
  - [ ] OR-Tools integration
  - [ ] Constraint satisfaction problem (CSP)
  - [ ] Best for: Karmaşık constraint'ler

### 3.7 Machine Learning Based (Bonus)

#### 3.7.1 Reinforcement Learning
- [ ] **algorithms/rl_scheduler.py** (BONUS - İleri seviye)
  - [ ] `RLScheduler(BaseScheduler)` class
  - [ ] Q-Learning or Deep Q-Network
  - [ ] State: Current schedule state
  - [ ] Action: Add/Remove course
  - [ ] Reward: Credit optimization - conflicts
  - [ ] Best for: Öğrenen, adaptive sistem

### 3.8 Constraint & Utility Modules

- [ ] **algorithms/constraints.py** (V2'den aktar ve geliştir)
  - [ ] `ConstraintManager` class
    - [ ] Hard constraints (must satisfy)
    - [ ] Soft constraints (preference)
    - [ ] Constraint validation
    - [ ] Constraint violation penalty
  - [ ] Constraint types:
    - [ ] Time slot constraints
    - [ ] ECTS constraints
    - [ ] Teacher constraints
    - [ ] Room capacity (future)
    - [ ] Course dependency (prerequisite)

- [ ] **algorithms/heuristics.py** (YENİ)
  - [ ] Heuristic function library
  - [ ] `conflict_heuristic()` - Conflict minimization
  - [ ] `credit_heuristic()` - Credit maximization
  - [ ] `preference_heuristic()` - User preference score
  - [ ] `balance_heuristic()` - Workload distribution
  - [ ] `combined_heuristic()` - Weighted combination

- [ ] **algorithms/evaluator.py** (YENİ)
  - [ ] `ScheduleEvaluator` class
  - [ ] Multi-objective evaluation
  - [ ] Pareto front calculation
  - [ ] Normalization functions

### 3.9 Algorithm Comparison & Benchmarking

- [ ] **algorithms/benchmark.py** (YENİ)
  - [ ] `AlgorithmBenchmark` class
  - [ ] Run all algorithms on same dataset
  - [ ] Metrics:
    - [ ] Execution time
    - [ ] Memory usage
    - [ ] Solution quality (conflicts, credits)
    - [ ] Convergence rate
  - [ ] Generate comparison report
  - [ ] Export results (CSV, JSON, PDF)

- [ ] **algorithms/algorithm_selector.py** (YENİ)
  - [ ] `AlgorithmSelector` class
  - [ ] Auto-select best algorithm based on:
    - [ ] Problem size (course count)
    - [ ] Constraint complexity
    - [ ] Time limit
    - [ ] Memory limit
  - [ ] Recommendation system

### 3.10 Multi-threading & Parallel Execution

- [ ] **algorithms/parallel_executor.py** (yedek'ten ilham al)
  - [ ] `ParallelScheduler` class
  - [ ] Run multiple algorithms simultaneously
  - [ ] Thread pool management
  - [ ] Result aggregation
  - [ ] Progress tracking for each algorithm
  - [ ] Cancel support

### 3.11 Testing & Validation

- [ ] **tests/test_algorithms.py**
  - [ ] Test each algorithm separately
  - [ ] Test with various dataset sizes
  - [ ] Test edge cases
  - [ ] Performance regression tests
  - [ ] Correctness validation

- [ ] **tests/test_benchmark.py**
  - [ ] Benchmark suite
  - [ ] Algorithm comparison tests
  - [ ] Performance profiling

### 3.12 Documentation

- [ ] **docs/algorithms.md**
  - [ ] Her algoritmanın detaylı açıklaması
  - [ ] Avantaj/dezavantajlar
  - [ ] Kullanım senaryoları
  - [ ] Parametre rehberi
  - [ ] Performans karşılaştırması

---

## 📊 ALGORİTMA KARŞILAŞTIRMA TAB LOSU

| Algoritma | Hız | Kalite | Bellek | Optimal? | En İyi Kullanım |
|-----------|-----|--------|--------|----------|-----------------|
| **DFS** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | Orta boyut problemler |
| **BFS** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ✅ | Küçük problemler, optimal garanti |
| **IDDFS** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | BFS bellek + DFS hız |
| **A*** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ | En iyi genel amaçlı |
| **Greedy** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ❌ | Hızlı yaklaşık sonuç |
| **Dijkstra** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ | Weighted constraints |
| **Simulated Annealing** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | Karmaşık problemler |
| **Hill Climbing** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | Hızlı yerel optimizasyon |
| **Tabu Search** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | Local minima kaçış |
| **Genetic Algorithm** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ | Büyük arama uzayı |
| **PSO** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ | Swarm intelligence |
| **ACO** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ❌ | Path optimization |
| **Hybrid GA+SA** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ❌ | En kaliteli sonuç |
| **Constraint Programming** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ | Karmaşık kısıtlar |

**Yıldız Sistemi:** 
- ⭐ = Kötü/Yavaş
- ⭐⭐⭐ = Orta
- ⭐⭐⭐⭐⭐ = Mükemmel/Çok Hızlı

---

## 🎨 FAZ 4: GUI GELİŞTİRME (1.5 Hafta)

### 4.1 Temel Widget'lar
- [ ] **gui/widgets/__init__.py**

- [ ] **gui/widgets/course_card.py**
  - [ ] CourseCard widget (QFrame)
  - [ ] Ders bilgilerini göster
  - [ ] Click/hover effects
  - [ ] Selection state (neutral/include/exclude)

- [ ] **gui/widgets/schedule_grid.py**
  - [ ] ScheduleGrid widget (QTableWidget)
  - [ ] 7 gün x 12 saat grid
  - [ ] Drag & drop support
  - [ ] Color coding
  - [ ] Tooltip'ler

- [ ] **gui/widgets/progress_dialog.py** (yedek'ten)
  - [ ] ProgressDialog (QDialog)
  - [ ] Determinate/Indeterminate modes
  - [ ] Cancel button
  - [ ] Status message

### 4.2 Splash Screen
- [ ] **gui/splash_screen.py** (V2'den ilham al)
  - [ ] SplashScreen (QSplashScreen)
  - [ ] Üniversite logosu
  - [ ] Loading animation
  - [ ] Version bilgisi
  - [ ] Fade in/out effects

### 4.3 Main Window
- [ ] **gui/main_window.py**
  - [ ] MainWindow (QMainWindow)
  - [ ] Menu bar
    - [ ] File: Open, Save, Export, Exit
    - [ ] Edit: Preferences, Clear Cache
    - [ ] View: Theme Toggle, Fullscreen
    - [ ] Help: About, Documentation
  - [ ] Tool bar (Quick actions)
  - [ ] Status bar
  - [ ] Tab widget (4 tabs)
  - [ ] Keyboard shortcuts
  - [ ] Window state persistence

### 4.4 Tab 1: File Manager & Algorithm Settings
- [ ] **gui/file_manager.py** (V2'nin FileSettingsTab'ından - GENİŞLETİLDİ)
  - [ ] FileManagerTab (QWidget)
  - [ ] **File Input Section**
    - [ ] Excel file browser
    - [ ] Sheet selector
    - [ ] Database import/export
    - [ ] Sample data loader
  
  - [ ] **Algorithm Selection Section** ⚡ YENİ
    - [ ] Algorithm category tabs:
      - [ ] 📊 Complete Search (DFS, BFS, IDDFS)
      - [ ] 🎯 Informed Search (A*, Greedy, Dijkstra)
      - [ ] 🔄 Local Search (SA, Hill Climbing, Tabu)
      - [ ] 🧬 Evolutionary (GA, PSO, ACO)
      - [ ] 🔀 Hybrid (GA+SA, Memetic, CP)
      - [ ] 🤖 ML-Based (RL) - Bonus
    - [ ] Algorithm dropdown/list
    - [ ] Algorithm info panel:
      - [ ] Name & description
      - [ ] Time/Space complexity
      - [ ] Pros & Cons
      - [ ] Best use case
      - [ ] Recommended for current dataset
    - [ ] **Algorithm-Specific Parameters** (Dynamic UI)
      - [ ] DFS: Max depth, Pruning strategy
      - [ ] BFS: Memory limit
      - [ ] A*: Heuristic selection (dropdown)
      - [ ] SA: Initial temp, Cooling rate, Iterations
      - [ ] GA: Population size, Mutation rate, Crossover type
      - [ ] PSO: Particles, Inertia weight
      - [ ] ACO: Ants, Evaporation rate
      - [ ] Hybrid: Sub-algorithm weights
    - [ ] "Auto-Select Best Algorithm" button
    - [ ] "Compare All Algorithms" checkbox
  
  - [ ] **General Settings Panel**
    - [ ] Max ECTS slider + spinbox
    - [ ] Conflict tolerance slider
    - [ ] Max results spinbox
    - [ ] Section priority order
    - [ ] Time limit (seconds)
    - [ ] Memory limit (MB)
  
  - [ ] **Advanced Options** (Collapsible)
    - [ ] Multi-threading enable
    - [ ] Parallel algorithm execution
    - [ ] Result caching
    - [ ] Benchmark mode
  
  - [ ] Load courses button
  - [ ] Status display with progress bar

### 4.5 Tab 2: Course Browser
- [ ] **gui/course_browser.py** (V2'nin CoursePreviewTab'ından)
  - [ ] CourseBrowserTab (QWidget)
  - [ ] Search bar
    - [ ] Text search
    - [ ] Regex support
    - [ ] Filter by: Code, Name, Teacher
  - [ ] Filter panel
    - [ ] Faculty dropdown
    - [ ] Department dropdown
    - [ ] Campus dropdown
    - [ ] Course type (lecture/ps/lab)
  - [ ] Course table (QTableView)
    - [ ] Sortable columns
    - [ ] Multi-selection
    - [ ] Context menu
  - [ ] Course details panel
  - [ ] Statistics summary

### 4.6 Tab 3: Course Selector
- [ ] **gui/course_selector.py** (V2'nin CourseSelectionWindow'undan)
  - [ ] CourseSelectorTab (QWidget)
  - [ ] Course list (QListWidget)
    - [ ] Tri-state selection (neutral/include/exclude)
    - [ ] Color coding (gray/green/red)
    - [ ] Batch operations
  - [ ] Per-course settings
    - [ ] Teacher dropdown
    - [ ] Frequency radio buttons (Never/Rarely/Often/Always)
    - [ ] Fix section button
  - [ ] Summary panel
    - [ ] Total credits
    - [ ] Combination count
    - [ ] Mandatory count
  - [ ] Include extra courses checkbox
  - [ ] Generate schedules button

### 4.7 Tab 4: Schedule Viewer & Algorithm Comparison
- [ ] **gui/schedule_viewer.py** (yedek'in DetailedScheduleReport'undan - GENİŞLETİLDİ)
  - [ ] ScheduleViewerTab (QWidget)
  
  - [ ] **Schedule Display Mode**
    - [ ] Single schedule view
    - [ ] Comparison view (2-4 schedules side-by-side)
    - [ ] Algorithm comparison view ⚡ YENİ
  
  - [ ] **Schedule List Panel**
    - [ ] Schedule list (QListWidget)
    - [ ] Grouped by algorithm (if multiple ran)
    - [ ] Color-coded by quality score
    - [ ] Sort options:
      - [ ] By credits (high to low)
      - [ ] By conflicts (low to high)
      - [ ] By algorithm
      - [ ] By custom score
    - [ ] Filter options:
      - [ ] Conflict-free only
      - [ ] Credit range
      - [ ] Specific algorithm
  
  - [ ] **Navigation & Actions**
    - [ ] Navigation buttons (prev/next/first/last)
    - [ ] Jump to schedule number
    - [ ] Mark as favorite (star icon)
    - [ ] Delete schedule
  
  - [ ] **Schedule Grid Display**
    - [ ] Interactive grid (click to see course details)
    - [ ] Hover effects
    - [ ] Conflict highlighting
    - [ ] Color-coded by course type
  
  - [ ] **Course Info Panel** (V1.1'den)
    - [ ] Course details on selection
    - [ ] Related courses (PS/Lab)
    - [ ] Alternative sections
    - [ ] Teacher info
  
  - [ ] **Statistics Panel**
    - [ ] Total credits with gauge
    - [ ] Conflicts count with severity
    - [ ] Course count by type (pie chart)
    - [ ] Day distribution (bar chart)
    - [ ] Time slot heatmap
    - [ ] Workload balance score
  
  - [ ] **Algorithm Comparison Panel** ⚡ YENİ
    - [ ] Show only if multiple algorithms ran
    - [ ] Comparison table:
      - [ ] Algorithm name
      - [ ] Execution time
      - [ ] Memory used
      - [ ] Schedules found
      - [ ] Best quality score
      - [ ] Average quality
      - [ ] Success rate
    - [ ] Performance charts:
      - [ ] Time vs Quality scatter plot
      - [ ] Convergence curves
      - [ ] Pareto front visualization
    - [ ] Winner badge (best overall)
    - [ ] Export comparison report
  
  - [ ] **Export Options**
    - [ ] Export current schedule:
      - [ ] PDF (detailed report)
      - [ ] JPEG (grid image)
      - [ ] Excel (data)
      - [ ] iCalendar (.ics)
    - [ ] Export all schedules:
      - [ ] PDF bundle
      - [ ] JPEG gallery
      - [ ] Excel workbook
    - [ ] Export comparison:
      - [ ] Comparison PDF
      - [ ] CSV data
    - [ ] Print current schedule
    - [ ] Print preview
  
  - [ ] **Actions**
    - [ ] Save as template
    - [ ] Share (generate link/QR code)
    - [ ] Email schedule
    - [ ] Sync to calendar

### 4.8 Live Analytics
- [ ] **gui/live_analytics.py** (V1.1'in ScheduleAnalyticsChart'ından)
  - [ ] LiveAnalyticsWindow (QDialog)
  - [ ] Real-time chart updates
  - [ ] Charts:
    - [ ] Credits vs Conflicts (Bar chart)
    - [ ] Day distribution (Pie chart)
    - [ ] Course type distribution
    - [ ] Time slot heatmap
  - [ ] Auto-refresh option
  - [ ] Export chart as image

### 4.9 Preferences Dialog
- [ ] **gui/preferences.py** (V2'den)
  - [ ] PreferencesDialog (QDialog)
  - [ ] General tab
    - [ ] Theme selection
    - [ ] Language
    - [ ] Auto-save
  - [ ] Scheduling tab
    - [ ] Default max ECTS
    - [ ] Default conflict tolerance
    - [ ] Algorithm selection
  - [ ] UI tab
    - [ ] Font size
    - [ ] Color scheme
    - [ ] Animation speed
  - [ ] Advanced tab
    - [ ] Logging level
    - [ ] Cache settings
    - [ ] Performance options

### 4.10 Styling
- [ ] **resources/styles/light_theme.qss**
  - [ ] Light mode stylesheet

- [ ] **resources/styles/dark_theme.qss**
  - [ ] Dark mode stylesheet

- [ ] **resources/styles/custom.qss**
  - [ ] Custom widgets styling

---

## 📊 FAZ 5: REPORTING (3 Gün)

### 5.1 PDF Generator
- [ ] **reporting/__init__.py**

- [ ] **reporting/pdf_generator.py** (V2'den)
  - [ ] `save_schedules_as_pdf()`
  - [ ] `save_schedule_as_pdf()`
  - [ ] `create_conflict_report()`
  - [ ] `save_all_selection_matrices_to_pdf()`
  - [ ] ReportLab integration
  - [ ] Professional formatting
  - [ ] Page headers/footers
  - [ ] Table of contents

### 5.2 JPEG Exporter
- [ ] **reporting/jpeg_exporter.py** (V2'den)
  - [ ] `save_schedules_as_jpegs()`
  - [ ] Grid rendering
  - [ ] High-quality output
  - [ ] Watermark support
  - [ ] Batch export

### 5.3 Charts Generator
- [ ] **reporting/charts.py** (V1.1'den)
  - [ ] `generate_summary_chart()`
  - [ ] `generate_day_distribution()`
  - [ ] `generate_time_heatmap()`
  - [ ] `generate_comparison_chart()`
  - [ ] matplotlib integration
  - [ ] Interactive charts
  - [ ] Export as PNG/SVG

### 5.4 Conflict Analyzer
- [ ] **reporting/conflict_analyzer.py** (V2'den)
  - [ ] `analyze_conflicts()`
  - [ ] `find_conflict_pairs()`
  - [ ] `suggest_resolutions()`
  - [ ] `generate_conflict_matrix()`
  - [ ] Detailed conflict report

### 5.5 Excel Exporter
- [ ] **reporting/excel_exporter.py** (YENİ)
  - [ ] `export_to_excel()`
  - [ ] Multiple sheets
  - [ ] Formatted tables
  - [ ] Charts in Excel
  - [ ] openpyxl integration

---

## 🛠️ FAZ 6: POLISH & TESTING (3 Gün)

### 6.1 Error Handling
- [ ] **utils/error_handler.py**
  - [ ] Global exception handler
  - [ ] User-friendly error dialogs
  - [ ] Error logging
  - [ ] Crash recovery

### 6.2 Logging System
- [ ] **utils/logging_config.py** (V2'den)
  - [ ] Configure logging
  - [ ] File rotation
  - [ ] Different log levels
  - [ ] Performance logging

### 6.3 Cache Management
- [ ] **utils/cache_manager.py** (yedek'ten)
  - [ ] Image cache
  - [ ] Data cache
  - [ ] Cache cleanup
  - [ ] Cache statistics

### 6.4 Utilities
- [ ] **utils/schedule_utils.py** (V2'den)
  - [ ] parse_schedule()
  - [ ] format_schedule()
  - [ ] Validation functions

- [ ] **utils/metrics.py** (V2'den)
  - [ ] SchedulerPrefs dataclass
  - [ ] score_schedule()
  - [ ] meets_constraints()
  - [ ] Statistical functions

### 6.5 Unit Tests
- [ ] **tests/test_models.py** ✅
- [ ] **tests/test_excel_loader.py** ✅
- [ ] **tests/test_scheduler.py** ✅

- [ ] **tests/test_gui.py** (YENİ)
  - [ ] Test main window
  - [ ] Test tab navigation
  - [ ] Test user interactions
  - [ ] Test dialogs

- [ ] **tests/test_reporting.py** (YENİ)
  - [ ] Test PDF generation
  - [ ] Test JPEG export
  - [ ] Test chart generation

- [ ] **tests/test_integration.py** (YENİ)
  - [ ] End-to-end workflows
  - [ ] Data flow tests
  - [ ] Performance tests

### 6.6 Documentation
- [ ] **README.md güncellemesi**
  - [ ] Kurulum talimatları
  - [ ] Kullanım kılavuzu
  - [ ] Screenshot'lar
  - [ ] Özellikler listesi

- [ ] **docs/user_guide.md**
  - [ ] Detaylı kullanım kılavuzu
  - [ ] Örnek senaryolar
  - [ ] FAQ

- [ ] **docs/developer_guide.md**
  - [ ] Kod yapısı
  - [ ] API documentation
  - [ ] Katkıda bulunma rehberi

- [ ] **docs/api_reference.md**
  - [ ] Function/Class documentation
  - [ ] Parameters
  - [ ] Return values
  - [ ] Examples

### 6.7 Code Quality
- [ ] **Linting**
  - [ ] flake8 ile kod kontrolü
  - [ ] Hataları düzelt

- [ ] **Type Checking**
  - [ ] mypy ile tip kontrolü
  - [ ] Type hints ekle/düzelt

- [ ] **Formatting**
  - [ ] black ile kod formatla
  - [ ] Consistent style

- [ ] **Code Review**
  - [ ] Code smell'leri temizle
  - [ ] Performance optimization
  - [ ] Security review

### 6.8 Packaging
- [ ] **setup.py oluştur**
- [ ] **Executable build**
  - [ ] PyInstaller setup
  - [ ] Windows .exe
  - [ ] macOS .app
  - [ ] Linux binary
- [ ] **Installer**
  - [ ] Windows installer (NSIS)
  - [ ] Icon ve resources

---

## 🆕 YENİ ÖZELLİKLER (Bonus)

### Bonus 1: Advanced Features
- [ ] **Drag & Drop Course Selection**
  - [ ] Sürükle-bırak ile ders ekleme/çıkarma
  - [ ] Visual feedback

- [ ] **Real-time Validation**
  - [ ] Anlık çakışma kontrolü
  - [ ] Credit limiti uyarısı
  - [ ] Eksik ders bildirimi

- [ ] **Keyboard Shortcuts**
  - [ ] Ctrl+O: Dosya aç
  - [ ] Ctrl+S: Kaydet
  - [ ] Ctrl+E: Export
  - [ ] Ctrl+F: Arama
  - [ ] Ctrl+T: Theme toggle
  - [ ] F5: Refresh
  - [ ] Ctrl+Z: Undo
  - [ ] Ctrl+Y: Redo

- [ ] **Undo/Redo System**
  - [ ] Command pattern
  - [ ] History stack
  - [ ] Undo/Redo buttons

### Bonus 2: Data Management
- [ ] **Favorites System**
  - [ ] Favori dersleri kaydet
  - [ ] Quick access

- [ ] **Saved Searches**
  - [ ] Arama kriterlerini kaydet
  - [ ] Hızlı filtreleme

- [ ] **Schedule Templates**
  - [ ] Şablon kaydetme
  - [ ] Şablon yükleme
  - [ ] Şablon paylaşma

### Bonus 3: Export Options
- [ ] **Excel Export**
  - [ ] Detaylı Excel raporu
  - [ ] Charts dahil

- [ ] **HTML Export**
  - [ ] Web görünümü
  - [ ] Interactive HTML

- [ ] **CSV Export**
  - [ ] Basit CSV formatı
  - [ ] Veri analizi için

### Bonus 4: Visualization
- [ ] **Schedule Comparison Tool**
  - [ ] İki programı yan yana karşılaştır
  - [ ] Farkları highlight et
  - [ ] Merge options

- [ ] **Print Preview**
  - [ ] Yazdırma önizlemesi
  - [ ] Page setup
  - [ ] Print dialog

### Bonus 5: Cloud Features (Optional)
- [ ] **Cloud Sync**
  - [ ] Google Drive integration
  - [ ] OneDrive integration
  - [ ] Settings sync

- [ ] **Collaboration**
  - [ ] Programları paylaş
  - [ ] Comments/Notes
  - [ ] Version control

---

## 🎓 AKADEMİK SİSTEM ÖZELLİKLERİ (Yeni Eklemeler)

### 1. Prerequisite (Ön Koşul) Sistemi
- [ ] **Prerequisite Database**
  - [ ] `core/prerequisite.py` modülü oluştur
  - [ ] Ön koşul ilişkilerini saklama (SQLite tablo)
  - [ ] Bölüm bazlı prerequisite listeleri
  - [ ] Elle prerequisite ekleme/düzenleme UI
  - [ ] Excel'den prerequisite import
  - [ ] JSON/CSV formatında prerequisite export

- [ ] **Prerequisite Validation**
  - [ ] Ders seçiminde ön koşul kontrolü
  - [ ] Alınmış dersleri kontrol et
  - [ ] Uyarı mesajları (prerequisite eksik)
  - [ ] Suggested courses (hangi dersi alınca açılır)
  - [ ] Prerequisite chain visualization (ağaç yapısı)

- [ ] **Department-Specific Prerequisites**
  - [ ] Her bölüm için ayrı prerequisite listesi
  - [ ] Bölüm seçici dropdown
  - [ ] Template prerequisite sets (örnek veri)
  - [ ] Bulk import (her bölüm için Excel/CSV)

- [ ] **Manual Entry Interface**
  - [ ] `gui/prerequisite_editor.py` dialog
  - [ ] Ders seçici + Prerequisite ders(ler) seçici
  - [ ] Add/Remove/Edit prerequisite
  - [ ] Prerequisite türü: "Mutlak" veya "Önerilen"
  - [ ] Validation rules (circular dependency check)

### 2. GPA/CGPA Hesaplama & Simülasyon
- [ ] **Transcript Import System**
  - [ ] `core/transcript_parser.py` modülü (zaten var, genişlet)
  - [ ] CSV transcript parser
  - [ ] Excel transcript parser
  - [ ] PDF transcript OCR (optional - PyPDF2/pdfplumber)
  - [ ] Transcript validation
  - [ ] Transkript formatı template'leri

- [ ] **Grade Data Storage**
  - [ ] `courses_taken` tablosu (database)
    - [ ] course_code, course_name, ects, grade, semester, year
  - [ ] GPA history tracking
  - [ ] Semester-wise CGPA calculation

- [ ] **GPA Calculator**
  - [ ] `core/gpa_calculator.py` modülü
  - [ ] CGPA hesaplama (4.0 scale)
  - [ ] Semester GPA hesaplama
  - [ ] Passing grades filter (DD ve üstü)
  - [ ] Grade point mapping (AA=4.0, BA=3.5, ...)
  - [ ] Weighted average by ECTS

- [ ] **ECTS Limit Adjustment**
  - [ ] CGPA bazlı ECTS limiti
    - [ ] < 2.5: 31 ECTS
    - [ ] 2.5 - 3.5: 37 ECTS
    - [ ] > 3.5: 42 ECTS
  - [ ] Scheduling sırasında otomatik limit ayarlama
  - [ ] Manuel override option
  - [ ] Limit uyarıları (schedule oluştururken)

- [ ] **GPA Simulation**
  - [ ] "What-if" GPA calculator
  - [ ] Seçilen derslere not varsayımları
  - [ ] Predicted CGPA hesaplama
  - [ ] Grade goals (hedef not/CGPA)
  - [ ] Required grades for target CGPA

- [ ] **Transcript GUI**
  - [ ] `gui/transcript_tab.py` - Yeni tab
  - [ ] Transcript upload butonu
  - [ ] Grade table görüntüleme
  - [ ] CGPA/GPA display
  - [ ] Semester filter
  - [ ] Grade distribution chart (pie/bar)
  - [ ] GPA trend line chart (semester bazlı)

### 3. Graduation Planning (Mezuniyet Planlama)
- [ ] **Curriculum Database**
  - [ ] `core/curriculum.py` modülü
  - [ ] Bölüm müfredatı storage (SQLite)
  - [ ] Excel'den curriculum import
  - [ ] Curriculum table structure:
    - [ ] department, year, semester, course_code, ects, type (zorunlu/seçmeli)
  - [ ] Multiple curriculum support (farklı bölümler)

- [ ] **Curriculum Import Tool**
  - [ ] `gui/curriculum_importer.py` dialog
  - [ ] Excel file browser
  - [ ] Department selector
  - [ ] Preview curriculum table
  - [ ] Validation and import
  - [ ] Update existing curriculum

- [ ] **Graduation Tracker**
  - [ ] `core/graduation_tracker.py` modülü
  - [ ] Alınan dersleri müfredatla karşılaştır
  - [ ] Remaining courses calculation
  - [ ] Required credits (total/remaining)
  - [ ] Seçmeli requirements tracking
  - [ ] Zorunlu courses checklist
  - [ ] Graduation eligibility check

- [ ] **Graduation Planning GUI**
  - [ ] `gui/graduation_planner_tab.py` - Yeni tab
  - [ ] Department curriculum viewer
  - [ ] Completed courses checkbox list
  - [ ] Remaining courses highlight
  - [ ] Progress bars (total, zorunlu, seçmeli)
  - [ ] Projected graduation semester
  - [ ] Recommended course schedule (semester-by-semester)

- [ ] **Multi-Year Planning**
  - [ ] 4-year plan generator
  - [ ] Semester-wise course distribution
  - [ ] Load balancing (ECTS per semester)
  - [ ] Prerequisite-aware planning
  - [ ] Export as PDF/Excel

- [ ] **Manual Entry Support**
  - [ ] "Add completed course" dialog
  - [ ] Course selector + Semester/Year input
  - [ ] Grade input (for GPA)
  - [ ] Bulk entry (multiple courses)
  - [ ] Edit/Delete completed courses

### 4. Course Difficulty & Workload Estimation
- [ ] **Difficulty Rating System**
  - [ ] `core/course_difficulty.py` modülü
  - [ ] Difficulty database (1-5 scale)
  - [ ] Workload estimation (hours/week)
  - [ ] Community ratings (optional - web scraping)
  - [ ] Historical pass rates (if available)

- [ ] **Difficulty Data Collection**
  - [ ] Manuel rating input (kullanıcıdan)
  - [ ] Crowd-sourced ratings (future)
  - [ ] Teacher difficulty rating
  - [ ] Default estimates (ECTS-based)

- [ ] **Workload Calculation**
  - [ ] Weekly study hours estimation
  - [ ] Schedule total workload
  - [ ] Per-day workload distribution
  - [ ] Balance score (günler arası denge)
  - [ ] Overload warning (>X hours/week)

- [ ] **Workload Visualization**
  - [ ] `gui/workload_widget.py` widget
  - [ ] Difficulty bar chart (per course)
  - [ ] Weekly workload heatmap
  - [ ] Workload gauge (total hours)
  - [ ] Overload warnings (light/medium/heavy)

- [ ] **Smart Warnings**
  - [ ] "Bu program çok yoğun olabilir" (>50 saat/hafta)
  - [ ] "Dengeli dağılım" mesajı
  - [ ] "Bu ders zor olabilir" individual warnings
  - [ ] Suggested lighter alternatives

### 5. Multi-User & Collaboration
- [ ] **User Profile System**
  - [ ] `core/user.py` modülü
  - [ ] User database (SQLite - users table)
  - [ ] Profile fields:
    - [ ] username, password (hashed), email
    - [ ] student_id, department, current_semester
    - [ ] preferences, theme, language
  - [ ] Multi-profile support (local)

- [ ] **User Authentication**
  - [ ] Login/Logout system
  - [ ] Password hashing (bcrypt/hashlib)
  - [ ] Session management
  - [ ] Remember me option
  - [ ] Profile switching

- [ ] **Profile-Specific Data**
  - [ ] Her kullanıcı kendi:
    - [ ] Transcript data
    - [ ] Saved schedules
    - [ ] Favorite courses
    - [ ] Preferences
    - [ ] Templates
  - [ ] Data isolation (user_id foreign key)

- [ ] **Profile GUI**
  - [ ] `gui/login_dialog.py` - Login screen
  - [ ] `gui/profile_manager.py` - Profile settings
  - [ ] Profile switcher (status bar)
  - [ ] User avatar/icon
  - [ ] Profile info display

- [ ] **Friend System (Optional)**
  - [ ] Friend requests
  - [ ] Friends list
  - [ ] Share schedules with friends
  - [ ] Compare schedules
  - [ ] Friend recommendations
  - [ ] Privacy settings (public/friends/private)

- [ ] **Privacy & Isolation**
  - [ ] Her PC/session bağımsız
  - [ ] Local-only data (no cloud by default)
  - [ ] Optional cloud sync (Bonus 5)
  - [ ] Data encryption (sensitive data)

### 6. Teacher Rating & Review System
- [ ] **Teacher Database**
  - [ ] `core/teacher.py` modülü
  - [ ] Teachers table:
    - [ ] teacher_id, name, department, email
    - [ ] avg_rating, review_count
  - [ ] Teacher-Course relationship

- [ ] **Teacher Ratings**
  - [ ] Ratings table:
    - [ ] teacher_id, user_id, rating (1-5), comment, date
  - [ ] Categories:
    - [ ] Teaching quality
    - [ ] Grading fairness
    - [ ] Accessibility
    - [ ] Course organization
  - [ ] Overall average calculation

- [ ] **Review System**
  - [ ] Text reviews (with moderation)
  - [ ] Helpful votes (upvote/downvote)
  - [ ] Anonymous option
  - [ ] Edit/Delete own reviews

- [ ] **Teacher-Student Collaboration**
  - [ ] **Teacher Access Mode** 🆕
    - [ ] Öğretmen hesabı (role: teacher)
    - [ ] Student list görüntüleme (sadece izin veren)
    - [ ] Student schedule görüntüleme (read-only)
  
  - [ ] **Permission System**
    - [ ] `gui/teacher_permission_dialog.py`
    - [ ] Öğrenci: "Hocam programa müdahale edebilir mi?" checkbox
    - [ ] Permission levels:
      - [ ] None: No access
      - [ ] View: Sadece görüntüleme
      - [ ] Suggest: Öneri gönderme
      - [ ] Edit: Direkt müdahale
  
  - [ ] **Teacher Suggestions**
    - [ ] `core/teacher_suggestions.py` modülü
    - [ ] Suggestions table:
      - [ ] teacher_id, student_id, course_code, action (add/remove), reason, status
    - [ ] Öğretmen öneriler gönderir
    - [ ] Öğrenci kabul/red eder
    - [ ] Notification system
  
  - [ ] **Schedule Annotation**
    - [ ] Öğretmen X işareti koyabilir (bad choice)
    - [ ] Öğretmen ✓ işareti koyabilir (good choice)
    - [ ] Öğretmen yorum ekleyebilir
    - [ ] Öğrenci bu işaretleri görür
  
  - [ ] **Teacher Dashboard**
    - [ ] `gui/teacher_dashboard.py` - Öğretmenler için
    - [ ] My students list (izin verenler)
    - [ ] Student schedule viewer
    - [ ] Send suggestion form
    - [ ] Annotation tool
    - [ ] Student statistics

- [ ] **Teacher Rating GUI**
  - [ ] `gui/teacher_rating_widget.py`
  - [ ] Teacher search
  - [ ] Rating display (stars)
  - [ ] Write review dialog
  - [ ] Review list (most helpful first)
  - [ ] Filter by rating/date

### 7. Course Recommendation System (AI-Powered)
- [ ] **Recommendation Engine**
  - [ ] `algorithms/recommender.py` modülü
  - [ ] Collaborative filtering (user-based)
  - [ ] Content-based filtering (course features)
  - [ ] Hybrid approach

- [ ] **Recommendation Features**
  - [ ] Based on:
    - [ ] Past courses taken
    - [ ] Current major/department
    - [ ] CGPA (kolay/zor ders önerisi)
    - [ ] Interest tags
    - [ ] Similar students' choices
    - [ ] Graduation requirements
  - [ ] "Students like you also took..." suggestions
  - [ ] "To improve GPA, consider..." suggestions
  - [ ] "Popular in your department" list

- [ ] **Machine Learning (Optional)**
  - [ ] scikit-learn integration
  - [ ] Train on historical data
  - [ ] Course success prediction
  - [ ] Difficulty prediction per student

- [ ] **Recommendation GUI**
  - [ ] `gui/recommendations_widget.py`
  - [ ] Recommended courses list
  - [ ] Reason/explanation for each
  - [ ] "Add to selection" quick button
  - [ ] Refresh recommendations

### 9. Progressive Web App (PWA) 🌐
- [ ] **Web Version Architecture**
  - [ ] `web/` dizini oluştur
  - [ ] Framework seçimi:
    - [ ] Option A: Flask + React
    - [ ] Option B: FastAPI + Vue.js
    - [ ] Option C: Django + React
  - [ ] REST API backend
  - [ ] Frontend responsive design

- [ ] **PWA Features**
  - [ ] Service Worker implementation
  - [ ] Offline support
  - [ ] App manifest (manifest.json)
  - [ ] Install prompt (Add to Home Screen)
  - [ ] Push notifications
  - [ ] Background sync

- [ ] **Web UI Components**
  - [ ] Mobile-first design
  - [ ] Touch-friendly interface
  - [ ] Responsive grid layout
  - [ ] Mobile course selector
  - [ ] Mobile schedule viewer

- [ ] **Backend API**
  - [ ] `/api/courses` - Ders listesi
  - [ ] `/api/schedules` - Program oluşturma
  - [ ] `/api/user` - Profil yönetimi
  - [ ] `/api/transcript` - Transkript upload
  - [ ] WebSocket for real-time updates

- [ ] **Deployment**
  - [ ] Heroku/Vercel/Railway
  - [ ] HTTPS/SSL certificate
  - [ ] CDN integration
  - [ ] Database migration (PostgreSQL/MySQL)

### 12. Calendar Integration 📅
- [ ] **iCalendar Export**
  - [ ] `reporting/icalendar_exporter.py` modülü
  - [ ] .ics file generation
  - [ ] Event per course session
  - [ ] Recurring events (weekly)
  - [ ] VALARM (reminders)
  - [ ] Location field (classroom)

- [ ] **Calendar Sync**
  - [ ] Google Calendar API integration
  - [ ] Microsoft Outlook Calendar
  - [ ] Apple Calendar (iCloud)
  - [ ] Manual .ics import instructions

- [ ] **Calendar Features**
  - [ ] Exam dates (if available)
  - [ ] Assignment deadlines
  - [ ] Office hours
  - [ ] Custom events
  - [ ] Color coding by course

- [ ] **Calendar GUI**
  - [ ] `gui/calendar_sync_dialog.py`
  - [ ] Choose calendar service
  - [ ] Authentication (OAuth)
  - [ ] Sync settings
  - [ ] Manual download .ics button

### 13. Advanced Analytics Dashboard 📊
- [ ] **Analytics Engine**
  - [ ] `analytics/analytics_engine.py` modülü
  - [ ] Data aggregation
  - [ ] Statistical analysis
  - [ ] Trend detection
  - [ ] Anomaly detection

- [ ] **Analytics Metrics**
  - [ ] Credit distribution (per semester)
  - [ ] GPA trends (timeline)
  - [ ] Course difficulty vs performance
  - [ ] Workload vs GPA correlation
  - [ ] Teacher rating vs grades
  - [ ] Most/Least popular courses
  - [ ] Peak study hours
  - [ ] Conflict patterns

- [ ] **Dashboard GUI**
  - [ ] `gui/analytics_dashboard_tab.py` - Yeni tab
  - [ ] Multi-chart display:
    - [ ] Line charts (GPA trend)
    - [ ] Bar charts (credit distribution)
    - [ ] Pie charts (course types)
    - [ ] Heatmaps (time slot usage)
    - [ ] Scatter plots (difficulty vs grade)
  - [ ] Date range filter
  - [ ] Export charts (PNG/PDF)
  - [ ] Drill-down capability

- [ ] **Predictive Analytics**
  - [ ] Predicted graduation semester
  - [ ] GPA trajectory
  - [ ] Risk courses (might fail)
  - [ ] Optimal course load
  - [ ] Success probability

### 15. Heatmap & Visualizations 🔥
- [ ] **Heatmap Generator**
  - [ ] `reporting/heatmap.py` modülü
  - [ ] Time slot usage heatmap
  - [ ] Day-by-day intensity
  - [ ] Weekly pattern visualization
  - [ ] Matplotlib/Seaborn integration

- [ ] **Heatmap Types**
  - [ ] Schedule density heatmap
  - [ ] Workload heatmap
  - [ ] Classroom occupancy (future)
  - [ ] Popular time slots
  - [ ] Free time availability

- [ ] **Interactive Heatmap**
  - [ ] Hover for details
  - [ ] Click to filter
  - [ ] Color scale customization
  - [ ] Export as image

### 17. Study Space Finder 🏫
- [ ] **Study Space Database**
  - [ ] `core/study_spaces.py` modülü
  - [ ] Spaces table:
    - [ ] space_id, name, building, floor, capacity
    - [ ] amenities (WiFi, outlets, whiteboard)
    - [ ] open_hours, noise_level
  - [ ] Availability tracking (optional)

- [ ] **Study Space Features**
  - [ ] List view (with filters)
  - [ ] Filter by:
    - [ ] Building/Campus
    - [ ] Capacity (group study)
    - [ ] Noise level (quiet/moderate/loud)
    - [ ] Amenities
    - [ ] Availability
  - [ ] Map view (optional - building map)
  - [ ] Favorites

- [ ] **Study Space GUI**
  - [ ] `gui/study_spaces_tab.py` - Yeni tab
  - [ ] Search & filter
  - [ ] List/Grid view
  - [ ] Space details
  - [ ] Directions/Location
  - [ ] User ratings/reviews

### 21. Achievement System 🏆
- [ ] **Achievement Engine**
  - [ ] `gamification/achievements.py` modülü
  - [ ] Achievements table:
    - [ ] achievement_id, name, description, icon, points
  - [ ] User achievements (unlocked tracking)
  - [ ] Progress tracking

- [ ] **Achievement Types**
  - [ ] Academic:
    - [ ] "Dean's List" (CGPA > 3.5)
    - [ ] "Perfect Schedule" (no conflicts)
    - [ ] "Early Bird" (first to register)
    - [ ] "Overachiever" (42 ECTS)
  - [ ] Usage:
    - [ ] "First Schedule" (created first schedule)
    - [ ] "Explorer" (tried 5+ algorithms)
    - [ ] "Optimizer" (used advanced features)
  - [ ] Social:
    - [ ] "Helpful" (shared X schedules)
    - [ ] "Popular" (X friends)

- [ ] **Points & Levels**
  - [ ] XP system
  - [ ] Level progression (1-100)
  - [ ] Leaderboard (optional)
  - [ ] Badges/Icons

- [ ] **Achievement GUI**
  - [ ] `gui/achievements_widget.py`
  - [ ] Achievement gallery
  - [ ] Progress bars
  - [ ] Locked/Unlocked states
  - [ ] Notification on unlock
  - [ ] Profile badge display

### 22. Motivational Features 💪
- [ ] **Daily Quotes/Tips**
  - [ ] Motivational quotes database
  - [ ] Daily tip system
  - [ ] Display on splash/dashboard
  - [ ] Category: Study, Success, Productivity

- [ ] **Goal Setting**
  - [ ] Set semester goals (GPA target)
  - [ ] Course completion goals
  - [ ] Study hour goals
  - [ ] Progress tracking
  - [ ] Goal reminders

- [ ] **Streaks**
  - [ ] Login streak
  - [ ] Study streak (calendar integration)
  - [ ] Streak counter
  - [ ] Streak rewards

- [ ] **Progress Visualization**
  - [ ] Progress rings/circles
  - [ ] Completion percentage
  - [ ] Milestone celebrations
  - [ ] Confetti animation 🎉

### 23. Security & Privacy 🔒
- [ ] **Data Encryption**
  - [ ] `utils/encryption.py` modülü
  - [ ] Password hashing (bcrypt)
  - [ ] Sensitive data encryption (AES)
  - [ ] Secure storage

- [ ] **Privacy Settings**
  - [ ] `gui/privacy_settings.py` dialog
  - [ ] Data sharing preferences
  - [ ] Anonymous mode
  - [ ] Data deletion (GDPR)
  - [ ] Export personal data

- [ ] **Security Features**
  - [ ] Session timeout
  - [ ] Auto-logout
  - [ ] Failed login attempts limit
  - [ ] Two-factor authentication (optional)
  - [ ] Activity log

### 24. Backup & Recovery 💾
- [ ] **Automatic Backup**
  - [ ] `utils/backup.py` modülü
  - [ ] Scheduled backups (daily/weekly)
  - [ ] Incremental backups
  - [ ] Cloud backup (optional)
  - [ ] Local backup (zip files)

- [ ] **Backup Features**
  - [ ] Backup schedule/data
  - [ ] Backup preferences
  - [ ] Backup to:
    - [ ] Local folder
    - [ ] USB drive
    - [ ] Cloud (Dropbox/Google Drive)
  - [ ] Backup history (list)

- [ ] **Recovery System**
  - [ ] Restore from backup
  - [ ] Point-in-time recovery
  - [ ] Selective restore (specific data)
  - [ ] Backup validation
  - [ ] Corruption detection

- [ ] **Backup GUI**
  - [ ] `gui/backup_dialog.py`
  - [ ] Backup now button
  - [ ] Restore button
  - [ ] Backup settings
  - [ ] Backup history viewer

### 25. AI Assistant (Chatbot) 🤖
- [ ] **Chatbot Engine**
  - [ ] `ai/chatbot.py` modülü
  - [ ] NLP integration (spaCy/NLTK)
  - [ ] Intent recognition
  - [ ] Response generation
  - [ ] Context management

- [ ] **Chatbot Features**
  - [ ] Help with scheduling
  - [ ] Answer FAQ
  - [ ] Course recommendations
  - [ ] Tutorial walkthrough
  - [ ] Quick actions (voice commands)

- [ ] **AI Integration (Optional)**
  - [ ] OpenAI GPT API
  - [ ] Local LLM (llama.cpp)
  - [ ] RAG (Retrieval-Augmented Generation)
  - [ ] Fine-tuned on university data

- [ ] **Chatbot GUI**
  - [ ] `gui/chatbot_widget.py`
  - [ ] Chat interface (messaging style)
  - [ ] Quick reply buttons
  - [ ] Voice input (optional)
  - [ ] Chat history
  - [ ] Minimize/Maximize

### 26. Auto-Schedule with AI 🧠
- [ ] **AI Auto-Scheduler**
  - [ ] `ai/auto_scheduler.py` modülü
  - [ ] ML-based scheduling
  - [ ] Learn from user preferences
  - [ ] Personalized recommendations
  - [ ] One-click optimal schedule

- [ ] **Learning System**
  - [ ] Track user choices
  - [ ] Preference learning (what user selects/rejects)
  - [ ] Adapt to patterns
  - [ ] Feedback loop (rating schedules)

- [ ] **AI Features**
  - [ ] "Generate best schedule for me"
  - [ ] Predict which schedule user will like
  - [ ] Suggest improvements
  - [ ] Explain decisions (interpretability)

### 27. Predictive Analytics 📈
- [ ] **Prediction Models**
  - [ ] `ai/prediction.py` modülü
  - [ ] Grade prediction (per course)
  - [ ] CGPA prediction (end of semester)
  - [ ] Course difficulty prediction
  - [ ] Success probability
  - [ ] Time to graduation

- [ ] **ML Models (Optional)**
  - [ ] scikit-learn models:
    - [ ] Regression (GPA prediction)
    - [ ] Classification (pass/fail)
    - [ ] Clustering (student groups)
  - [ ] Feature engineering
  - [ ] Model training pipeline
  - [ ] Model evaluation

- [ ] **Prediction GUI**
  - [ ] `gui/predictions_widget.py`
  - [ ] "What-if" scenarios
  - [ ] Prediction confidence
  - [ ] Visualization (charts)
  - [ ] Suggestions to improve

### 28. Course Materials Hub 📚
- [ ] **Materials Integration**
  - [ ] `core/course_materials.py` modülü
  - [ ] Materials database:
    - [ ] material_id, course_code, type, title, url, file_path
  - [ ] Types: syllabus, slides, notes, assignments, exams

- [ ] **LMS Integration**
  - [ ] **Blackboard Integration**
    - [ ] Blackboard API/scraper
    - [ ] Login authentication
    - [ ] Course list fetch
    - [ ] Materials download (PDF, PPTX, etc.)
  
  - [ ] **Moodle Integration**
    - [ ] Moodle Web Services API
    - [ ] Course content fetch
    - [ ] Assignment deadlines
    - [ ] Announcements

  - [ ] **Generic LMS Support**
    - [ ] Web scraping (Beautiful Soup)
    - [ ] Selenium automation (if needed)
    - [ ] File download management

- [ ] **Materials Manager**
  - [ ] Local storage (organized by course)
  - [ ] Sync with LMS
  - [ ] Version tracking (new materials)
  - [ ] Offline access

- [ ] **Materials GUI**
  - [ ] `gui/materials_tab.py` - Yeni tab
  - [ ] Course materials browser
  - [ ] Folder tree view
  - [ ] File preview (PDF/Image)
  - [ ] Download/Open file
  - [ ] Search materials
  - [ ] Sync button

- [ ] **Automatic Fetching**
  - [ ] Scheduled sync (daily)
  - [ ] Notification (new materials)
  - [ ] Background download
  - [ ] Storage management

### 29. Study Planner 📖
- [ ] **Study Planner Module**
  - [ ] `planner/study_planner.py` modülü
  - [ ] Study sessions database:
    - [ ] session_id, course_code, date, start_time, end_time, topic, completed
  - [ ] Weekly study plan generator

- [ ] **Planning Features**
  - [ ] Auto-generate study schedule
  - [ ] Based on:
    - [ ] Course schedule (avoid conflicts)
    - [ ] Course difficulty
    - [ ] Exam dates
    - [ ] Assignment deadlines
  - [ ] Allocate study hours per course
  - [ ] Break time recommendations
  - [ ] Spaced repetition scheduling

- [ ] **Study Sessions**
  - [ ] Plan study sessions
  - [ ] Set reminders
  - [ ] Track completion
  - [ ] Pomodoro timer integration
  - [ ] Study log/journal

- [ ] **Study Planner GUI**
  - [ ] `gui/study_planner_tab.py` - Yeni tab
  - [ ] Weekly view (calendar grid)
  - [ ] Add/Edit study session
  - [ ] Mark as completed
  - [ ] Study statistics (hours studied)
  - [ ] Progress per course

### 36. Performance Enhancements ⚡
- [ ] **Optimization Techniques**
  - [ ] Code profiling (cProfile)
  - [ ] Bottleneck identification
  - [ ] Algorithm optimization
  - [ ] Database indexing
  - [ ] Query optimization (SQL)

- [ ] **Caching System**
  - [ ] Redis integration (optional)
  - [ ] In-memory cache (LRU)
  - [ ] Result caching
  - [ ] Image caching
  - [ ] API response caching

- [ ] **Lazy Loading**
  - [ ] Defer heavy operations
  - [ ] Load on demand
  - [ ] Pagination (large lists)
  - [ ] Virtual scrolling

- [ ] **Multi-threading**
  - [ ] Background tasks
  - [ ] Parallel algorithm execution
  - [ ] Async I/O (asyncio)
  - [ ] Worker threads

### 37. Scalability 📏
- [ ] **Database Optimization**
  - [ ] Migration to PostgreSQL (optional)
  - [ ] Connection pooling
  - [ ] Indexing strategy
  - [ ] Query optimization
  - [ ] Partitioning (large tables)

- [ ] **Microservices (Optional)**
  - [ ] Separate services:
    - [ ] Auth service
    - [ ] Scheduling service
    - [ ] Analytics service
  - [ ] API Gateway
  - [ ] Load balancing

- [ ] **Horizontal Scaling**
  - [ ] Stateless architecture
  - [ ] Session management (Redis)
  - [ ] CDN for static assets
  - [ ] Database replication

### 38. Advanced Theming 🎨
- [ ] **Theme System**
  - [ ] `themes/` dizini
  - [ ] Theme files (.json/.qss)
  - [ ] Dynamic theme loading
  - [ ] Theme preview

- [ ] **Built-in Themes**
  - [ ] Light (default)
  - [ ] Dark (default)
  - [ ] High contrast
  - [ ] Solarized
  - [ ] Dracula
  - [ ] Nord
  - [ ] University branded (customizable)

- [ ] **Theme Editor**
  - [ ] `gui/theme_editor.py` dialog
  - [ ] Color picker
  - [ ] Font selector
  - [ ] Live preview
  - [ ] Save custom theme
  - [ ] Export/Import theme

- [ ] **Theming Options**
  - [ ] Accent color
  - [ ] Background color
  - [ ] Font family/size
  - [ ] Border radius
  - [ ] Spacing/Padding
  - [ ] Icon style

### 39. Widget Customization 🧩
- [ ] **Dashboard Customization**
  - [ ] Drag-and-drop widgets
  - [ ] Resizable widgets
  - [ ] Show/Hide widgets
  - [ ] Widget layout save

- [ ] **Custom Widgets**
  - [ ] Clock widget
  - [ ] Weather widget (optional)
  - [ ] Quote widget
  - [ ] GPA widget
  - [ ] Upcoming classes widget
  - [ ] Tasks/To-do widget

- [ ] **Widget Store (Bonus)**
  - [ ] Plugin architecture
  - [ ] Community widgets
  - [ ] Install/Uninstall widgets

### 40. Research & Export 🔬
- [ ] **Data Export**
  - [ ] Export all data:
    - [ ] Schedules (CSV/Excel/JSON)
    - [ ] Grades (CSV/Excel)
    - [ ] Analytics (CSV/Excel)
    - [ ] Ratings (CSV)
  - [ ] Batch export
  - [ ] Scheduled exports

- [ ] **Research Tools**
  - [ ] Data anonymization
  - [ ] Statistical reports
  - [ ] Aggregated data
  - [ ] Visualization export
  - [ ] Research-ready datasets

- [ ] **API for Researchers**
  - [ ] REST API endpoints
  - [ ] API documentation
  - [ ] Rate limiting
  - [ ] Authentication (API keys)

### 41. A/B Testing Framework 🧪
- [ ] **A/B Testing System**
  - [ ] `testing/ab_testing.py` modülü
  - [ ] Experiment configuration
  - [ ] User assignment (random)
  - [ ] Variant tracking
  - [ ] Metrics collection

- [ ] **Testing Features**
  - [ ] Test UI variations
  - [ ] Test algorithm performance
  - [ ] Test feature adoption
  - [ ] Statistical significance
  - [ ] Results dashboard

- [ ] **A/B Testing GUI**
  - [ ] `gui/ab_testing_admin.py` (admin only)
  - [ ] Create experiment
  - [ ] Monitor results
  - [ ] End experiment
  - [ ] Winner selection

---

## 🎓 IMPLEMENTATİON NOTES - Özel Sistemler

### Prerequisite Sistemi - İmplementasyon Detayı
```python
# core/prerequisite.py
class Prerequisite:
    course_code: str
    prerequisite_codes: List[str]  # Birden fazla ön koşul olabilir
    type: str  # "mandatory" veya "recommended"
    
class PrerequisiteManager:
    def check_prerequisites(self, course, taken_courses):
        """Ön koşulları kontrol et"""
        pass
    
    def get_available_courses(self, taken_courses):
        """Alabileceği dersleri döndür"""
        pass
    
    def import_from_excel(self, file_path, department):
        """Excel'den ön koşulları içe aktar"""
        pass
```

### GPA Sistemi - İmplementasyon Detayı
```python
# core/gpa_calculator.py
GRADE_POINTS = {
    'AA': 4.0, 'BA': 3.5, 'BB': 3.0, 'CB': 2.5,
    'CC': 2.0, 'DC': 1.5, 'DD': 1.0, 'FD': 0.5, 'FF': 0.0
}

def calculate_cgpa(grades_df):
    """CGPA hesapla (ECTS ağırlıklı)"""
    total_points = (grades_df['grade_point'] * grades_df['ects']).sum()
    total_ects = grades_df['ects'].sum()
    return total_points / total_ects if total_ects > 0 else 0.0

def get_ects_limit(cgpa):
    """CGPA'ya göre ECTS limiti"""
    if cgpa < 2.5:
        return 31
    elif cgpa < 3.5:
        return 37
    else:
        return 42
```

### Teacher-Student Sistem - İmplementasyon Detayı
```python
# core/teacher_suggestions.py
class TeacherSuggestion:
    teacher_id: int
    student_id: int
    course_code: str
    action: str  # "add" veya "remove"
    reason: str
    status: str  # "pending", "accepted", "rejected"
    created_at: datetime

class TeacherStudentManager:
    def get_students_with_permission(self, teacher_id):
        """Öğretmenin erişebileceği öğrenciler"""
        pass
    
    def send_suggestion(self, suggestion):
        """Öneri gönder"""
        pass
    
    def annotate_schedule(self, teacher_id, student_id, course_code, mark):
        """Ders üzerine işaret koy (X veya ✓)"""
        pass
```

### LMS Integration - İmplementasyon Detayı
```python
# core/lms_integrations.py
class BlackboardScraper:
    def login(self, username, password):
        """Blackboard'a giriş yap"""
        pass
    
    def get_courses(self):
        """Ders listesi"""
        pass
    
    def download_materials(self, course_id, save_dir):
        """Ders materyallerini indir"""
        pass

class MoodleAPI:
    def __init__(self, url, token):
        self.url = url
        self.token = token
    
    def get_course_contents(self, course_id):
        """Moodle API ile içerik al"""
        pass
```

---

## 📊 YENİ ÖZELLİKLER ÖNCEL İK MATR İSİ

| # | Özellik | Öncelik | Zorluk | Tahmini Süre |
|---|---------|---------|--------|--------------|
| 1 | Prerequisite Sistemi | 🔴 Yüksek | Orta | 3 gün |
| 2 | GPA/CGPA Hesaplama | 🔴 Yüksek | Orta | 4 gün |
| 3 | Graduation Planning | 🔴 Yüksek | Yüksek | 5 gün |
| 4 | Course Difficulty | 🟡 Orta | Düşük | 2 gün |
| 5 | Multi-User System | 🔴 Yüksek | Yüksek | 5 gün |
| 6 | Teacher-Student System | 🟡 Orta | Yüksek | 4 gün |
| 7 | Course Recommendation | 🟡 Orta | Yüksek | 5 gün |
| 9 | Progressive Web App | 🟢 Düşük | Çok Yüksek | 15 gün |
| 12 | Calendar Integration | 🟡 Orta | Orta | 3 gün |
| 13 | Analytics Dashboard | 🟡 Orta | Orta | 4 gün |
| 15 | Heatmap Visualizations | 🟢 Düşük | Düşük | 2 gün |
| 17 | Study Space Finder | 🟢 Düşük | Düşük | 2 gün |
| 21 | Achievement System | 🟢 Düşük | Orta | 3 gün |
| 22 | Motivational Features | 🟢 Düşük | Düşük | 2 gün |
| 23 | Security & Privacy | 🔴 Yüksek | Orta | 3 gün |
| 24 | Backup & Recovery | 🟡 Orta | Orta | 3 gün |
| 25 | AI Chatbot | 🟢 Düşük | Yüksek | 5 gün |
| 26 | Auto-Schedule AI | 🟡 Orta | Yüksek | 5 gün |
| 27 | Predictive Analytics | 🟢 Düşük | Yüksek | 5 gün |
| 28 | Course Materials Hub | 🟡 Orta | Çok Yüksek | 8 gün |
| 29 | Study Planner | 🟡 Orta | Orta | 4 gün |
| 36 | Performance Enhancements | 🔴 Yüksek | Orta | Sürekli |
| 37 | Scalability | 🟢 Düşük | Yüksek | 7 gün |
| 38 | Advanced Theming | 🟢 Düşük | Düşük | 2 gün |
| 39 | Widget Customization | 🟢 Düşük | Orta | 3 gün |
| 40 | Research & Export | 🟢 Düşük | Düşük | 2 gün |
| 41 | A/B Testing | 🟢 Düşük | Orta | 3 gün |

**Toplam Tahmini Süre:** ~100+ gün (3-4 ay)

---

## 🎯 ROADMAP - Genişletilmiş

### Sprint 1 (Hafta 1-3): Temel Sistem ✅
- Faz 1-6 (Mevcut plan)

### Sprint 2 (Hafta 4-5): Akademik Özellikler 🎓
- Prerequisite sistemi
- GPA/CGPA hesaplama
- Transcript import
- Graduation planning

### Sprint 3 (Hafta 6-7): Kullanıcı Sistemi 👥
- Multi-user/Profile system
- Teacher-Student collaboration
- Security & Privacy
- Backup & Recovery

### Sprint 4 (Hafta 8-9): Akıllı Özellikler 🤖
- Course recommendation
- AI Chatbot
- Auto-Schedule AI
- Course difficulty estimation

### Sprint 5 (Hafta 10-11): İçerik & Planlama 📚
- Course materials hub (LMS integration)
- Study planner
- Calendar integration
- Analytics dashboard

### Sprint 6 (Hafta 12-13): Gamification & UX 🎮
- Achievement system
- Motivational features
- Advanced theming
- Widget customization
- Heatmaps & visualizations

### Sprint 7 (Hafta 14-15): Web & Mobile 🌐
- Progressive Web App
- Responsive design
- API development
- Deployment

### Sprint 8 (Hafta 16+): Advanced & Optional 🚀
- Predictive analytics
- Study space finder
- A/B testing
- Research tools
- Performance optimization
- Scalability improvements

---

**🎉 TOPLAM YENİ ÖZELLİK SAYISI: 26 Ana Kategori, 200+ Alt Görev!**

---

## 📋 KALİTE KRİTERLERİ

### Code Quality Checklist
- [ ] **Type Hints:** Her fonksiyonda tip belirtme
- [ ] **Docstrings:** Her class/function için docstring
- [ ] **Comments:** Karmaşık logic için yorum
- [ ] **Error Handling:** Try-except blokları
- [ ] **Logging:** Kritik noktalarda log
- [ ] **Testing:** %80+ test coverage
- [ ] **Performance:** Profiling ve optimization
- [ ] **Security:** Input validation, SQL injection prevention

### UI/UX Checklist
- [ ] **Responsive:** Farklı ekran boyutlarında çalışır
- [ ] **Accessible:** Keyboard navigation
- [ ] **Intuitive:** Kullanımı kolay
- [ ] **Fast:** Hızlı yanıt süresi (<100ms)
- [ ] **Feedback:** Her aksiyonda kullanıcıya geri bildirim
- [ ] **Error Messages:** Anlaşılır hata mesajları
- [ ] **Help:** Tooltips ve help system

---

## 🚀 DEPLOYMENT CHECKLIST

### Pre-Release
- [ ] Tüm testler geçiyor
- [ ] Dokümantasyon tamamlandı
- [ ] Version number belirlendi
- [ ] Changelog hazırlandı
- [ ] Beta test yapıldı

### Release
- [ ] Executable build edildi
- [ ] Installer oluşturuldu
- [ ] GitHub release oluşturuldu
- [ ] README güncellemesi
- [ ] Website/Blog post

### Post-Release
- [ ] User feedback toplama
- [ ] Bug tracking
- [ ] Feature requests değerlendirme
- [ ] Performance monitoring

---

## 📝 NOTLAR

### Önemli Kararlar
1. **GUI Framework:** PyQt6 (daha profesyonel, cross-platform)
2. **Database:** SQLite (hafif, embedded)
3. **Testing:** pytest + pytest-qt
4. **Type Checking:** mypy
5. **Code Style:** black + flake8

### Riskler ve Çözümler
- **Risk:** PyQt6 learning curve
  - **Çözüm:** Dokümantasyon ve örnekler hazırla
- **Risk:** Performance sorunları
  - **Çözüm:** Multi-threading, caching, profiling
- **Risk:** Test coverage düşük
  - **Çözüm:** TDD approach, CI/CD

### Referanslar
- V1.1: `SchedularV1.1.py`
- yedek: `yedek/` klasörü
- V2: `SchedularV2/` klasörü

---

## 🎯 MİLESTONE'LAR

### Milestone 1: Foundation (Hafta 1 Sonu)
- [x] Proje yapısı
- [x] Core models
- [x] Excel loader
- [x] Basic tests

### Milestone 2: Brain (Hafta 2 Ortası)
- [ ] DFS scheduler
- [ ] Annealing optimizer
- [ ] Constraints system
- [ ] Multi-threading

### Milestone 3: Face (Hafta 2 Sonu)
- [ ] Main window
- [ ] All 4 tabs
- [ ] Basic widgets
- [ ] Theme support

### Milestone 4: Polish (Hafta 3 Ortası)
- [ ] Reporting system
- [ ] Error handling
- [ ] Full testing
- [ ] Documentation

### Milestone 5: Ship (Hafta 3 Sonu)
- [ ] Packaging
- [ ] Installer
- [ ] Release
- [ ] Deployment

---

## 🏆 BAŞARI KRİTERLERİ

### Teknik Kriterler
- ✅ %80+ test coverage
- ✅ <100ms UI response time
- ✅ <5MB memory footprint (idle)
- ✅ 1000+ courses işleyebilme
- ✅ 100+ schedules generate edebilme
- ✅ Type hints %100
- ✅ Zero mypy errors
- ✅ Zero flake8 errors

### Fonksiyonel Kriterler
- ✅ Excel dosyası import
- ✅ Türkçe/İngilizce data desteği
- ✅ Multi-constraint scheduling
- ✅ Conflict detection & resolution
- ✅ PDF/JPEG export
- ✅ Database persistence
- ✅ Dark/Light theme
- ✅ Search & filter

### Kullanıcı Deneyimi
- ✅ 5 dakikada öğrenilebilir
- ✅ Hata mesajları açık ve yardımcı
- ✅ Responsive UI
- ✅ Keyboard shortcuts
- ✅ Undo/Redo
- ✅ Help system

---

**Son Güncelleme:** 10 Kasım 2025  
**Versiyon:** 2.0 - 🚀 Algorithm Expansion Edition  
**Durum:** 🔴 Planning Phase

**Toplam Algoritma Sayısı:** 15+ 🎯  
**Yeni Özellik:** Kullanıcı algoritma seçimi + karşılaştırma

---

## 🎓 ALGORİTMA REHBERİ - Hızlı Başvuru

### 🎯 Hangi Algoritmayı Ne Zaman Kullanmalı?

#### Problem Büyüklüğüne Göre:

**Küçük Dataset (< 50 ders)**
- ✅ **BFS** - Garantili optimal sonuç
- ✅ **A*** - Hızlı ve optimal
- ✅ **IDDFS** - Bellek tasarrufu

**Orta Dataset (50-200 ders)**
- ✅ **A*** - En dengeli seçim
- ✅ **DFS** - Hızlı sonuç
- ✅ **Genetic Algorithm** - Kaliteli sonuçlar
- ⚠️ **Tabu Search** - İyi balance

**Büyük Dataset (200+ ders)**
- ✅ **Genetic Algorithm** - En iyi ölçeklenme
- ✅ **Simulated Annealing** - Güvenilir
- ✅ **Greedy** - Çok hızlı yaklaşım
- ⚠️ **Particle Swarm** - Alternatif
- ❌ **BFS** - Çok yavaş/bellek problemi

#### Constraint Kompleksitesine Göre:

**Basit Constraint'ler (Sadece zaman çakışması)**
- ✅ **Greedy Best-First**
- ✅ **DFS**
- ✅ **Hill Climbing**

**Orta Constraint'ler (Zaman + ECTS + Tercihler)**
- ✅ **A*** 
- ✅ **Genetic Algorithm**
- ✅ **Simulated Annealing**

**Karmaşık Constraint'ler (Multiple hard/soft constraints)**
- ✅ **Constraint Programming** (OR-Tools)
- ✅ **Hybrid GA+SA**
- ✅ **Tabu Search**

#### Hedef/Önceliğe Göre:

**Hız Öncelikli (Hızlı sonuç gerekiyor)**
1. **Greedy Best-First** - En hızlı
2. **Hill Climbing** - Çok hızlı
3. **DFS** (pruning ile) - Hızlı
4. **A*** (iyi heuristic ile) - Hızlı + kaliteli

**Kalite Öncelikli (En iyi sonuç istiyorum)**
1. **Hybrid GA+SA** - En kaliteli
2. **Genetic Algorithm** - Çok iyi
3. **A*** - Optimal garantili
4. **Constraint Programming** - Optimal + constraint handling

**Bellek Kısıtlı (RAM az)**
1. **IDDFS** - Minimum RAM
2. **Simulated Annealing** - O(1) space
3. **Hill Climbing** - O(1) space
4. **DFS** - Düşük bellek

**Optimal Garanti İstiyorum**
1. **A*** - Admissible heuristic ile
2. **BFS** - Garantili ama yavaş
3. **Dijkstra** - Garantili
4. **IDDFS** - Garantili + düşük bellek
5. **Constraint Programming** - Garantili + constraints

### 🧪 Algoritma Test Senaryoları

#### Senaryo 1: Hızlı Demo için
```
Dataset: 30 ders
Constraint: Orta
Önerilen: A* (h = conflicts + credits)
Beklenen Süre: 2-5 saniye
Kalite: 9/10
```

#### Senaryo 2: Gerçek Kullanım (Öğrenci)
```
Dataset: 80 ders
Constraint: Yüksek (tercihler dahil)
Önerilen: Genetic Algorithm
Popülasyon: 100
Jenerasyon: 50
Beklenen Süre: 20-40 saniye
Kalite: 10/10
```

#### Senaryo 3: Büyük Fakülte
```
Dataset: 500+ ders
Constraint: Çok karmaşık
Önerilen: Hybrid GA+SA veya Parallel Execution
Paralel: Evet (4 algoritma aynı anda)
Beklenen Süre: 2-5 dakika
Kalite: 10/10
```

#### Senaryo 4: Araştırma/Benchmark
```
Dataset: Değişken
Amaç: Tüm algoritmaları karşılaştır
Önerilen: Benchmark Mode
Algoritmalar: Hepsi (15+)
Beklenen Süre: 10-30 dakika
Çıktı: Karşılaştırma raporu
```

### 📚 Algoritma Implementasyon Önceliği

**Faz 1 (Temel - Hemen gerekli):**
1. DFS - Mevcut, iyileştir
2. A* - En önemli
3. Genetic Algorithm - Popüler
4. Simulated Annealing - Mevcut, iyileştir

**Faz 2 (Önemli - İkinci hafta):**
5. Greedy Best-First - Hızlı demo için
6. Tabu Search - Kalite için
7. Hill Climbing - Basit local search
8. BFS - Completeness için

**Faz 3 (İyi olurdu - Üçüncü hafta):**
9. IDDFS - Bellek efficiency
10. Dijkstra - Weighted constraints
11. Particle Swarm - Farklılık için
12. Ant Colony - Akademik ilgi

**Faz 4 (Bonus - Zaman varsa):**
13. Hybrid GA+SA - En kaliteli
14. Memetic Algorithm - Advanced
15. Constraint Programming - Profesyonel
16. Reinforcement Learning - Cutting edge

### � Her Algoritma İçin Kod Template

```python
# algorithms/example_scheduler.py

from typing import List, Dict, Set, Optional
from .base_scheduler import BaseScheduler, AlgorithmMetadata
from ..core.models import Course, Schedule

class ExampleScheduler(BaseScheduler):
    """
    Example scheduling algorithm.
    
    Time Complexity: O(?)
    Space Complexity: O(?)
    """
    
    def __init__(self, param1: int = 100, param2: float = 0.5):
        super().__init__()
        self.param1 = param1
        self.param2 = param2
    
    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Example Algorithm",
            description="Brief description",
            time_complexity="O(?)",
            space_complexity="O(?)",
            pros=["Fast", "Simple"],
            cons=["Not optimal"],
            best_use_case="Small to medium datasets"
        )
    
    def generate_schedules(
        self, 
        course_groups: Dict[str, CourseGroup],
        mandatory_codes: Set[str],
        **kwargs
    ) -> List[Schedule]:
        """Main scheduling logic"""
        # Implementation here
        pass
    
    def get_algorithm_params(self) -> Dict[str, Any]:
        """Return configurable parameters for GUI"""
        return {
            "param1": {
                "type": "int",
                "min": 1,
                "max": 1000,
                "default": 100,
                "description": "Parameter 1 description"
            },
            "param2": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.5,
                "description": "Parameter 2 description"
            }
        }
```

### 🎛️ GUI Algoritma Seçici Mockup

```
┌─────────────────────────────────────────────────┐
│ 🎯 Algorithm Selection                          │
├─────────────────────────────────────────────────┤
│                                                 │
│ Category: [📊 Complete Search ▼]                │
│                                                 │
│ ┌─────────────────────────────────────────────┐ │
│ │ ○ Depth-First Search (DFS)                  │ │
│ │ ● A* Search                    ⭐ Recommended│ │
│ │ ○ Breadth-First Search (BFS)                │ │
│ │ ○ IDDFS                                     │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Algorithm Info:                                 │
│ ┌─────────────────────────────────────────────┐ │
│ │ A* Search                                   │ │
│ │                                             │ │
│ │ An informed search algorithm that finds    │ │
│ │ optimal solutions efficiently using         │ │
│ │ heuristics.                                 │ │
│ │                                             │ │
│ │ ⏱️  Time: O(b^d) - Usually faster           │ │
│ │ 💾 Space: O(b^d)                            │ │
│ │                                             │ │
│ │ ✅ Pros: Fast, Optimal, Flexible            │ │
│ │ ❌ Cons: Memory intensive                   │ │
│ │                                             │ │
│ │ 🎯 Best for: Medium datasets (50-200)       │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Parameters:                                     │
│ ┌─────────────────────────────────────────────┐ │
│ │ Heuristic: [Conflict + Credit ▼]           │ │
│ │ Weight:    [═══════●═══] 0.7               │ │
│ │ Max Depth: [══════●════] 15                │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ [🤖 Auto-Select Best]  [📊 Compare All]        │
│                                                 │
│ ☑️ Enable parallel execution                    │
│ ☐ Benchmark mode                               │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

> 💡 **İpucu:** Her görev tamamlandıkça `[ ]` işaretini `[x]` olarak değiştir.  
> 🎯 **Hedef:** 3 hafta içinde production-ready PyQt6 uygulama + 15 algoritma!  
> 🚀 **Motto:** "One app, infinite algorithms, perfect schedules!"
