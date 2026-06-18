# QUICK START GUIDE

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed numpy, pandas, networkx, matplotlib
```

### Step 2: Run Application
```bash
python main.py
```

### Step 3: Initialize Database
When prompted, select option `1` to set up the database.
- Creates SQLite database with 5,000 nodes
- Generates ~25,000 edges
- Takes 30-60 seconds first time

Output:
```
Generated 5000 nodes
Generated 25487 edges
Database setup complete!
```

### Step 4: Find Shortest Path
Select option `2` and try:
- Source Node: 1
- Destination Node: 2500
- Algorithm: Sequential (1st time)

You should see:
```
Shortest Distance: 45.67
Path Length (hops): 7
Path: 1 -> 145 -> 892 -> ...
Computation Time: 0.1234 ms
```

### Step 5: Run Performance Test
Select option `3` for benchmarking:
- Enter 10 test cases
- System will test both sequential and parallel versions
- Generates performance_report.txt

---

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

# Reset database
rm graph_data.db

# View performance report
cat performance_report.txt

# View performance data
cat performance_data.csv

# Test individual modules
python database.py      # Test database setup
python dijkstra.py      # Test algorithm
python performance.py   # Test benchmarking
```

---

## Testing Checklist

- [ ] Python installed (3.8+)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Application runs (`python main.py`)
- [ ] Database initialized (Option 1)
- [ ] Shortest path found (Option 2)
- [ ] Performance analysis runs (Option 3)
- [ ] Performance report generated

---

## Example Walkthrough

```
$ python main.py

============================================================
DIJKSTRA'S ALGORITHM WITH PARALLEL PROCESSING
============================================================

============================================================
DIJKSTRA'S SHORTEST PATH - PARALLEL IMPLEMENTATION
============================================================

1. Setup/Initialize Database
2. Find Shortest Path
3. Run Performance Analysis
4. View Database Statistics
5. Exit

------------------------------------------------------------
Select option (1-5): 1

============================================================
DATABASE SETUP
============================================================

Generating 5000 nodes and edges...
Generated 5000 nodes
Generated 27534 edges
Database setup complete!

[Menu repeats]

Select option (1-5): 2

============================================================
FIND SHORTEST PATH
============================================================

Enter source node ID: 100
Enter destination node ID: 4500
Algorithm Options:
1. Sequential (Single-threaded)
2. Parallel (Multi-threaded)
Select algorithm (1-2): 1

Computing shortest path...

------------------------------------------------------------
RESULTS:
------------------------------------------------------------
Source Node: 100
Destination Node: 4500
Shortest Distance: 67.34
Path Length (hops): 12
Path: 100 -> 457 -> 1289 -> ...
Computation Time: 0.3456 ms
Algorithm: Sequential (1 thread(s))
Path Validation: VALID ✓
Calculated Distance: 67.34

Save result to database? (y/n): y
Result saved to database!
```

---

## Performance Expectations

### Sequential Algorithm
- Small paths (< 5 hops): 0.05-0.1 ms
- Medium paths (5-10 hops): 0.1-0.3 ms
- Long paths (> 10 hops): 0.3-1.0 ms

### Parallel Algorithm (4 threads)
- Should see 1.5-2.0x speedup
- Efficiency: 40-50% (acceptable for Python)
- Better on larger graphs/longer paths

### Database Operations
- Initial setup: 30-60 seconds
- Subsequent loads: < 1 second
- Path lookups: < 10 ms

---

## File Locations

After first run, you'll have:

```
Your Project Folder/
├── main.py                    # Main application
├── database.py               # Database module
├── dijkstra.py              # Algorithm module
├── performance.py           # Performance module
├── requirements.txt         # Dependencies
├── README.md               # Full documentation
├── graph_data.db           # Generated database
├── performance_report.txt  # Generated report
└── performance_data.csv    # Generated data
```

---

## Helpful Tips

1. **First time is slowest**: Database generation takes time initially
2. **Use sequential first**: Verify it works before testing parallel
3. **Small test cases**: Start with 5-10 test cases before 50+
4. **Check system**: More CPU cores = better parallel speedup
5. **Save results**: Database persists results for later analysis

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError" | Run `pip install -r requirements.txt` |
| Database takes forever | First run is slow. Give it 2 minutes. |
| Parallel is slower | Use larger test cases, more threads |
| Can't find nodes | Nodes are 1-5000. Use values in range. |
| Database corrupted | Delete `graph_data.db` and reinitialize |

---

## Next Steps

1. ✓ Run the application
2. ✓ Verify shortest path finding works
3. ✓ Run performance analysis
4. ✓ Review performance_report.txt
5. ✓ Experiment with different thread counts
6. ✓ Generate final documentation

---

Need more help? Check README.md for detailed documentation.
