# Technical Architecture & API Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│                    (main.py)                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Database │  │ Path     │  │ Perf     │  │ Stats   │ │
│  │ Setup    │  │ Finding  │  │ Analysis │  │ Display │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
└───────┼─────────────┼─────────────┼─────────────┼───────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼──────────────┐  ┌────────▼──────────────┐
│   DATABASE LAYER     │  │  ALGORITHM LAYER     │
│   (database.py)      │  │  (dijkstra.py)       │
│                      │  │                      │
│  • Node management   │  │  • Sequential impl   │
│  • Edge management   │  │  • Parallel impl     │
│  • Path storage      │  │  • Path validation   │
│  • Graph retrieval   │  │  • Timing & metrics  │
└───────┬──────────────┘  └────────┬──────────────┘
        │                          │
        └──────────────┬───────────┘
                       │
                ┌──────▼────────┐
                │ PERFORMANCE   │
                │ ANALYSIS      │
                │ (performance  │
                │ .py)          │
                │               │
                │ • Benchmark   │
                │ • Statistics  │
                │ • Report gen  │
                │ • CSV export  │
                └───────────────┘
                       │
                ┌──────▼────────┐
                │  SQLite DB    │
                │ graph_data.db │
                │               │
                │  Nodes table  │
                │  Edges table  │
                │  Paths table  │
                └───────────────┘
```

---

## Module APIs

### 1. GraphDatabase (database.py)

#### Class: `GraphDatabase`

**Constructor:**
```python
db = GraphDatabase(db_path='graph_data.db')
```

**Methods:**

##### `connect()`
Connect to SQLite database
```python
db.connect()
# Raises: sqlite3.Error if connection fails
```

##### `disconnect()`
Close database connection
```python
db.disconnect()
```

##### `create_tables()`
Create database schema (3 tables: nodes, edges, paths)
```python
db.create_tables()
# Creates:
#   - nodes (node_id, node_name, latitude, longitude, created_at)
#   - edges (edge_id, source_node_id, destination_node_id, weight, ...)
#   - paths (path_id, source, destination, distance, path_nodes, ...)
```

##### `generate_sample_data(num_nodes=5000)`
Generate graph with specified number of nodes
```python
db.generate_sample_data(5000)
# Creates:
#   - 5000 nodes (ID: 1-5000)
#   - ~20k-30k edges with random weights (1-100)
```

##### `get_graph_as_dict()`
Returns: `Dict[int, List[Tuple[int, float]]]`
```python
graph = db.get_graph_as_dict()
# Returns adjacency list:
# {
#   1: [(2, 4.5), (3, 2.1)],
#   2: [(1, 4.5), (4, 5.3)],
#   ...
# }
```

##### `get_all_nodes()`
Returns: `List[int]`
```python
nodes = db.get_all_nodes()
# Returns [1, 2, 3, ..., 5000]
```

##### `save_path_result(source, destination, total_distance, path_nodes, computation_time, algorithm_type, num_threads)`
Store computed path in database
```python
db.save_path_result(
    source=1,
    destination=100,
    total_distance=45.67,
    path_nodes=[1, 12, 45, 100],
    computation_time=0.001234,
    algorithm_type='Sequential',
    num_threads=1
)
```

##### `get_stats()`
Returns: `Dict[str, int]`
```python
stats = db.get_stats()
# Returns {
#   'nodes': 5000,
#   'edges': 27534,
#   'paths_computed': 15
# }
```

##### `clear_all()`
Delete all data from tables
```python
db.clear_all()  # Destructive operation
```

---

### 2. DijkstraAlgorithm (dijkstra.py)

#### Class: `DijkstraAlgorithm` (Static methods only)

##### `dijkstra_sequential(graph, source, destination)`
Returns: `Tuple[float, List[int]]`
```python
distance, path = DijkstraAlgorithm.dijkstra_sequential(graph, 1, 100)
# distance: float - shortest distance
# path: List[int] - node sequence [1, 12, 45, ..., 100]
```

**Time Complexity**: O((V + E) log V)
**Space Complexity**: O(V)

##### `dijkstra_parallel(graph, source, destination, num_threads=None)`
Returns: `Tuple[float, List[int]]`
```python
distance, path = DijkstraAlgorithm.dijkstra_parallel(
    graph, 1, 100, num_threads=4
)
# Same returns as sequential
# num_threads: int or None (uses cpu_count() if None)
```

**Note**: In Python, true parallelism limited by GIL. Efficiency depends on graph structure and hardware.

##### `dijkstra_with_timing(graph, source, destination, use_parallel=False, num_threads=None)`
Returns: `Dict`
```python
result = DijkstraAlgorithm.dijkstra_with_timing(
    graph, 1, 100, use_parallel=True, num_threads=4
)
# Returns:
# {
#   'source': 1,
#   'destination': 100,
#   'distance': 45.67,
#   'path': [1, 12, 45, ..., 100],
#   'path_length': 4,
#   'computation_time': 0.001234,  # in seconds
#   'algorithm': 'Parallel',
#   'num_threads': 4
# }
```

##### `validate_path(graph, path)`
Returns: `Tuple[bool, float]`
```python
is_valid, calc_distance = DijkstraAlgorithm.validate_path(graph, path)
# is_valid: bool - True if path exists in graph
# calc_distance: float - calculated distance if valid, inf if invalid
```

---

### 3. PerformanceAnalyzer (performance.py)

#### Class: `PerformanceAnalyzer`

**Constructor:**
```python
analyzer = PerformanceAnalyzer(db)  # db is GraphDatabase instance
```

##### `benchmark_implementation(graph, test_cases=10, use_parallel=False, num_threads=None)`
Returns: `List[Dict]`
```python
results = analyzer.benchmark_implementation(
    graph,
    test_cases=20,
    use_parallel=True,
    num_threads=4
)
# Returns list of result dicts from dijkstra_with_timing()
```

**Output:**
```
Benchmarking Parallel Dijkstra's Algorithm
Number of threads: 4
=====================================================
Test 1: Source=145, Dest=3456, Distance=67.34, Time=0.1234ms
Test 2: Source=2, Dest=4999, Distance=45.67, Time=0.0987ms
...
```

##### `run_full_benchmark(num_threads_list=None, test_cases_per_config=20)`
Returns: `Dict`
```python
full_results = analyzer.run_full_benchmark(
    num_threads_list=[1, 2, 4, 8],
    test_cases_per_config=30
)
# Returns comprehensive benchmark dict with:
# {
#   'timestamp': '2024-01-01T12:00:00',
#   'database_stats': {...},
#   'configurations': {
#       'sequential': {...},
#       'parallel_1t': {...},
#       'parallel_2t': {...},
#       ...
#   }
# }
```

##### `generate_performance_report(benchmark_results, output_file='performance_report.txt')`
Generates human-readable report
```python
analyzer.generate_performance_report(full_results)
# Outputs:
#   - Console output
#   - File: performance_report.txt
#
# Contains:
#   - Database statistics
#   - Per-configuration metrics
#   - Speedup analysis
#   - Parallel efficiency
#   - Recommendations
```

##### `export_results_csv(benchmark_results, output_file='performance_data.csv')`
Export detailed data to CSV
```python
analyzer.export_results_csv(full_results)
# Creates: performance_data.csv
# Columns: Configuration, Source, Destination, Distance, 
#          Path_Length, Computation_Time_ms, Algorithm, Num_Threads
```

---

### 4. DijkstraApp (main.py)

#### Class: `DijkstraApp`

**Constructor:**
```python
app = DijkstraApp()
```

**Methods:**

##### `setup_database()`
Initialize and populate database
```python
app.setup_database()
# Interactive menu if data exists
# Generates 5000 nodes and edges
```

##### `load_graph()`
Load graph from database into memory
```python
app.load_graph()
# Loads graph_dict and all_nodes
# Takes ~1 second
```

##### `find_shortest_path()`
Interactive shortest path computation
```python
app.find_shortest_path()
# Prompts for:
#   - Source node
#   - Destination node
#   - Algorithm choice (sequential/parallel)
#   - Thread count (if parallel)
# Displays: distance, path, time, validation
# Option to save to database
```

##### `run_performance_analysis()`
Run benchmarking suite
```python
app.run_performance_analysis()
# Prompts for number of test cases
# Runs full benchmark
# Generates report and CSV
```

##### `view_database_stats()`
Display database statistics
```python
app.view_database_stats()
# Shows: nodes, edges, paths computed
# Graph connectivity metrics
```

##### `run()`
Main application loop
```python
app.run()
# Interactive menu system
# Runs until user selects exit
```

---

## Data Flow Diagram

### Finding Shortest Path

```
User Input
    ↓
Validate Nodes
    ↓
Load Graph from DB
    ↓
Run Dijkstra (Sequential or Parallel)
    ↓
Validate Path
    ↓
Display Results
    ↓
Option to Save
    ↓
Store in Database
```

### Performance Analysis

```
Get Thread Configurations
    ↓
Load Graph from DB
    ↓
For Each Configuration:
    ├─ Generate Random Test Cases
    ├─ Run Multiple Dijkstra Calls
    ├─ Collect Timing Data
    └─ Calculate Statistics
    ↓
Compare Configurations
    ↓
Calculate Speedup & Efficiency
    ↓
Generate Report
    ↓
Export CSV Data
```

---

## Database Schema Details

### Nodes Table
```sql
CREATE TABLE nodes (
    node_id INTEGER PRIMARY KEY,      -- 1 to 5000
    node_name TEXT NOT NULL UNIQUE,   -- "Node_1", "Node_2", etc.
    latitude REAL,                     -- Optional geographic data
    longitude REAL,                    -- Optional geographic data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Edges Table
```sql
CREATE TABLE edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_node_id INTEGER NOT NULL,
    destination_node_id INTEGER NOT NULL,
    weight REAL NOT NULL,             -- 1.0 to 100.0
    distance REAL,                     -- Optional
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_node_id) REFERENCES nodes(node_id),
    FOREIGN KEY(destination_node_id) REFERENCES nodes(node_id),
    UNIQUE(source_node_id, destination_node_id)
)
```

### Paths Table
```sql
CREATE TABLE paths (
    path_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_node_id INTEGER NOT NULL,
    destination_node_id INTEGER NOT NULL,
    total_distance REAL,
    path_nodes TEXT,                  -- "1,12,45,100"
    computation_time REAL,            -- seconds
    algorithm_type TEXT,              -- "Sequential" or "Parallel"
    num_threads INTEGER,              -- 1 or more
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_node_id) REFERENCES nodes(node_id),
    FOREIGN KEY(destination_node_id) REFERENCES nodes(node_id)
)
```

---

## Performance Metrics

### Measured Metrics
- **Execution Time**: CPU time in milliseconds
- **Path Distance**: Sum of edge weights
- **Path Length**: Number of hops
- **Speedup**: Sequential Time / Parallel Time
- **Efficiency**: (Speedup / Thread Count) × 100%

### Expected Performance

**Sequential (Baseline)**
- Small paths (< 5 hops): 0.05-0.10 ms
- Medium paths (5-10 hops): 0.10-0.30 ms
- Large paths (> 10 hops): 0.30-1.00 ms

**Parallel (4 threads)**
- Expected speedup: 1.5-2.0x
- Efficiency: 40-50%
- Better with larger graphs

---

## Error Handling

### Database Errors
```python
try:
    db.connect()
except sqlite3.Error as e:
    print(f"Database error: {e}")
```

### Algorithm Errors
```python
distance, path = DijkstraAlgorithm.dijkstra_sequential(graph, source, dest)
if distance == float('inf'):
    print("No path found")
else:
    print(f"Path found: {path}")
```

### Input Validation
```python
if source not in graph or destination not in graph:
    raise ValueError(f"Node not in graph")
```

---

## Performance Optimization Tips

### Algorithm Level
1. **Early Termination**: Stop when destination reached
2. **Priority Queue**: Use heapq for efficiency
3. **Visited Tracking**: Avoid revisiting nodes

### Database Level
1. **Indexing**: Add indexes on frequently queried columns
2. **Caching**: Load graph once, reuse in memory
3. **Batch Operations**: Group multiple inserts

### System Level
1. **Thread Count**: Optimize for hardware
2. **Memory Usage**: Monitor RAM during benchmarks
3. **CPU Affinity**: Pin threads to cores if available

---

## Testing

### Unit Tests Examples

```python
# Test algorithm
def test_dijkstra():
    graph = {1: [(2, 4)], 2: []}
    dist, path = DijkstraAlgorithm.dijkstra_sequential(graph, 1, 2)
    assert dist == 4
    assert path == [1, 2]

# Test database
def test_database():
    db = GraphDatabase(':memory:')  # In-memory DB
    db.connect()
    db.create_tables()
    assert db.get_stats()['nodes'] == 0

# Test performance
def test_performance():
    analyzer = PerformanceAnalyzer(db)
    results = analyzer.benchmark_implementation(graph, 5, False)
    assert len(results) == 5
```

---

## Conclusion

This architecture provides:
- ✓ Clear separation of concerns
- ✓ Reusable modules
- ✓ Comprehensive API
- ✓ Performance measurement
- ✓ User-friendly interface
- ✓ Extensible design

---

**Last Updated**: 2024  
**Version**: 1.0
