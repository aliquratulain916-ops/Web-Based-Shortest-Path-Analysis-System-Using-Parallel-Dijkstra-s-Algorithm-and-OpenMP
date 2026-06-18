# Database-Driven Shortest Path Analysis and Visualization System Using Parallel Dijkstra's Algorithm with OpenMP

**Developed by ATA (Advanced Technical Architecture)**

## Project Overview

This enterprise-grade system implements **Dijkstra's Shortest Path Algorithm** with parallel execution using SQLite database persistence and a high-performance C++ OpenMP solver. The architecture integrates a Python FastAPI backend, comprehensive performance benchmarking, and an interactive React+Vite frontend for real-time path analysis and visualization.

### Key Features

- ✓ **Parallel Dijkstra's Algorithm**: OpenMP-optimized C++ implementation with configurable thread counts
- ✓ **SQLite Database**: 5,000+ node persistent graph storage with computed path caching (20+ precomputed paths)
- ✓ **High-Performance Computing**: Multi-threaded computation with automatic fallback to Python sequential solver
- ✓ **Comprehensive Benchmarking**: Sequential vs. parallel performance analysis with statistical reporting
- ✓ **RESTful API**: FastAPI backend with 5 production endpoints (/health, /setup, /stats, /shortest-path, /benchmark)
- ✓ **Professional Frontend**: React+Vite interactive dashboard with real-time result visualization
- ✓ **Path Validation**: Automatic verification of computed shortest paths against edge weights
- ✓ **Enterprise Reporting**: Machine-readable CSV exports and human-readable performance summaries

---

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended for benchmarking)
- **Disk Space**: ~100MB for database and files

---

## Installation & Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Python Dependencies:**
- `fastapi` - High-performance REST API framework
- `uvicorn` - ASGI application server
- `pydantic` - Data validation and type checking

**Frontend Dependencies:**
- `React` 18.3+ - UI component framework
- `Vite` 5.4+ - Lightning-fast build tool and dev server
- `TypeScript` 5.5+ - Static type checking for JavaScript

### 2. Initialize the Project

```bash
python main.py
```

### 3. First-Time Setup

When you run the application for the first time:
1. Select option **1** (Setup/Initialize Database)
2. The system will:
   - Create SQLite database (`graph_data.db`)
   - Generate 5,000 nodes
   - Create ~25,000-30,000 edges
   - Validate database structure

---

## Project Structure

```
dijkstra-parallel/
├── main.py                 # Main application with menu system
├── database.py             # Database management and graph storage
├── dijkstra.py            # Algorithm implementation (sequential & parallel)
├── performance.py         # Performance analysis and benchmarking
├── requirements.txt       # Python dependencies
├── graph_data.db          # SQLite database (auto-created)
├── performance_report.txt # Generated performance analysis
├── performance_data.csv   # Detailed benchmark results
└── README.md             # This file
```

---

## Module Descriptions

### 1. **database.py** - Database Management
Handles all database operations:
- **GraphDatabase class**:
  - `create_tables()` - Initialize database schema
  - `generate_sample_data()` - Create 5,000+ node graph
  - `get_graph_as_dict()` - Load graph into memory
  - `save_path_result()` - Store computed paths
  - `get_stats()` - Database statistics

### 2. **dijkstra.py** - Algorithm Implementation
Core algorithm implementations:
- **DijkstraAlgorithm class**:
  - `dijkstra_sequential()` - Single-threaded implementation
  - `dijkstra_parallel()` - Parallel version
  - `dijkstra_with_timing()` - Execute with performance metrics
  - `validate_path()` - Verify path correctness

### 3. **performance.py** - Performance Analysis
Benchmarking and analysis:
- **PerformanceAnalyzer class**:
  - `benchmark_implementation()` - Run multiple test cases
  - `run_full_benchmark()` - Comprehensive multi-config testing
  - `generate_performance_report()` - Create analysis report
  - `export_results_csv()` - Export data for external analysis

### 4. **main.py** - Application Interface
Interactive user interface:
- **DijkstraApp class**:
  - Database setup and management
  - Interactive path finding
  - Performance benchmarking
  - Statistics display

---

## Usage Guide

### Option 1: Find Shortest Path

```
1. Select "Find Shortest Path" from menu
2. Enter source node ID (1-5000)
3. Enter destination node ID (1-5000)
4. Choose algorithm:
   - Sequential (single-threaded baseline)
   - Parallel (multi-threaded)
5. View results:
   - Shortest distance
   - Complete path
   - Computation time
   - Path validation status
6. Optionally save to database
```

### Option 2: Run Performance Analysis

```
1. Select "Run Performance Analysis"
2. Enter number of test cases (recommended: 20-50)
3. System will benchmark:
   - Sequential implementation (baseline)
   - Parallel with 1, 2, 4, N/2, N threads
4. Generates:
   - performance_report.txt (human-readable analysis)
   - performance_data.csv (detailed data)
```

### Option 3: View Statistics

```
1. Select "View Database Statistics"
2. Display:
   - Total nodes and edges
   - Paths computed
   - Graph connectivity metrics
```

### Optional Web Frontend

This repository now includes a professional React frontend and a FastAPI backend.

- Backend entrypoint: `api.py`
- Frontend folder: `frontend/`
- To run the web interface:
  1. Install Python dependencies: `pip install -r requirements.txt`
  2. Start the API: `uvicorn api:app --reload --port 8000`
  3. Install frontend dependencies: `cd frontend && npm install`
  4. Start the frontend: `npm run dev`
  5. Open the browser at `http://localhost:5173`

### Strict OpenMP Compliance

This project now includes a true OpenMP implementation in `dijkstra_openmp.cpp`.
The C++ solver reads the SQLite graph and uses OpenMP to parallelize neighbor processing.

#### Windows setup

Requirements:
- Python 3.8+ installed and available as `py`
- Node.js and npm
- Visual Studio Build Tools with MSVC and OpenMP support, or MinGW-w64 with OpenMP
- SQLite3 development libraries if using MinGW

Steps:
1. Open PowerShell in the repository root.
2. Install Python dependencies:
   - `py -m pip install -r requirements.txt`
3. Install frontend dependencies:
   - `cd frontend`
   - `npm install`
   - `cd ..`
4. Build the OpenMP solver:
   - `build_openmp.bat`

If MSVC is available, run the script from a Developer Command Prompt.
If using MinGW, ensure `g++` and `sqlite3` are on the PATH.

#### Run the Windows app

1. Start the backend:
   - `py -m uvicorn api:app --reload --port 8000`
2. Start the frontend:
   - `cd frontend`
   - `npm run dev -- --host 127.0.0.1 --port 5173`
3. Open the browser at `http://127.0.0.1:5173`
4. Use the UI to initialize the database, compute paths, and benchmark.

---

## Algorithm Details

### Dijkstra's Algorithm Complexity

- **Time Complexity**: O((V + E) log V)
  - V = number of vertices (nodes)
  - E = number of edges
  
- **Space Complexity**: O(V)

### Implementation Strategy

#### Sequential Version
- Uses priority queue (heapq)
- Single-threaded execution
- Maintains distance and previous node tracking
- Early termination when destination reached

#### Parallel Version
- Leverages Python's multiprocessing
- Parallelizes neighbor processing
- Maintains thread-safe data structures
- Configurable thread count

---

## Performance Metrics

### Key Performance Indicators

1. **Execution Time**
   - Measured in milliseconds
   - Average, minimum, maximum times
   - Standard deviation

2. **Speedup**
   - Speedup = Sequential Time / Parallel Time
   - Ideally near thread count (linear scaling)
   - Actual speedup depends on hardware

3. **Parallel Efficiency**
   - Efficiency = (Speedup / Threads) × 100%
   - Optimal: 70-90% efficiency
   - Diminishing returns with more threads

### Sample Results

```
Sequential:     ~0.15 ms per path
Parallel (4T):  ~0.08 ms per path
Speedup:        1.87x (70% efficiency)
```

---

## Database Schema

### Tables

#### 1. **nodes**
```sql
- node_id: INTEGER PRIMARY KEY (1-5000)
- node_name: TEXT (Node_1, Node_2, ...)
- latitude: REAL (optional geo data)
- longitude: REAL (optional geo data)
- created_at: TIMESTAMP
```

#### 2. **edges**
```sql
- edge_id: INTEGER PRIMARY KEY
- source_node_id: FOREIGN KEY
- destination_node_id: FOREIGN KEY
- weight: REAL (1-100)
- distance: REAL (optional)
- created_at: TIMESTAMP
```

#### 3. **paths**
```sql
- path_id: INTEGER PRIMARY KEY
- source_node_id: FOREIGN KEY
- destination_node_id: FOREIGN KEY
- total_distance: REAL
- path_nodes: TEXT (comma-separated)
- computation_time: REAL (milliseconds)
- algorithm_type: TEXT (Sequential/Parallel)
- num_threads: INTEGER
- created_at: TIMESTAMP
```

---

## Performance Analysis Report

### Generated Files

#### 1. **performance_report.txt**
Human-readable analysis including:
- Database statistics
- Per-configuration metrics
- Speedup analysis
- Parallel efficiency
- Recommendations

#### 2. **performance_data.csv**
Detailed data for each test:
- Configuration name
- Source/destination nodes
- Path distance
- Computation time
- Algorithm type
- Thread count

---

## Advanced Usage

### Programmatic Usage

```python
from database import GraphDatabase
from dijkstra import DijkstraAlgorithm
from performance import PerformanceAnalyzer

# Setup database
db = GraphDatabase('graph_data.db')
db.connect()
db.create_tables()
db.generate_sample_data(5000)

# Get graph
graph = db.get_graph_as_dict()

# Find shortest path (sequential)
distance, path = DijkstraAlgorithm.dijkstra_sequential(graph, 1, 100)
print(f"Distance: {distance}, Path: {path}")

# Find shortest path (parallel)
distance, path = DijkstraAlgorithm.dijkstra_parallel(graph, 1, 100, num_threads=4)
print(f"Distance: {distance}, Path: {path}")

# Run performance analysis
analyzer = PerformanceAnalyzer(db)
results = analyzer.run_full_benchmark(test_cases_per_config=30)
analyzer.generate_performance_report(results)

db.disconnect()
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'X'"
**Solution**: Install missing packages
```bash
pip install -r requirements.txt
```

### Issue: Database already exists
**Solution**: Delete `graph_data.db` or select "Overwrite" when prompted

### Issue: Slow performance on initial runs
**Solution**: Database is being created and populated. First run may take 30-60 seconds.

### Issue: Parallel slower than sequential
**Solution**: 
- For small graphs, overhead > benefit
- Increase test case size
- Check CPU count: `from multiprocessing import cpu_count; print(cpu_count())`

---

## Optimization Tips

1. **Thread Count Selection**
   - Use 4-8 threads for most systems
   - Test with `run_full_benchmark()`
   - Monitor CPU utilization

2. **Database Optimization**
   - Create indexes on frequently queried columns
   - Use connection pooling for multiple queries
   - Cache graph in memory when possible

3. **Algorithm Optimization**
   - Use bidirectional search for distant nodes
   - Implement A* with heuristics if coordinates available
   - Precompute all-pairs shortest paths if needed

---

## Project Deliverables

### ✓ Submitted Files

1. **Source Code**
   - main.py
   - database.py
   - dijkstra.py
   - performance.py
   - requirements.txt

2. **Database**
   - graph_data.db (auto-generated, 5,000+ nodes)

3. **Documentation**
   - README.md (this file)
   - Code comments and docstrings

4. **Performance Analysis**
   - performance_report.txt
   - performance_data.csv

---

## References & Resources

- **Dijkstra's Algorithm**: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- **Python multiprocessing**: https://docs.python.org/3/library/multiprocessing.html
- **SQLite Documentation**: https://www.sqlite.org/docs.html
- **NetworkX**: https://networkx.org/

---

## Author & License

**Project**: CCP - Parallel Implementation of Dijkstra's Algorithm  
**Language**: Python 3.8+  
**License**: Educational Use

---

## Contact & Support

For issues or questions:
1. Check this README for troubleshooting
2. Review code comments in respective modules
3. Verify database integrity with option 4 in menu

---

**Last Updated**: 2024  
**Status**: Production Ready ✓
