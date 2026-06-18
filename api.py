from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pathlib import Path
from typing import List, Optional
import json
import subprocess

from database import GraphDatabase
from dijkstra import DijkstraAlgorithm
from performance import PerformanceAnalyzer
import math
from typing import Any


def sanitize_for_json(obj: Any) -> Any:
    """Recursively coerce numbers to JSON-safe types and replace non-finite values with None.

    This attempts to handle built-in floats/ints, numpy numeric types, and Decimal by
    converting to float where possible and treating non-finite values as None.
    """
    # dicts, lists, tuples — recurse
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(sanitize_for_json(v) for v in obj)

    # Try to coerce numeric-like objects to float
    try:
        if isinstance(obj, (int, float)):
            val = float(obj)
        else:
            # noqa: F401 - may raise for non-numeric types
            val = float(obj)
    except Exception:
        return obj

    # Now val is a float; check finiteness
    if not math.isfinite(val):
        return None

    # If original was int-like, return int; otherwise return float
    if isinstance(obj, int):
        return int(val)
    return val

app = FastAPI(
    title="Dijkstra Web API",
    description="Backend API for Dijkstra shortest path visualization and benchmarking.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SetupRequest(BaseModel):
    num_nodes: int = Field(default=5000, ge=100, description="Number of nodes to generate")
    force: bool = Field(default=False, description="Force database regeneration")


class SetupResponse(BaseModel):
    nodes: int
    edges: int
    message: str


class ShortestPathRequest(BaseModel):
    source: int
    destination: int
    use_parallel: bool = False
    num_threads: Optional[int] = 1


class ShortestPathResponse(BaseModel):
    source: int
    destination: int
    distance: Optional[float]
    path: List[int]
    path_length: int
    computation_time_ms: float
    algorithm: str
    num_threads: int
    valid: bool
    calculated_distance: Optional[float]


class BenchmarkRequest(BaseModel):
    test_cases_per_config: int = Field(default=10, ge=1)
    thread_counts: Optional[List[int]] = Field(default=None)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "message": "Dijkstra API is running"}


@app.post("/setup", response_model=SetupResponse)
def setup_graph(request: SetupRequest) -> SetupResponse:
    with GraphDatabase("graph_data.db") as db:
        db.create_tables()
        stats = db.get_stats()

        if stats["nodes"] > 0 and request.force:
            db.clear_all()
            db.generate_sample_data(request.num_nodes)
        elif stats["nodes"] < request.num_nodes:
            if stats["nodes"] > 0:
                db.clear_all()
            db.generate_sample_data(request.num_nodes)

        stats = db.get_stats()

    return SetupResponse(
        nodes=stats["nodes"],
        edges=stats["edges"],
        message="Database ready with graph data."
    )


def run_openmp_solver(source: int, destination: int, num_threads: int) -> dict:
    exe_name = "dijkstra_openmp.exe" if Path("dijkstra_openmp.exe").exists() else "dijkstra_openmp"
    solver_path = Path(exe_name)
    if not solver_path.exists():
        raise FileNotFoundError("OpenMP solver binary not found. Build dijkstra_openmp first.")

    command = [str(solver_path), "graph_data.db", str(source), str(destination), str(num_threads)]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise HTTPException(status_code=500, detail=f"OpenMP solver failed: {completed.stderr.strip()}")

    out = completed.stdout.strip()
    try:
        # extract JSON object
        start = out.find('{')
        end = out.rfind('}')
        json_text = out[start:end+1] if start != -1 and end != -1 and end > start else out
        # sanitize non-JSON floats
        import re
        json_text = re.sub(r'(?<=:\s)(-?inf|nan)(?=[,\}])', 'null', json_text, flags=re.IGNORECASE)
        parsed = json.loads(json_text)
        if 'distance' in parsed and parsed['distance'] is None:
            parsed['distance'] = None
        return parsed
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Invalid JSON from OpenMP solver: {exc}. Stdout: {out} | Stderr: {completed.stderr}")


@app.get("/stats")
def get_database_stats() -> dict:
    with GraphDatabase("graph_data.db") as db:
        db.create_tables()
        stats = db.get_stats()

    return {
        "nodes": stats["nodes"],
        "edges": stats["edges"],
        "paths_computed": stats["paths_computed"],
    }


def extract_edge_distances(graph: dict, path: list) -> list:
    """Extract weights for each edge in the path"""
    edge_distances = []
    for i in range(len(path) - 1):
        src, dst = path[i], path[i + 1]
        if src in graph:
            for neighbor, weight in graph[src]:
                if neighbor == dst:
                    edge_distances.append(weight)
                    break
    return edge_distances


@app.post("/shortest-path")
def find_shortest_path(request: ShortestPathRequest):
    """Find shortest path between two nodes. Returns plain JSON dict to bypass Pydantic validation of inf."""
    with GraphDatabase("graph_data.db") as db:
        db.create_tables()
        graph = db.get_graph_as_dict()

    if request.source not in graph:
        raise HTTPException(status_code=404, detail="Source node not found")
    if request.destination not in graph:
        raise HTTPException(status_code=404, detail="Destination node not found")

    num_threads = request.num_threads if request.num_threads and request.num_threads > 0 else 1
    if request.use_parallel:
        solver_result = run_openmp_solver(request.source, request.destination, num_threads)
        dist = solver_result.get("distance")
        # convert non-finite distances to None for JSON
        try:
            import math
            if not math.isfinite(dist):
                dist_json = None
            else:
                dist_json = float(dist)
        except Exception:
            dist_json = None

        path_data = solver_result.get("path", [])
        edge_dists = extract_edge_distances(graph, path_data)
        
        resp = {
            'source': solver_result["source"],
            'destination': solver_result["destination"],
            'distance': dist_json,
            'path': path_data,
            'edge_distances': edge_dists,
            'path_length': solver_result["path_length"],
            'computation_time_ms': solver_result["computation_time_ms"],
            'algorithm': solver_result["algorithm"],
            'num_threads': solver_result["num_threads"],
            'valid': len(path_data) > 0,
            'calculated_distance': dist_json,
        }
        # Sanitize and return as JSONResponse to avoid Pydantic validation
        sanitized = sanitize_for_json(resp)
        return JSONResponse(content=sanitized)

    result = DijkstraAlgorithm.dijkstra_with_timing(
        graph,
        request.source,
        request.destination,
        use_parallel=False,
        num_threads=num_threads,
    )

    valid, calculated_distance = DijkstraAlgorithm.validate_path(graph, result["path"])

    # sanitize infinite distances for JSON
    try:
        import math
        dist_val = result["distance"]
        distance_json = None if not math.isfinite(dist_val) else float(dist_val)
        calc_json = None if not math.isfinite(calculated_distance) else float(calculated_distance)
    except Exception:
        distance_json = None
        calc_json = None

    path_data = result["path"]
    edge_dists = extract_edge_distances(graph, path_data)
    
    resp = {
        'source': request.source,
        'destination': request.destination,
        'distance': distance_json,
        'path': path_data,
        'edge_distances': edge_dists,
        'path_length': result["path_length"],
        'computation_time_ms': result["computation_time"] * 1000,
        'algorithm': result["algorithm"],
        'num_threads': result["num_threads"],
        'valid': valid,
        'calculated_distance': calc_json,
    }

    # Sanitize and return as JSONResponse to avoid Pydantic validation
    sanitized = sanitize_for_json(resp)
    return JSONResponse(content=sanitized)


@app.post("/benchmark")
def run_benchmark(request: BenchmarkRequest) -> dict:
    with GraphDatabase("graph_data.db") as db:
        db.create_tables()
        analyzer = PerformanceAnalyzer(db)
        results = analyzer.run_full_benchmark(
            num_threads_list=request.thread_counts,
            test_cases_per_config=request.test_cases_per_config,
        )

    return sanitize_for_json(results)
