"""
Main Application - Dijkstra's Shortest Path with Parallelization
Interactive system for finding shortest paths in graph databases
"""

import json
import subprocess
from pathlib import Path
import sys
from database import GraphDatabase
from dijkstra import DijkstraAlgorithm
from performance import PerformanceAnalyzer
from multiprocessing import cpu_count

class DijkstraApp:
    
    def __init__(self):
        """Initialize application"""
        self.db = GraphDatabase('graph_data.db')
        self.graph = None
        self.all_nodes = None

    def run_openmp_solver(self, source: int, destination: int, num_threads: int) -> dict:
        exe_name = "dijkstra_openmp.exe" if Path("dijkstra_openmp.exe").exists() else "dijkstra_openmp"
        solver_path = Path(exe_name)
        if not solver_path.exists():
            raise FileNotFoundError("OpenMP solver binary not found. Build dijkstra_openmp first.")

        command = [str(solver_path), "graph_data.db", str(source), str(destination), str(num_threads)]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0:
            raise RuntimeError(f"OpenMP solver failed: {completed.stderr.strip()}")

        return json.loads(completed.stdout)

    def setup_database(self):
        """Initialize and populate database"""
        print("\n" + "="*60)
        print("DATABASE SETUP")
        print("="*60)
        
        self.db.connect()
        self.db.create_tables()
        
        # Check if data already exists
        stats = self.db.get_stats()
        if stats['nodes'] > 0:
            print(f"\nDatabase already contains data:")
            print(f"  Nodes: {stats['nodes']}")
            print(f"  Edges: {stats['edges']}")
            response = input("\nOverwrite existing data? (y/n): ").lower()
            if response == 'y':
                self.db.clear_all()
                self.db.generate_sample_data(5000)
        else:
            print("\nGenerating sample graph data...")
            self.db.generate_sample_data(5000)
        
        # Load graph
        self.load_graph()
        print("\nDatabase setup complete!")
    
    def load_graph(self):
        """Load graph from database"""
        print("Loading graph from database...")
        self.graph = self.db.get_graph_as_dict()
        self.all_nodes = self.db.get_all_nodes()
        print(f"Graph loaded: {len(self.all_nodes)} nodes, {sum(len(v) for v in self.graph.values())} edges")
    
    def find_shortest_path(self):
        """Interactive shortest path finder"""
        print("\n" + "="*60)
        print("FIND SHORTEST PATH")
        print("="*60)
        
        try:
            source = int(input("\nEnter source node ID: "))
            destination = int(input("Enter destination node ID: "))
            
            if source not in self.all_nodes:
                print(f"Error: Node {source} not found")
                return
            if destination not in self.all_nodes:
                print(f"Error: Node {destination} not found")
                return
            
            print("\nAlgorithm Options:")
            print("1. Sequential (Single-threaded)")
            print("2. Parallel (Multi-threaded)")
            algo_choice = input("Select algorithm (1-2): ").strip()
            
            use_parallel = algo_choice == '2'
            num_threads = 1
            
            if use_parallel:
                max_threads = cpu_count()
                print(f"\nAvailable CPU cores: {max_threads}")
                try:
                    num_threads = int(input(f"Enter number of threads (1-{max_threads}): "))
                    num_threads = min(max(num_threads, 1), max_threads)
                except:
                    num_threads = max_threads
            
            # Run algorithm
            print("\nComputing shortest path...")
            if use_parallel:
                try:
                    solver_result = self.run_openmp_solver(source, destination, num_threads)
                    result = {
                        'source': solver_result['source'],
                        'destination': solver_result['destination'],
                        'distance': solver_result['distance'],
                        'path': solver_result['path'],
                        'path_length': solver_result['path_length'],
                        'computation_time': solver_result['computation_time_ms'] / 1000.0,
                        'algorithm': solver_result['algorithm'],
                        'num_threads': solver_result['num_threads'],
                    }
                except FileNotFoundError as err:
                    print(f"\n{err}\nFalling back to Python multiprocessing parallel implementation.")
                    result = DijkstraAlgorithm.dijkstra_with_timing(
                        self.graph, source, destination, use_parallel=True, num_threads=num_threads
                    )
                except RuntimeError as err:
                    print(f"\nOpenMP solver error: {err}\nFalling back to Python multiprocessing parallel implementation.")
                    result = DijkstraAlgorithm.dijkstra_with_timing(
                        self.graph, source, destination, use_parallel=True, num_threads=num_threads
                    )
            else:
                result = DijkstraAlgorithm.dijkstra_with_timing(
                    self.graph, source, destination, use_parallel=False, num_threads=num_threads
                )
            
            # Display results
            print("\n" + "-"*60)
            print("RESULTS:")
            print("-"*60)
            print(f"Source Node: {source}")
            print(f"Destination Node: {destination}")
            print(f"Shortest Distance: {result['distance']:.2f}")
            print(f"Path Length (hops): {result['path_length']}")
            print(f"Path: {' -> '.join(map(str, result['path']))}")
            print(f"Computation Time: {result['computation_time']*1000:.4f} ms")
            print(f"Algorithm: {result['algorithm']} ({result['num_threads']} thread(s))")
            
            # Validate path
            valid, calc_distance = DijkstraAlgorithm.validate_path(self.graph, result['path'])
            if valid:
                print(f"Path Validation: VALID ✓")
                print(f"Calculated Distance: {calc_distance:.2f}")
            else:
                print(f"Path Validation: INVALID ✗")
            
            # Save to database
            save_choice = input("\nSave result to database? (y/n): ").lower()
            if save_choice == 'y':
                self.db.save_path_result(
                    source, destination, result['distance'], result['path'],
                    result['computation_time'], result['algorithm'], result['num_threads']
                )
                print("Result saved to database!")
            
        except ValueError:
            print("Error: Please enter valid node IDs")
        except Exception as e:
            print(f"Error: {e}")
    
    def run_performance_analysis(self):
        """Run performance benchmarks"""
        print("\n" + "="*60)
        print("PERFORMANCE ANALYSIS")
        print("="*60)
        
        print("\nConfiguring benchmark...")
        
        try:
            test_cases = int(input("Enter number of test cases per configuration (default 20): ") or "20")
            
            analyzer = PerformanceAnalyzer(self.db)
            
            print("\nStarting comprehensive benchmark...")
            print("This may take a few minutes...")
            
            # Run benchmark
            results = analyzer.run_full_benchmark(test_cases_per_config=test_cases)
            
            # Generate report
            print("\nGenerating performance report...")
            analyzer.generate_performance_report(results)
            
            # Export CSV
            analyzer.export_results_csv(results)
            
            print("\n✓ Performance analysis complete!")
            
        except ValueError:
            print("Error: Please enter valid input")
        except Exception as e:
            print(f"Error during benchmark: {e}")
    
    def view_database_stats(self):
        """Display database statistics"""
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)
        
        stats = self.db.get_stats()
        print(f"\nTotal Nodes: {stats['nodes']}")
        print(f"Total Edges: {stats['edges']}")
        print(f"Total Paths Computed: {stats['paths_computed']}")
        
        if stats['nodes'] > 0:
            avg_edges_per_node = stats['edges'] / stats['nodes']
            print(f"Average Edges per Node: {avg_edges_per_node:.2f}")
        
        print("\nGraph loaded in memory: " + ("Yes" if self.graph else "No"))
        if self.graph:
            print(f"Loaded nodes count: {len(self.all_nodes)}")
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("DIJKSTRA'S SHORTEST PATH - PARALLEL IMPLEMENTATION")
        print("="*60)
        print("\n1. Setup/Initialize Database")
        print("2. Find Shortest Path")
        print("3. Run Performance Analysis")
        print("4. View Database Statistics")
        print("5. Exit")
        print("\n" + "-"*60)
    
    def run(self):
        """Main application loop"""
        print("\n" + "="*60)
        print("DIJKSTRA'S ALGORITHM WITH PARALLEL PROCESSING")
        print("Graph Database Implementation")
        print("="*60)
        
        while True:
            self.display_menu()
            choice = input("Select option (1-5): ").strip()
            
            if choice == '1':
                self.setup_database()
            elif choice == '2':
                if not self.graph:
                    self.load_graph()
                self.find_shortest_path()
            elif choice == '3':
                if not self.graph:
                    self.load_graph()
                self.run_performance_analysis()
            elif choice == '4':
                self.view_database_stats()
            elif choice == '5':
                print("\nClosing application...")
                if self.db.conn:
                    self.db.disconnect()
                print("Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")

if __name__ == "__main__":
    app = DijkstraApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
        if app.db.conn:
            app.db.disconnect()
    except Exception as e:
        print(f"\nFatal error: {e}")
        if app.db.conn:
            app.db.disconnect()
