# Image-Based Pathfinding Analysis

This Python script performs a complete analysis pipeline: it reads an image, identifies key points of interest based on color, constructs a weighted graph from these points, and calculates various optimal paths. The final results, including the calculated paths and coordinates, are then visualized by drawing them directly onto the source image.

## How It Works

The application follows a four-step process from image input to visual output.

### 1\. Image Processing & Node Detection

The script first opens the input image (`Media.jpg`) and scans it pixel by pixel to find the coordinates of specific colored dots. It identifies four key "dynamic nodes":

  * **Left & Right Yellow dots**
  * **Left & Right Orange dots**

### 2\. Graph Construction

Once the dynamic nodes are found, the script builds a **Directed Acyclic Graph (DAG)**. This graph includes:

  * The four dynamic nodes found in the image.
  * Several predefined static "intersection" nodes with fixed coordinates.
  * **Edges** connecting these nodes, where the weight of each edge is the Euclidean distance between the nodes. A specific vertical edge has its weight multiplied to simulate higher "cost."

### 3\. Pathfinding Calculations

With the graph in place, the script calculates three distinct paths:

  * **Shortest Path** from `Left Yellow` to `Right Yellow`.
  * **Shortest Path** from `Left Orange` to `Right Orange`.
  * **Longest Path** from `Left Yellow` to `Right Orange`.

### 4\. Visualization

The final step is to draw the results. The script takes the original image and overlays the calculated paths with different colors (green, blue, and red). It also **labels the coordinates** of the four dynamic nodes directly on the image for clear identification. The final annotated image is saved as `results_mapped.png`.

-----

## Algorithms Used

This script employs three core algorithms to determine the different paths.

### Dijkstra's Algorithm 🛣️

  * **Purpose**: Used to find the **shortest path** between two nodes in a weighted graph.
  * **Application**: In this code, it calculates the shortest possible route for the `Yellow -> Yellow` path and the `Orange -> Orange` path. It works by exploring the graph and always choosing the next node with the lowest total distance from the start.

### Topological Sort (Kahn's Algorithm) ➡️

  * **Purpose**: This algorithm creates a linear ordering of nodes in a **Directed Acyclic Graph (DAG)**. It ensures that for every directed edge from node `A` to node `B`, `A` comes before `B` in the sequence.
  * **Application**: It's a preparatory step for finding the longest path. It organizes the graph nodes in a logical left-to-right sequence, which is essential for the longest path algorithm to work correctly.

### Longest Path in a DAG 📈

  * **Purpose**: Used to find the path with the **maximum total weight** between two nodes in a DAG. Unlike the general longest path problem (which is NP-hard), it can be solved efficiently on a DAG.
  * **Application**: After the graph is topologically sorted, this algorithm processes the nodes in that order to find the longest route for the `Yellow -> Orange` path.

-----

## How to Run

### Prerequisites

You need Python 3 and the `Pillow` library. You can install it via pip:

```bash
pip install Pillow
```

### Execution

1.  Place your input image named `Media.jpg` in the same directory as the Python script.
2.  Run the script from your terminal:
    ```bash
    python app.py
    ```
3.  The script will print the found coordinates and path details to the console, and the final visual output will be saved as `results_mapped.png`.

-----

## Sample Output

### Console Output

When the script is run, it produces the following output in the terminal, showing the results of each step:

```text
Attempting to open image file: Media.jpg
Image file opened successfully.

Successfully found colored dots in the image:
 - Left Yellow: (28, 57)
 - Right Yellow: (1133, 379)
 - Left Orange: (43, 120)
 - Right Orange: (1144, 303)
--------------------
Graph built. Calculating paths...

--- Path Mapping Results ---
1. Shortest Path (Yellow -> Yellow):
   - Path: Left Yellow -> I_Top_Wavy -> I_Top_Diag1 -> I_Mid_Diag1 -> I_Low_Diags -> I_Bot_Diag1 -> Right Yellow
   - Length: 1290.30 units

2. Shortest Path (Orange -> Orange):
   - Path: Left Orange -> I_Mid_Diag2 -> I_Low_Diags -> Right Orange
   - Length: 1162.28 units

3. Longest Path (Yellow -> Orange):
   - Path: Left Yellow -> I_Top_Wavy -> I_Low_Wavy -> I_Low_Diags -> Right Orange
   - Length: 1492.71 units

Attempting to save the visual map to 'results_mapped.png'...
--- SUCCESS ---
Visual map has been saved as 'results_mapped.png'.
Please check your file directory to view the image.
```

-----

## Input & Output Images

*(Note: For the images to display correctly in the README on Git, `Media.jpg` and `results_mapped.png` must be committed to the repository.)*

### Input Image (`Media.jpg`)

This is the source image that the script analyzes.

### Output Image (`results_mapped.png`)

This is the final generated image, showing the calculated paths and the coordinates of the start/end nodes.

  * \<span style="color:green;"\>**Green Path**\</span\>: Shortest path (Yellow -\> Yellow)
  * \<span style="color:blue;"\>**Blue Path**\</span\>: Shortest path (Orange -\> Orange)
  * \<span style="color:red;"\>**Red Path**\</span\>: Longest path (Yellow -\> Orange)
