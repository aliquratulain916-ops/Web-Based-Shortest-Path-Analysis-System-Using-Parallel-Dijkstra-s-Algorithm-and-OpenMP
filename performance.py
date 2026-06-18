"""
Performance Analysis Module
Benchmarks Dijkstra's algorithm implementations and generates performance reports
"""

import time
import random
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List
import csv
from datetime import datetime
from database import GraphDatabase
from dijkstra import DijkstraAlgorithm
from multiprocessing import cpu_count

class PerformanceAnalyzer:
    
    def __init__(self, db: GraphDatabase):
        """Initialize performance analyzer"""
        self.db = db
        self.results = []

    def _openmp_solver_path(self):
        exe_name = "dijkstra_openmp.exe" if Path("dijkstra_openmp.exe").exists() else "dijkstra_openmp"
        solver_path = Path(exe_name)
        return solver_path if solver_path.exists() else None

    def _run_openmp_solver(self, source: int, destination: int, num_threads: int) -> dict:
        solver_path = self._openmp_solver_path()
        if solver_path is None:
            raise FileNotFoundError("OpenMP solver binary not found.")

        command = [str(solver_path), "graph_data.db", str(source), str(destination), str(num_threads)]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0:
            raise RuntimeError(f"OpenMP solver failed: {completed.stderr.strip()}")
        out = completed.stdout.strip()
        # Attempt to extract JSON object from possibly noisy stdout
        try:
            # find first { and last }
            start = out.find('{')
            end = out.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_text = out[start:end+1]
            else:
                json_text = out

            # Replace non-JSON floats like inf, -inf, nan with null so json.loads succeeds
            json_text = re.sub(r'(?<=:\s)(-?inf|nan)(?=[,\}])', 'null', json_text, flags=re.IGNORECASE)

            parsed = json.loads(json_text)

            # Normalize distance field: if null, convert to Python inf
            if 'distance' in parsed and parsed['distance'] is None:
                parsed['distance'] = float('inf')

            return parsed
        except Exception as e:
            raise RuntimeError(f"Failed to parse OpenMP solver JSON output: {e}\nStdout:\n{out}\nStderr:\n{completed.stderr}")

    def benchmark_implementation(self, graph: Dict, test_cases: int = 10,
                                use_parallel: bool = False,
                                num_threads: int = None) -> List[Dict]:
        """
        Benchmark algorithm implementation on multiple test cases
        
        Args:
            graph: Graph as adjacency list
            test_cases: Number of test cases to run
            use_parallel: Whether to benchmark parallel version
            num_threads: Number of threads (if parallel)
            
        Returns:
            List of benchmark results
        """
        all_nodes = list(graph.keys())
        results = []
        
        print(f"\n{'='*70}")
        print(f"Benchmarking {'Parallel' if use_parallel else 'Sequential'} Dijkstra's Algorithm")
        if use_parallel:
            print(f"Number of threads: {num_threads}")
        print(f"{'='*70}")
        
        for i in range(test_cases):
            # Randomly select source and destination
            source = random.choice(all_nodes)
            destination = random.choice(all_nodes)
            
            # Skip if same node
            if source == destination:
                continue
            
            # Run algorithm
            if use_parallel and self._openmp_solver_path() is not None:
                solver_result = self._run_openmp_solver(source, destination, num_threads)
                result = {
                    'source': solver_result['source'],
                    'destination': solver_result['destination'],
                    'distance': solver_result['distance'],
                    'path': solver_result['path'],
                    'path_length': solver_result['path_length'],
                    'computation_time': solver_result['computation_time_ms'] / 1000.0,
                    'algorithm': solver_result['algorithm'],
                    'num_threads': solver_result['num_threads']
                }
            else:
                if use_parallel:
                    print("OpenMP binary not found. Using Python multiprocessing fallback for this benchmark.")
                result = DijkstraAlgorithm.dijkstra_with_timing(
                    graph, source, destination, use_parallel, num_threads
                )
            
            results.append(result)
            
            print(f"Test {i+1}: Source={source}, Dest={destination}, "
                  f"Distance={result['distance']:.2f}, "
                  f"Time={result['computation_time']*1000:.4f}ms")
        
        return results
    
    def run_full_benchmark(self, num_threads_list: List[int] = None,
                          test_cases_per_config: int = 20) -> Dict:
        """
        Run comprehensive benchmark with multiple configurations
        
        Args:
            num_threads_list: List of thread counts to test
            test_cases_per_config: Number of test cases per configuration
            
        Returns:
            Comprehensive benchmark results
        """
        if num_threads_list is None:
            max_threads = cpu_count()
            num_threads_list = [1, 2, 4, max(1, max_threads//2), max_threads]
            num_threads_list = sorted(list(set(num_threads_list)))
        
        # Load graph from database
        print("\nLoading graph from database...")
        graph = self.db.get_graph_as_dict()
        print(f"Graph loaded: {len(graph)} nodes")
        
        benchmark_results = {
            'timestamp': datetime.now().isoformat(),
            'database_stats': self.db.get_stats(),
            'configurations': {}
        }
        
        # Benchmark sequential
        seq_results = self.benchmark_implementation(
            graph, test_cases_per_config, use_parallel=False
        )
        benchmark_results['configurations']['sequential'] = {
            'results': seq_results,
            'stats': self._compute_statistics(seq_results)
        }
        
        # Benchmark parallel with different thread counts
        for num_threads in num_threads_list:
            config_name = f'parallel_{num_threads}t'
            par_results = self.benchmark_implementation(
                graph, test_cases_per_config, use_parallel=True, num_threads=num_threads
            )
            benchmark_results['configurations'][config_name] = {
                'results': par_results,
                'stats': self._compute_statistics(par_results)
            }
        
        return benchmark_results
    
    @staticmethod
    def _compute_statistics(results: List[Dict]) -> Dict:
        """Compute statistics from benchmark results"""
        if not results:
            return {}
        
        times = [r['computation_time'] for r in results]
        distances = [r['distance'] for r in results if r['distance'] != float('inf')]
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        # Standard deviation
        variance = sum((t - avg_time) ** 2 for t in times) / len(times)
        std_dev = variance ** 0.5
        
        return {
            'total_tests': len(results),
            'avg_execution_time_ms': avg_time * 1000,
            'min_execution_time_ms': min_time * 1000,
            'max_execution_time_ms': max_time * 1000,
            'std_deviation_ms': std_dev * 1000,
            'avg_path_distance': sum(distances) / len(distances) if distances else 0,
            'successful_paths': len(distances)
        }
    
    def generate_performance_report(self, benchmark_results: Dict, 
                                   output_file: str = 'performance_report.txt'):
        """
        Generate comprehensive performance analysis report
        
        Args:
            benchmark_results: Results from run_full_benchmark
            output_file: Output file path
        """
        report = []
        report.append("="*80)
        report.append("DIJKSTRA'S ALGORITHM - PERFORMANCE ANALYSIS REPORT")
        report.append("="*80)
        report.append(f"\nGenerated: {benchmark_results['timestamp']}")
        report.append(f"\nDatabase Statistics:")
        stats = benchmark_results['database_stats']
        report.append(f"  - Total Nodes: {stats['nodes']}")
        report.append(f"  - Total Edges: {stats['edges']}")
        report.append(f"  - Computed Paths: {stats['paths_computed']}")
        
        report.append("\n" + "="*80)
        report.append("PERFORMANCE METRICS BY CONFIGURATION")
        report.append("="*80)
        
        # Extract and compare statistics
        configs = benchmark_results['configurations']
        
        for config_name, config_data in configs.items():
            report.append(f"\n{config_name.upper()}:")
            report.append("-" * 40)
            
            stats = config_data['stats']
            report.append(f"  Total Tests Run: {stats['total_tests']}")
            report.append(f"  Average Execution Time: {stats['avg_execution_time_ms']:.4f} ms")
            report.append(f"  Min Execution Time: {stats['min_execution_time_ms']:.4f} ms")
            report.append(f"  Max Execution Time: {stats['max_execution_time_ms']:.4f} ms")
            report.append(f"  Standard Deviation: {stats['std_deviation_ms']:.4f} ms")
            report.append(f"  Successful Paths: {stats['successful_paths']}/{stats['total_tests']}")
            report.append(f"  Average Path Distance: {stats['avg_path_distance']:.2f}")
        
        # Speedup analysis
        report.append("\n" + "="*80)
        report.append("SPEEDUP AND EFFICIENCY ANALYSIS")
        report.append("="*80)
        
        seq_time = configs['sequential']['stats']['avg_execution_time_ms']
        
        for config_name, config_data in configs.items():
            if config_name != 'sequential':
                par_time = config_data['stats']['avg_execution_time_ms']
                speedup = seq_time / par_time if par_time > 0 else 0
                
                # Extract thread count from config name
                threads = int(config_name.split('_')[1].replace('t', ''))
                efficiency = (speedup / threads) * 100
                
                report.append(f"\n{config_name.upper()}:")
                report.append(f"  Speedup (vs Sequential): {speedup:.2f}x")
                report.append(f"  Parallel Efficiency: {efficiency:.2f}%")
                report.append(f"  Time Improvement: {((seq_time - par_time) / seq_time * 100):.2f}%")
        
        report.append("\n" + "="*80)
        report.append("CONCLUSIONS AND RECOMMENDATIONS")
        report.append("="*80)
        
        report.append("\n1. Performance Observations:")
        report.append("   - Sequential implementation provides baseline performance")
        report.append("   - Parallel implementations show varying efficiency levels")
        
        report.append("\n2. Scalability Analysis:")
        report.append("   - Review speedup vs thread count for optimal performance")
        report.append("   - Check for diminishing returns with increased threads")
        
        report.append("\n3. Recommendations:")
        report.append("   - For small graphs: Sequential implementation may be optimal")
        report.append("   - For large graphs: Use parallel with 4-8 threads (adjust per hardware)")
        report.append("   - Consider overhead vs. gain when choosing thread count")
        
        report_text = "\n".join(report)
        
        # Save report
        with open(output_file, 'w') as f:
            f.write(report_text)
        
        print(f"\nReport saved to: {output_file}")
        print(report_text)
        
        return report_text
    
    def export_results_csv(self, benchmark_results: Dict, 
                          output_file: str = 'performance_data.csv'):
        """
        Export detailed results to CSV for further analysis
        
        Args:
            benchmark_results: Results from run_full_benchmark
            output_file: CSV output file path
        """
        rows = []
        
        for config_name, config_data in benchmark_results['configurations'].items():
            for result in config_data['results']:
                rows.append({
                    'Configuration': config_name,
                    'Source': result['source'],
                    'Destination': result['destination'],
                    'Distance': result['distance'],
                    'Path_Length': result['path_length'],
                    'Computation_Time_ms': result['computation_time'] * 1000,
                    'Algorithm': result['algorithm'],
                    'Num_Threads': result['num_threads']
                })
        
        # Write CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"CSV data exported to: {output_file}")

if __name__ == "__main__":
    # Test performance analysis
    db = GraphDatabase('graph_data.db')
    db.connect()
    
    analyzer = PerformanceAnalyzer(db)
    results = analyzer.run_full_benchmark()
    
    analyzer.generate_performance_report(results)
    analyzer.export_results_csv(results)
    
    db.disconnect()
