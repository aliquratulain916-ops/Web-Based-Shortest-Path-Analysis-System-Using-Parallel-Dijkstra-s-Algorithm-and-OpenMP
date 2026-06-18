"""
Database Module for Graph Data Management
Handles creation, population, and retrieval of graph data from SQLite database
"""

import sqlite3
import random
from typing import Optional, Dict, List, Tuple, Any

class GraphDatabase:
    def __init__(self, db_path: str = 'graph_data.db') -> None:
        """Initialize database connection"""
        self.db_path: str = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def ensure_connected(self):
        """Ensure database connection is established"""
        if self.conn is None:
            self.connect()
        
    def connect(self) -> None:
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"Connected to database: {self.db_path}")

    def __enter__(self) -> 'GraphDatabase':
        self.connect()
        return self

    def __exit__(self, exc_type: Optional[type], exc_value: Optional[BaseException], traceback: Optional[Any]) -> None:
        self.disconnect()
        
    def disconnect(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            print("Database connection closed")
    
    def create_tables(self) -> None:
        """Create database schema"""
        self.ensure_connected()
        assert self.cursor is not None
        assert self.conn is not None
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                node_id INTEGER PRIMARY KEY,
                node_name TEXT NOT NULL UNIQUE,
                latitude REAL,
                longitude REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS edges (
                edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_node_id INTEGER NOT NULL,
                destination_node_id INTEGER NOT NULL,
                weight REAL NOT NULL,
                distance REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(source_node_id) REFERENCES nodes(node_id),
                FOREIGN KEY(destination_node_id) REFERENCES nodes(node_id),
                UNIQUE(source_node_id, destination_node_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS paths (
                path_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_node_id INTEGER NOT NULL,
                destination_node_id INTEGER NOT NULL,
                total_distance REAL,
                path_nodes TEXT,
                computation_time REAL,
                algorithm_type TEXT,
                num_threads INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(source_node_id) REFERENCES nodes(node_id),
                FOREIGN KEY(destination_node_id) REFERENCES nodes(node_id)
            )
        ''')
        
        self.conn.commit()
        print("Tables created successfully")
    
    def generate_sample_data(self, num_nodes: int = 5000) -> None:
        """Generate sample graph data with at least 5000 nodes"""
        self.ensure_connected()
        assert self.cursor is not None
        assert self.conn is not None
        print(f"\nGenerating {num_nodes} nodes and edges...")
        
        # Insert nodes
        nodes_data: List[Tuple[int, str]] = [(i, f"Node_{i}") for i in range(1, num_nodes + 1)]
        self.cursor.executemany(
            'INSERT INTO nodes (node_id, node_name) VALUES (?, ?)',
            nodes_data
        )
        
        # Insert edges (create a connected network)
        edges_data: List[Tuple[int, int, float]] = []
        random.seed(42)
        
        # Create edges for connectivity
        for i in range(1, num_nodes):
            # Connect each node to 2-5 random nodes
            num_connections = random.randint(2, 5)
            for _ in range(num_connections):
                dest = random.randint(1, num_nodes)
                if dest != i:
                    weight = round(random.uniform(1, 100), 2)
                    edges_data.append((i, dest, weight))
        
        self.cursor.executemany(
            'INSERT OR IGNORE INTO edges (source_node_id, destination_node_id, weight) VALUES (?, ?, ?)',
            edges_data
        )
        
        self.conn.commit()
        
        # Get counts
        self.cursor.execute('SELECT COUNT(*) FROM nodes')
        node_count = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT COUNT(*) FROM edges')
        edge_count = self.cursor.fetchone()[0]
        
        print(f"Generated {node_count} nodes")
        print(f"Generated {edge_count} edges")
    
    def clear_all(self) -> None:
        """Clear all data from tables"""
        self.ensure_connected()
        assert self.cursor is not None
        assert self.conn is not None
        self.cursor.execute('DELETE FROM paths')
        self.cursor.execute('DELETE FROM edges')
        self.cursor.execute('DELETE FROM nodes')
        self.conn.commit()
        print("All data cleared")
    
    def get_graph_as_dict(self) -> Dict[int, List[Tuple[int, float]]]:
        """Retrieve graph as adjacency list dictionary"""
        self.ensure_connected()
        assert self.cursor is not None
        self.cursor.execute('SELECT node_id FROM nodes ORDER BY node_id')
        graph: Dict[int, List[Tuple[int, float]]] = {row[0]: [] for row in self.cursor.fetchall()}

        self.cursor.execute('''
            SELECT source_node_id, destination_node_id, weight 
            FROM edges
        ''')

        for source, dest, weight in self.cursor.fetchall():
            graph.setdefault(source, []).append((dest, weight))

        return graph
    
    def get_all_nodes(self) -> List[int]:
        """Get all node IDs"""
        self.ensure_connected()
        assert self.cursor is not None
        self.cursor.execute('SELECT node_id FROM nodes ORDER BY node_id')
        return [row[0] for row in self.cursor.fetchall()]
    
    def save_path_result(self, source: int, destination: int, total_distance: float, path_nodes: List[int], 
                        computation_time: float, algorithm_type: str, num_threads: int = 1) -> None:
        """Save computed path to database"""
        self.ensure_connected()
        assert self.cursor is not None
        assert self.conn is not None
        path_str = ','.join(map(str, path_nodes))
        self.cursor.execute('''
            INSERT INTO paths 
            (source_node_id, destination_node_id, total_distance, path_nodes, 
             computation_time, algorithm_type, num_threads)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (source, destination, total_distance, path_str, computation_time, algorithm_type, num_threads))
        self.conn.commit()
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        self.ensure_connected()
        assert self.cursor is not None
        self.cursor.execute('SELECT COUNT(*) FROM nodes')
        node_count = int(self.cursor.fetchone()[0])

        self.cursor.execute('SELECT COUNT(*) FROM edges')
        edge_count = int(self.cursor.fetchone()[0])

        self.cursor.execute('SELECT COUNT(*) FROM paths')
        path_count = int(self.cursor.fetchone()[0])

        return {
            'nodes': node_count,
            'edges': edge_count,
            'paths_computed': path_count
        }

if __name__ == "__main__":
    # Test database setup
    db = GraphDatabase('graph_data.db')
    db.connect()
    db.create_tables()
    db.generate_sample_data(5000)
    stats = db.get_stats()
    print(f"\nDatabase Statistics: {stats}")
    db.disconnect()
