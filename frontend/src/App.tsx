import { useState, useRef, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

type ViewKey = 'setup' | 'path' | 'benchmark' | 'stats';

type StatsData = {
  nodes: number;
  edges: number;
  paths_computed: number;
};

type PathResult = {
  source: number;
  destination: number;
  distance: number;
  path: number[];
  path_length: number;
  computation_time_ms: number;
  algorithm: string;
  num_threads: number;
  valid: boolean;
  calculated_distance: number;
  edge_distances?: number[];
};

type BenchmarkResult = {
  timestamp: string;
  database_stats: {
    nodes: number;
    edges: number;
    paths_computed: number;
  };
  configurations: Record<string, { stats: Record<string, number> }>;
};

function App() {
  const [view, setView] = useState<ViewKey>('setup');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [stats, setStats] = useState<StatsData | null>(null);
  const [pathRequest, setPathRequest] = useState<{ source: string; destination: string; use_parallel: boolean; num_threads: string }>({ source: '1', destination: '2', use_parallel: false, num_threads: '2' });
  const [pathResult, setPathResult] = useState<PathResult | null>(null);
  const [benchmarkResult, setBenchmarkResult] = useState<BenchmarkResult | null>(null);
  const [testCases, setTestCases] = useState(10);
  const [numNodes, setNumNodes] = useState('5000');

  const handleAction = async (action: () => Promise<void>) => {
    setMessage('');
    setLoading(true);
    try {
      await action();
    } catch (error) {
      setMessage('Operation failed. Check the API connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    await handleAction(async () => {
      const response = await fetch(`${API_BASE}/stats`);
      if (!response.ok) throw new Error('Stats fetch failed');
      const data = await response.json();
      setStats(data);
      setMessage('Database statistics loaded successfully.');
    });
  };

  const runSetup = async () => {
    await handleAction(async () => {
      const nodes = parseInt(numNodes || '5000', 10) || 5000;
      const response = await fetch(`${API_BASE}/setup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ num_nodes: nodes, force: false }),
      });
      if (!response.ok) throw new Error('Setup failed');
      const data = await response.json();
      setStats({ nodes: data.nodes, edges: data.edges, paths_computed: 0 });
      setMessage(data.message);
    });
  };

  const requestPath = async () => {
    // Validate that all fields are selected
    if (!pathRequest.source || !pathRequest.destination || !pathRequest.num_threads) {
      setMessage('Please select source node, destination node, and threads before computing.');
      return;
    }
    
    await handleAction(async () => {
      // parse and validate numeric inputs
      const src = parseInt(pathRequest.source || '', 10);
      const dst = parseInt(pathRequest.destination || '', 10);
      const threads = parseInt(pathRequest.num_threads || '1', 10) || 1;
      if (!src || !dst) throw new Error('Invalid source or destination');

      const payload = { source: src, destination: dst, use_parallel: pathRequest.use_parallel, num_threads: threads };

      const response = await fetch(`${API_BASE}/shortest-path`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error('Shortest path computation failed');
      const data = await response.json();
      setPathResult(data);
      setMessage('Shortest path computed successfully.');
    });
  };

  // Send a specific payload immediately (avoids relying on asynchronous setState)
  const requestPathWithPayload = async (payload: { source: number; destination: number; use_parallel: boolean; num_threads: number; }) => {
    await handleAction(async () => {
      const response = await fetch(`${API_BASE}/shortest-path`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error('Shortest path computation failed');
      const data = await response.json();
      setPathResult(data);
      setMessage('Shortest path computed successfully.');
    });
  };

  const runBenchmark = async () => {
    if (!testCases || testCases < 1) {
      setMessage('Please enter a valid number of test cases (at least 1).');
      return;
    }
    
    await handleAction(async () => {
      const response = await fetch(`${API_BASE}/benchmark`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test_cases_per_config: testCases }),
      });
      if (!response.ok) throw new Error('Benchmark failed');
      const data = await response.json();
      setBenchmarkResult(data as BenchmarkResult);
      setMessage('Benchmark completed. Review the performance summary.');
    });
  };

  return (
    <div className="app-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">Database-Driven Shortest Path Analysis & Visualization System</p>
          <h1>Parallel Dijkstra's Algorithm with OpenMP</h1>
          <p className="subtitle">
            Enterprise-grade graph analysis platform featuring parallel computation, performance benchmarking, and real-time path visualization powered by SQLite and OpenMP optimization.
          </p>
          <p className="attribution">Developed by ATA</p>
        </div>
      </header>

      <nav className="tab-row">
        {(['setup', 'path', 'benchmark', 'stats'] as ViewKey[]).map((item) => (
          <button
            key={item}
            className={view === item ? 'tab active' : 'tab'}
            onClick={() => {
              setView(item);
              if (item === 'stats') loadStats();
            }}
          >
            {item === 'setup' ? 'Setup' : item === 'path' ? 'Shortest Path' : item === 'benchmark' ? 'Benchmark' : 'Stats'}
          </button>
        ))}
      </nav>

      <main className="content-panel">
        <div className="status-bar">
          <span>{loading ? 'Running ...' : 'Ready'}</span>
          <span>{message}</span>
        </div>

        {view === 'setup' && (
          <section className="panel">
            <h2>Database Initialization</h2>
            <p>Configure and prepare the SQLite graph store with your desired number of nodes.</p>
            <div className="grid-form">
              <label>
                Number of Nodes
                <select value={numNodes} onChange={(event) => setNumNodes(event.currentTarget.value)}>
                  <option value="1000">1,000 nodes</option>
                  <option value="2000">2,000 nodes</option>
                  <option value="3000">3,000 nodes</option>
                  <option value="4000">4,000 nodes</option>
                  <option value="5000">5,000 nodes</option>
                  <option value="6000">6,000 nodes</option>
                  <option value="7000">7,000 nodes</option>
                  <option value="8000">8,000 nodes</option>
                  <option value="9000">9,000 nodes</option>
                  <option value="10000">10,000 nodes</option>
                </select>
              </label>
            </div>
            <button className="primary-button" onClick={runSetup} disabled={loading}>
              Initialize Database
            </button>
            <div className="panel-details">
              <strong>Current counts:</strong>
              <div>Nodes: {stats?.nodes ?? '—'}</div>
              <div>Edges: {stats?.edges ?? '—'}</div>
              <div>Paths Computed: {stats?.paths_computed ?? '—'}</div>
            </div>
          </section>
        )}

        {view === 'path' && (
          <section className="panel">
            <h2>Compute Shortest Path</h2>
            <div className="grid-form">
              <label>
                Source Node
                <select value={pathRequest.source} onChange={(event) => setPathRequest({ ...pathRequest, source: event.currentTarget.value })}>
                  <option value="">Select source...</option>
                  {Array.from({ length: 100 }, (_, i) => i + 1).map(i => (
                    <option key={i} value={String(i)}>{i}</option>
                  ))}
                </select>
              </label>
              <label>
                Destination Node
                <select value={pathRequest.destination} onChange={(event) => setPathRequest({ ...pathRequest, destination: event.currentTarget.value })}>
                  <option value="">Select destination...</option>
                  {Array.from({ length: 500 }, (_, i) => i + 1).map(i => (
                    <option key={i} value={String(i)}>{i}</option>
                  ))}
                </select>
              </label>
              <label>
                Use Parallel Mode
                <input
                  type="checkbox"
                  checked={pathRequest.use_parallel}
                  onChange={(event) => setPathRequest({ ...pathRequest, use_parallel: event.target.checked })}
                />
              </label>
              <label>
                Threads
                <select value={pathRequest.num_threads} onChange={(event) => setPathRequest({ ...pathRequest, num_threads: event.currentTarget.value })}>
                  <option value="1">1 thread</option>
                  <option value="2">2 threads</option>
                  <option value="4">4 threads</option>
                  <option value="8">8 threads</option>
                  <option value="16">16 threads</option>
                  <option value="32">32 threads</option>
                </select>
              </label>
            </div>
            <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              <button 
                className="primary-button" 
                onClick={requestPath} 
                disabled={loading || !pathRequest.source || !pathRequest.destination || !pathRequest.num_threads}
              >
                Compute Path
              </button>
              <button
                className="secondary-button"
                onClick={async () => {
                  // quick example: source 1 -> destination 100 using parallel solver
                  const example = { source: 1, destination: 100, use_parallel: true, num_threads: 4 };
                  // keep controlled inputs as strings
                  setPathRequest({ source: String(example.source), destination: String(example.destination), use_parallel: example.use_parallel, num_threads: String(example.num_threads) });
                  await requestPathWithPayload(example);
                }}
                disabled={loading}
              >
                Run Example (1 → 100)
              </button>
            </div>

            {pathResult && (
              <div className="result-card">
                <h3>Computed Result</h3>
                <div>Algorithm: {pathResult.algorithm}</div>
                <div>Distance: {typeof pathResult.distance === 'number' ? pathResult.distance.toFixed(2) : 'N/A'}</div>
                <div>Path length: {pathResult.path_length ?? 'N/A'}</div>
                <div>Time: {typeof pathResult.computation_time_ms === 'number' ? pathResult.computation_time_ms.toFixed(2) : 'N/A'} ms</div>
                <div>Valid path: {pathResult.valid ? 'Yes' : 'No'}</div>
                <div>Path: {Array.isArray(pathResult.path) && pathResult.path.length > 0 ? pathResult.path.join(' → ') : 'No path found'}</div>
              </div>
            )}
            {pathResult && pathResult.path && pathResult.path.length > 0 && (
              <section className="panel" style={{ marginTop: 16 }}>
                <h3>Path Visualization</h3>
                <PathVisualizer path={pathResult.path} />
                <div style={{ marginTop: 20 }}>
                  <h4 style={{ marginBottom: 10 }}>Interactive Network Graph</h4>
                  <PathNetworkVisualizer path={pathResult.path} edgeDistances={pathResult.edge_distances} />
                </div>
              </section>
            )}
          </section>
        )}

        {view === 'benchmark' && (
          <section className="panel">
            <h2>Performance Benchmark</h2>
            <p>Run a multi-configuration benchmark to compare sequential and parallel execution.</p>
            <div className="grid-form">
              <label>
                Test Cases
                <input
                  type="number"
                  value={testCases}
                  min={1}
                  onChange={(event) => setTestCases(Number(event.target.value))}
                />
              </label>
            </div>
            <button className="primary-button" onClick={runBenchmark} disabled={loading || !testCases || testCases < 1}>
              Run Benchmark
            </button>

            {benchmarkResult && (
              <div className="result-card">
                <h3>Benchmark Summary</h3>
                <div>Timestamp: {benchmarkResult.timestamp}</div>
                <div>Nodes: {benchmarkResult.database_stats.nodes}</div>
                <div>Edges: {benchmarkResult.database_stats.edges}</div>
                <div>
                  Configurations:
                  <ul>
                    {Object.entries(benchmarkResult.configurations).map(([key, config]) => (
                      <li key={key}>{key}: {Math.round(config.stats.avg_execution_time_ms)} ms avg</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </section>
        )}

        {view === 'stats' && (
          <section className="panel">
            <h2>Database Statistics</h2>
            <div className="stat-grid">
              <div className="stat-card">
                <span className="stat-value">{stats?.nodes ?? '—'}</span>
                <span className="stat-label">Total Nodes</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{stats?.edges ?? '—'}</span>
                <span className="stat-label">Total Edges</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{stats?.paths_computed ?? '—'}</span>
                <span className="stat-label">Saved Paths</span>
              </div>
            </div>
            <button className="secondary-button" onClick={loadStats} disabled={loading}>
              Refresh Statistics
            </button>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;

// Simple SVG path visualizer — lays out nodes horizontally and connects them
function PathVisualizer({ path }: { path: number[] }) {
  const width = 760;
  const height = 140;
  const pad = 24;
  const n = path.length;
  const positions = path.map((_, i) => {
    const x = n === 1 ? width / 2 : pad + (i * (width - pad * 2)) / (n - 1);
    const y = height / 2;
    return { x, y };
  });

  return (
    <div style={{ overflowX: 'auto' }}>
      <svg className="graph-svg" width={Math.min(width, Math.max(300, n * 80))} height={height}>
        {/* edges */}
        {positions.slice(1).map((pos, i) => {
          const a = positions[i];
          return <line key={i} x1={a.x} y1={a.y} x2={pos.x} y2={pos.y} stroke="#94a3b8" strokeWidth={3} />;
        })}

        {/* nodes */}
        {positions.map((p, i) => (
          <g key={i} transform={`translate(${p.x},${p.y})`}>
            <circle r={16} fill="#2563eb" stroke="#0f172a" strokeWidth={1} />
            <text x={0} y={4} textAnchor="middle" fill="#fff" fontWeight={700} fontSize={12}>
              {path[i]}
            </text>
          </g>
        ))}
      </svg>
      <div style={{ marginTop: 8, color: '#334155' }}>
        Nodes shown are the sequence of node IDs returned by the solver. If the path is long, scroll horizontally.
      </div>
    </div>
  );
}

function PathNetworkVisualizer({ path, edgeDistances }: { path: number[]; edgeDistances?: number[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const networkRef = useRef<any>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!containerRef.current) return;
      const vis = await import('vis-network/standalone');

      const nodes = path.map((id, i) => ({ id, label: String(id), title: `Node ${id}` }));
      const edges = path.slice(1).map((to, i) => {
        const dist = edgeDistances && edgeDistances[i] ? edgeDistances[i].toFixed(2) : '';
        return { 
          from: path[i], 
          to,
          label: dist,
          title: `Distance: ${dist}`
        };
      });

      // pass plain arrays to avoid strict DataSet typing issues in TS
      const data = {
        nodes,
        edges,
      };

      const options = {
        physics: {
          enabled: true,
          stabilization: { iterations: 200 },
        },
        nodes: { shape: 'dot', size: 16, font: { color: '#ffffff' }, color: { background: '#2563eb' } },
        edges: { color: '#94a3b8', width: 2, arrows: { to: { enabled: true, scaleFactor: 0.6 } }, font: { size: 12, color: '#64748b' } },
        layout: { improvedLayout: true },
        interaction: { hover: true, dragNodes: true, zoomView: true, dragView: true },
      };

      // destroy previous network
      if (networkRef.current) {
        try { networkRef.current.destroy(); } catch (e) {}
        networkRef.current = null;
      }

      if (cancelled) return;
      networkRef.current = new vis.Network(containerRef.current, data, options);
    })();

    return () => {
      cancelled = true;
      if (networkRef.current) {
        try { networkRef.current.destroy(); } catch (e) {}
        networkRef.current = null;
      }
    };
  }, [path, edgeDistances]);

  return <div ref={containerRef} style={{ height: 320, borderRadius: 12, border: '1px solid rgba(15,23,42,0.06)' }} />;
}
