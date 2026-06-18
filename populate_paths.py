import random
from database import GraphDatabase
from dijkstra import DijkstraAlgorithm

NUM_TESTS = 20

if __name__ == '__main__':
    db = GraphDatabase('graph_data.db')
    db.connect()
    graph = db.get_graph_as_dict()

    all_nodes = list(graph.keys())
    saved = 0

    for _ in range(NUM_TESTS):
        src = random.choice(all_nodes)
        dst = random.choice(all_nodes)
        if src == dst:
            continue
        result = DijkstraAlgorithm.dijkstra_with_timing(graph, src, dst, use_parallel=False, num_threads=1)
        # result keys: source,destination,distance,path,path_length,computation_time,algorithm,num_threads
        db.save_path_result(
            result['source'], result['destination'], float(result['distance']) if result['distance'] is not None else float('inf'),
            result['path'], result['computation_time'], result['algorithm'], result.get('num_threads', 1)
        )
        saved += 1

    print(f"Saved {saved} path results to database.")
    db.disconnect()
