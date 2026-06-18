#!/usr/bin/env bash
# Build the OpenMP-enabled Dijkstra solver on Unix-like systems.
set -e
if command -v g++ >/dev/null 2>&1; then
  g++ -fopenmp -o dijkstra_openmp dijkstra_openmp.cpp -lsqlite3
  echo "Built dijkstra_openmp"
elif command -v clang++ >/dev/null 2>&1; then
  clang++ -fopenmp -o dijkstra_openmp dijkstra_openmp.cpp -lsqlite3
  echo "Built dijkstra_openmp"
else
  echo "No supported C++ compiler found. Install g++ or clang++."
  exit 1
fi
