"""
Dijkstra's Shortest Path Algorithm Implementation
Includes both sequential and parallel (multiprocessing) versions
"""

import heapq
import time
from typing import Dict, List, Tuple
from multiprocessing import Pool, cpu_count
import math


def _relax_neighbor_batch(args):
    current_distance, neighbor_batch = args
    return [(neighbor, current_distance + weight) for neighbor, weight in neighbor_batch]


class DijkstraAlgorithm:
    
    @staticmethod
    def dijkstra_sequential(graph: Dict, source: int, destination: int) -> Tuple[float, List[int]]:
        """
        Sequential Dijkstra's algorithm implementation
        
        Args:
            graph: Adjacency list representation of the graph
            source: Starting node ID
            destination: Target node ID
            
        Returns:
            Tuple of (shortest_distance, path)
        """
        # Initialize distances and previous nodes
        distances = {node: float('inf') for node in graph}
        distances[source] = 0
        previous = {node: None for node in graph}
        
        # Priority queue: (distance, node)
        pq = [(0, source)]
        visited = set()
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            # Skip if already visited
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # If destination reached, break early
            if current_node == destination:
                break
            
            # Skip if distance is outdated
            if current_distance > distances[current_node]:
                continue
            
            # Update neighbors
            if current_node in graph:
                for neighbor, weight in graph[current_node]:
                    distance = current_distance + weight
                    
                    if distance < distances.get(neighbor, float('inf')):
                        distances[neighbor] = distance
                        previous[neighbor] = current_node
                        heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct path
        if distances.get(destination, float('inf')) == float('inf'):
            return float('inf'), []
        
        path = []
        current = destination
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        
        return distances[destination], path
    
    @staticmethod
    def dijkstra_parallel(graph: Dict, source: int, destination: int, 
                          num_threads: int = None) -> Tuple[float, List[int]]:
        """
        Parallel Dijkstra's algorithm using multiprocessing for neighbor relaxation.
        
        Args:
            graph: Adjacency list representation of the graph
            source: Starting node ID
            destination: Target node ID
            num_threads: Number of processes to use
            
        Returns:
            Tuple of (shortest_distance, path)
        """
        if num_threads is None:
            num_threads = cpu_count()
        
        distances = {node: float('inf') for node in graph}
        distances[source] = 0
        previous = {node: None for node in graph}
        
        pq = [(0, source)]
        visited = set()
        
        with Pool(processes=max(1, min(num_threads, cpu_count()))) as pool:
            while pq:
                current_distance, current_node = heapq.heappop(pq)
                
                if current_node in visited:
                    continue
                
                visited.add(current_node)
                
                if current_node == destination:
                    break
                
                if current_distance > distances.get(current_node, float('inf')):
                    continue
                
                neighbors_data = graph.get(current_node, [])
                if neighbors_data:
                    chunk_size = max(1, len(neighbors_data) // num_threads)
                    batches = [
                        neighbors_data[i:i + chunk_size]
                        for i in range(0, len(neighbors_data), chunk_size)
                    ]
                    
                    batch_args = [(current_distance, batch) for batch in batches]
                    for result_batch in pool.map(_relax_neighbor_batch, batch_args):
                        for neighbor, distance in result_batch:
                            if distance < distances.get(neighbor, float('inf')):
                                distances[neighbor] = distance
                                previous[neighbor] = current_node
                                heapq.heappush(pq, (distance, neighbor))
        
        if distances.get(destination, float('inf')) == float('inf'):
            return float('inf'), []
        
        path = []
        current = destination
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        
        return distances[destination], path
    
    @staticmethod
    def dijkstra_with_timing(graph: Dict, source: int, destination: int, 
                            use_parallel: bool = False, num_threads: int = None) -> Dict:
        """
        Run Dijkstra's algorithm and measure execution time
        
        Args:
            graph: Adjacency list representation
            source: Source node
            destination: Destination node
            use_parallel: Whether to use parallel version
            num_threads: Number of threads for parallel version
            
        Returns:
            Dictionary with results and timing information
        """
        start_time = time.time()
        
        if use_parallel:
            distance, path = DijkstraAlgorithm.dijkstra_parallel(
                graph, source, destination, num_threads
            )
        else:
            distance, path = DijkstraAlgorithm.dijkstra_sequential(
                graph, source, destination
            )
        
        end_time = time.time()
        computation_time = end_time - start_time
        
        return {
            'source': source,
            'destination': destination,
            'distance': distance,
            'path': path,
            'path_length': len(path),
            'computation_time': computation_time,
            'algorithm': 'Parallel' if use_parallel else 'Sequential',
            'num_threads': num_threads if use_parallel else 1
        }
    
    @staticmethod
    def validate_path(graph: Dict, path: List[int]) -> Tuple[bool, float]:
        """
        Validate if a path is valid and calculate its total distance
        
        Args:
            graph: Adjacency list
            path: List of nodes forming a path
            
        Returns:
            Tuple of (is_valid, total_distance)
        """
        if not path or len(path) < 1:
            return False, float('inf')
        
        total_distance = 0
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            
            # Find edge weight
            if current in graph:
                edge_found = False
                for neighbor, weight in graph[current]:
                    if neighbor == next_node:
                        total_distance += weight
                        edge_found = True
                        break
                
                if not edge_found:
                    return False, float('inf')
            else:
                return False, float('inf')
        
        return True, total_distance

if __name__ == "__main__":
    # Test Dijkstra's algorithm
    test_graph = {
        1: [(2, 4), (3, 2)],
        2: [(3, 1), (4, 5)],
        3: [(4, 8), (5, 10)],
        4: [(5, 2)],
        5: []
    }
    
    print("Testing Sequential Dijkstra's:")
    result_seq = DijkstraAlgorithm.dijkstra_with_timing(test_graph, 1, 5, use_parallel=False)
    print(result_seq)
    
    print("\nTesting Parallel Dijkstra's:")
    result_par = DijkstraAlgorithm.dijkstra_with_timing(test_graph, 1, 5, use_parallel=True, num_threads=2)
    print(result_par)
