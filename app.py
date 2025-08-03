import heapq
import math
from PIL import Image, ImageDraw, ImageFont
from collections import deque

# --- 1. Image Processing to Find Nodes ---

def find_colored_dots(image_path):
    """
    Analyzes an image to find the coordinates of colored dots.
    """
    try:
        print(f"Attempting to open image file: {image_path}")
        img = Image.open(image_path).convert('RGB')
        print("Image file opened successfully.")
    except FileNotFoundError:
        print(f"\n--- FATAL ERROR ---")
        print(f"The file '{image_path}' was not found.")
        print(f"Please make sure 'Media.jpg' is in the same folder as your script.")
        return None, None

    width, height = img.size
    pixels = img.load()

    YELLOW_TARGET = (255, 255, 0)
    ORANGE_TARGET = (255, 165, 0)
    COLOR_TOLERANCE = 50

    def is_color_match(pixel_rgb, target_rgb):
        return all(abs(pixel_rgb[i] - target_rgb[i]) < COLOR_TOLERANCE for i in range(3))

    yellow_points, orange_points = [], []
    for x in range(width):
        for y in range(height):
            if is_color_match(pixels[x, y], YELLOW_TARGET):
                yellow_points.append((x, y))
            elif is_color_match(pixels[x, y], ORANGE_TARGET):
                orange_points.append((x, y))

    if not yellow_points or not orange_points:
        print("\n--- FATAL ERROR ---")
        print("Could not find the yellow or orange dots in the image.")
        print("Please ensure the image is correct and the colors are clear.")
        return None, None

    yellow_points.sort(); orange_points.sort()
    found_nodes = {
        'Left Yellow': yellow_points[0], 'Right Yellow': yellow_points[-1],
        'Left Orange': orange_points[0], 'Right Orange': orange_points[-1]
    }
    
    print("\nSuccessfully found colored dots in the image:")
    for name, coord in found_nodes.items():
        print(f" - {name}: {coord}")
    print("-" * 20)
    return found_nodes, img


# --- 2. Graph Construction ---

def build_graph(dynamic_nodes):
    """Builds the graph structures from node coordinates."""
    node_coordinates = dynamic_nodes.copy()
    static_nodes = {
        'I_Top_Wavy': (100, 50), 'I_Top_Diag1': (350, 50),
        'I_Mid_Diag2': (280, 150), 'I_Mid_Diag1': (470, 150),
        'I_Low_Wavy': (200, 350), 'I_Low_Diags': (600, 350),
        'I_Bot_Diag1': (730, 450),
    }
    node_coordinates.update(static_nodes)
    
    graph = {node: [] for node in node_coordinates}

    def get_distance(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def add_edge(u, v, weight_multiplier=1.0):
        p1, p2 = node_coordinates[u], node_coordinates[v]
        # Ensure the graph is directed from left-to-right based on x-coordinate
        if p1[0] > p2[0]: u, v = v, u 
        weight = get_distance(node_coordinates[u], node_coordinates[v]) * weight_multiplier
        graph[u].append((v, weight))

    # Define all connections
    add_edge('Left Yellow', 'I_Top_Wavy'); add_edge('I_Top_Wavy', 'I_Top_Diag1')
    add_edge('Left Orange', 'I_Mid_Diag2'); add_edge('I_Mid_Diag2', 'I_Mid_Diag1')
    add_edge('I_Low_Wavy', 'I_Low_Diags'); add_edge('I_Low_Diags', 'Right Orange')
    add_edge('I_Bot_Diag1', 'Right Yellow'); add_edge('I_Top_Wavy', 'I_Low_Wavy', 1.5)
    add_edge('I_Top_Diag1', 'I_Mid_Diag1'); add_edge('I_Mid_Diag1', 'I_Low_Diags')
    add_edge('I_Low_Diags', 'I_Bot_Diag1'); add_edge('I_Mid_Diag2', 'I_Low_Diags')
    
    return graph, node_coordinates


# --- 3. Pathfinding Algorithms ---

def find_shortest_path(graph_dict, start_node, end_node):
    """Finds the shortest path in an undirected graph using Dijkstra's algorithm."""
    # Create an undirected version for Dijkstra's
    undirected_graph = {node: {} for node in graph_dict}
    for u, neighbors in graph_dict.items():
        for v, weight in neighbors:
            undirected_graph[u][v] = weight
            undirected_graph[v][u] = weight
    
    distances = {node: float('inf') for node in undirected_graph}
    distances[start_node], predecessors, pq = 0, {}, [(0, start_node)]
    while pq:
        dist, current_node = heapq.heappop(pq)
        if dist > distances[current_node]: continue
        if current_node == end_node: break
        for neighbor, weight in undirected_graph[current_node].items():
            if distances[current_node] + weight < distances[neighbor]:
                distances[neighbor] = distances[current_node] + weight
                predecessors[neighbor] = current_node
                heapq.heappush(pq, (distances[neighbor], neighbor))
    path, node = [], end_node
    while node:
        path.insert(0, node)
        if node == start_node: break
        node = predecessors.get(node)
    return path, distances[end_node]

def find_longest_path_dag(graph, start_node, end_node):
    """Finds the longest path in a Directed Acyclic Graph (DAG)."""
    # Kahn's algorithm for topological sort
    in_degree = {u: 0 for u in graph}
    for u in graph:
        for v, _ in graph[u]: in_degree[v] += 1
    queue = deque([u for u in graph if in_degree[u] == 0])
    topo_order = []
    while queue:
        u = queue.popleft()
        topo_order.append(u)
        for v, _ in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0: queue.append(v)

    # Find longest path using the topological order
    distances = {node: -float('inf') for node in graph}
    distances[start_node], predecessors = 0, {}
    for u in topo_order:
        if distances[u] == -float('inf'): continue
        for v, weight in graph[u]:
            if distances[v] < distances[u] + weight:
                distances[v], predecessors[v] = distances[u] + weight, u
    path, node = [], end_node
    while node:
        path.insert(0, node)
        if node == start_node: break
        node = predecessors.get(node)
    return path, distances[end_node]


# --- 4. Function to Draw Paths and Coordinates on the Image ---

def draw_paths_on_image(original_image, paths_to_draw, node_coordinates, output_filename):
    """Draws the calculated paths and node coordinates onto the image and saves it."""
    drawable_image = original_image.copy()
    draw = ImageDraw.Draw(drawable_image)
    
    # Try to use a default font, handle if not found
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()

    # --- Draw the paths ---
    for path_info in paths_to_draw:
        path = path_info['path']
        color = path_info['color']
        for i in range(len(path) - 1):
            start_coord = node_coordinates[path[i]]
            end_coord = node_coordinates[path[i+1]]
            draw.line([start_coord, end_coord], fill=color, width=5)

    # --- NEW: Draw the coordinates for the dynamic start/end nodes ---
    nodes_to_label = ['Left Yellow', 'Right Yellow', 'Left Orange', 'Right Orange']
    for node_name in nodes_to_label:
        if node_name in node_coordinates:
            coords = node_coordinates[node_name]
            text = str(coords)
            # Position the text slightly offset from the dot for visibility
            text_position = (coords[0] + 10, coords[1] - 10) 
            # Draw a small background box for the text for better readability
            bbox = draw.textbbox(text_position, text, font=font)
            draw.rectangle(bbox, fill="white")
            draw.text(text_position, text, fill="black", font=font)

    try:
        print(f"\nAttempting to save the visual map to '{output_filename}'...")
        drawable_image.save(output_filename)
        print(f"--- SUCCESS ---")
        print(f"Visual map has been saved as '{output_filename}'.")
        print("Please check your file directory to view the image.")
    except Exception as e:
        print(f"\n--- FAILED TO SAVE IMAGE ---")
        print(f"An error occurred during the save operation: {e}")
        print("This is often caused by file permission issues in the environment.")
        print("You still have the text results above for your assignment.")


# --- 5. Main Execution ---

if __name__ == "__main__":
    IMAGE_FILE_PATH = 'Media.jpg'
    OUTPUT_IMAGE_PATH = 'results_mapped.png'

    start_end_nodes, original_image_obj = find_colored_dots(IMAGE_FILE_PATH)

    if original_image_obj and start_end_nodes:
        dag_graph, node_coords = build_graph(start_end_nodes)
        print("Graph built. Calculating paths...")
        
        path1, len1 = find_shortest_path(dag_graph, 'Left Yellow', 'Right Yellow')
        path2, len2 = find_shortest_path(dag_graph, 'Left Orange', 'Right Orange')
        path3, len3 = find_longest_path_dag(dag_graph, 'Left Yellow', 'Right Orange')

        print("\n--- Path Mapping Results ---")
        print("1. Shortest Path (Yellow -> Yellow):")
        print(f"   - Path: {' -> '.join(path1)}")
        print(f"   - Length: {len1:.2f} units\n")
        
        print("2. Shortest Path (Orange -> Orange):")
        print(f"   - Path: {' -> '.join(path2)}")
        print(f"   - Length: {len2:.2f} units\n")

        print("3. Longest Path (Yellow -> Orange):")
        print(f"   - Path: {' -> '.join(path3)}")
        print(f"   - Length: {len3:.2f} units")

        paths_to_visualize = [
            {'path': path1, 'color': 'green'},
            {'path': path2, 'color': 'blue'},
            {'path': path3, 'color': 'red'}
        ]
        
        draw_paths_on_image(original_image_obj, paths_to_visualize, node_coords, OUTPUT_IMAGE_PATH)
    else:
        print("\nScript terminated because the initial setup failed (e.g., image not found).")