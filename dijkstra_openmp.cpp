#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
#include <omp.h>
#include <sqlite3.h>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>

using Edge = std::pair<int, double>;
using AdjList = std::vector<std::vector<Edge>>;

struct EdgeInfo {
    int src;
    int dst;
    double weight;
};

static int exec_sqlite_query(sqlite3* db, const char* sql, int (*callback)(void*, int, char**, char**), void* data) {
    char* errmsg = nullptr;
    int rc = sqlite3_exec(db, sql, callback, data, &errmsg);
    if (rc != SQLITE_OK) {
        std::fprintf(stderr, "SQLite error: %s\n", errmsg ? errmsg : "unknown");
        sqlite3_free(errmsg);
    }
    return rc;
}

static int load_nodes_callback(void* userdata, int argc, char** argv, char** azColName) {
    auto* ids = reinterpret_cast<std::vector<int>*>(userdata);
    if (argc >= 1 && argv[0]) {
        ids->push_back(std::atoi(argv[0]));
    }
    return 0;
}

static int load_edges_callback(void* userdata, int argc, char** argv, char** azColName) {
    auto* edges = reinterpret_cast<std::vector<EdgeInfo>*>(userdata);
    if (argc >= 3 && argv[0] && argv[1] && argv[2]) {
        edges->push_back({std::atoi(argv[0]), std::atoi(argv[1]), std::atof(argv[2])});
    }
    return 0;
}

static std::tuple<AdjList, int> load_graph(const std::string& db_path, int source, int destination) {
    sqlite3* db = nullptr;
    if (sqlite3_open(db_path.c_str(), &db) != SQLITE_OK) {
        std::fprintf(stderr, "Unable to open database: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        std::exit(EXIT_FAILURE);
    }

    std::vector<int> node_ids;
    if (exec_sqlite_query(db, "SELECT node_id FROM nodes ORDER BY node_id;", load_nodes_callback, &node_ids) != SQLITE_OK) {
        sqlite3_close(db);
        std::exit(EXIT_FAILURE);
    }

    if (node_ids.empty()) {
        std::fprintf(stderr, "No nodes found in database.\n");
        sqlite3_close(db);
        std::exit(EXIT_FAILURE);
    }

    int max_node = *std::max_element(node_ids.begin(), node_ids.end());
    AdjList graph(max_node + 1);

    std::vector<struct EdgeInfo> edges;
    if (exec_sqlite_query(db, "SELECT source_node_id, destination_node_id, weight FROM edges;", load_edges_callback, &edges) != SQLITE_OK) {
        sqlite3_close(db);
        std::exit(EXIT_FAILURE);
    }

    sqlite3_close(db);

    for (const auto& edge : edges) {
        if (edge.src >= 0 && edge.src <= max_node && edge.dst >= 0 && edge.dst <= max_node) {
            graph[edge.src].emplace_back(edge.dst, edge.weight);
        }
    }

    return {graph, max_node};
}

static std::pair<double, std::vector<int>> dijkstra_openmp(const AdjList& graph, int source, int destination, int num_threads) {
    const int max_node = static_cast<int>(graph.size()) - 1;
    std::vector<double> distances(graph.size(), std::numeric_limits<double>::infinity());
    std::vector<int> previous(graph.size(), -1);
    std::vector<bool> visited(graph.size(), false);
    distances[source] = 0.0;

    using NodeDist = std::pair<double, int>;
    std::vector<std::pair<int, double>> updates;
    updates.reserve(128);

    auto compare = [](const NodeDist& a, const NodeDist& b) {
        return a.first > b.first;
    };
    std::vector<NodeDist> pq;
    pq.reserve(graph.size());
    pq.emplace_back(0.0, source);

    while (!pq.empty()) {
        std::pop_heap(pq.begin(), pq.end(), compare);
        auto [current_distance, current_node] = pq.back();
        pq.pop_back();

        if (visited[current_node]) {
            continue;
        }

        visited[current_node] = true;
        if (current_node == destination) {
            break;
        }

        if (current_distance > distances[current_node]) {
            continue;
        }

        const auto& neighbors = graph[current_node];
        updates.clear();

        omp_set_num_threads(num_threads);
#pragma omp parallel
        {
            std::vector<std::pair<int, double>> local_updates;
            local_updates.reserve(64);

#pragma omp for schedule(dynamic, 8)
            for (int i = 0; i < static_cast<int>(neighbors.size()); ++i) {
                int neighbor = neighbors[i].first;
                double weight = neighbors[i].second;
                double distance = current_distance + weight;
                if (distance < distances[neighbor]) {
                    local_updates.emplace_back(neighbor, distance);
                }
            }

#pragma omp critical
            {
                updates.insert(updates.end(), local_updates.begin(), local_updates.end());
            }
        }

        for (const auto& [neighbor, distance] : updates) {
            if (distance < distances[neighbor]) {
                distances[neighbor] = distance;
                previous[neighbor] = current_node;
                pq.emplace_back(distance, neighbor);
                std::push_heap(pq.begin(), pq.end(), compare);
            }
        }
    }

    if (distances[destination] == std::numeric_limits<double>::infinity()) {
        return {std::numeric_limits<double>::infinity(), {}};
    }

    std::vector<int> path;
    for (int current = destination; current != -1; current = previous[current]) {
        path.push_back(current);
    }
    std::reverse(path.begin(), path.end());
    return {distances[destination], path};
}

int main(int argc, char** argv) {
    if (argc < 4) {
        std::fprintf(stderr, "Usage: %s <database.db> <source> <destination> [num_threads]\n", argv[0]);
        return EXIT_FAILURE;
    }

    std::string db_path = argv[1];
    int source = std::atoi(argv[2]);
    int destination = std::atoi(argv[3]);
    int num_threads = 4;
    if (argc >= 5) {
        num_threads = std::max(1, std::atoi(argv[4]));
    }

    auto [graph, max_node] = load_graph(db_path, source, destination);
    if (source < 0 || source > max_node || destination < 0 || destination > max_node) {
        std::fprintf(stderr, "Source or destination node is out of bounds.\n");
        return EXIT_FAILURE;
    }

    const double start = omp_get_wtime();
    auto [distance, path] = dijkstra_openmp(graph, source, destination, num_threads);
    const double end = omp_get_wtime();

    std::printf("{\n");
    std::printf("  \"source\": %d,\n", source);
    std::printf("  \"destination\": %d,\n", destination);
    std::printf("  \"distance\": %.6f,\n", distance);
    std::printf("  \"path_length\": %zu,\n", path.size());
    std::printf("  \"computation_time_ms\": %.3f,\n", (end - start) * 1000.0);
    std::printf("  \"algorithm\": \"OpenMP\",\n");
    std::printf("  \"num_threads\": %d,\n", num_threads);
    std::printf("  \"path\": [");
    for (size_t i = 0; i < path.size(); ++i) {
        std::printf("%d", path[i]);
        if (i + 1 < path.size()) std::printf(", ");
    }
    std::printf("]\n");
    std::printf("}\n");

    return EXIT_SUCCESS;
}
