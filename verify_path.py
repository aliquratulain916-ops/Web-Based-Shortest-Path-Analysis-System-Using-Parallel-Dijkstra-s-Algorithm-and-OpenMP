import sqlite3

conn = sqlite3.connect('graph_data.db')
cursor = conn.cursor()

# The path returned
path = [1, 2007, 475, 4915, 3856, 2169, 539, 10]

print("Validating path edges:")
print(f"Path: {' → '.join(map(str, path))}")
print("\nEdge verification:")

total_distance = 0
all_valid = True

for i in range(len(path) - 1):
    from_node = path[i]
    to_node = path[i + 1]
    
    # Check if edge exists
    cursor.execute('SELECT weight FROM graph_edges WHERE source = ? AND target = ?', (from_node, to_node))
    result = cursor.fetchone()
    
    if result:
        weight = result[0]
        total_distance += weight
        print(f"✓ {from_node} → {to_node}: {weight:.2f}")
    else:
        # Try reverse direction
        cursor.execute('SELECT weight FROM graph_edges WHERE source = ? AND target = ?', (to_node, from_node))
        result = cursor.fetchone()
        if result:
            weight = result[0]
            total_distance += weight
            print(f"✓ {from_node} ← {to_node}: {weight:.2f} (reverse)")
        else:
            print(f"✗ NO EDGE: {from_node} → {to_node}")
            all_valid = False

print(f"\nTotal distance calculated: {total_distance:.2f}")
print(f"Distance from API: 266.69")
print(f"Difference: {abs(total_distance - 266.69):.2f}")
print(f"Match: {abs(total_distance - 266.69) < 0.01}")
print(f"All edges valid: {all_valid}")

# Also check if there's a shorter path
print("\n--- Checking for direct edge 1->10 ---")
cursor.execute('SELECT weight FROM graph_edges WHERE source = 1 AND target = 10')
result = cursor.fetchone()
if result:
    print(f"Direct edge 1→10 exists with weight: {result[0]:.2f}")
else:
    cursor.execute('SELECT weight FROM graph_edges WHERE source = 10 AND target = 1')
    result = cursor.fetchone()
    if result:
        print(f"Reverse edge 10→1 exists with weight: {result[0]:.2f}")
    else:
        print("No direct edge between 1 and 10")

conn.close()
