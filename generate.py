import os
import shutil
import json

# ===============================================
# Configure your directed graph here!
# -----------------------------------------------
# The graph is defined as a dictionary where each key is a unique node value
# and its value is a list of neighbors (outgoing edges).
# Changes include:
#   - Node 7 now has an outdegree of 4.
#   - Node 12 (and node 34) have an outdegree of 3.
#   - At least one node (e.g., node 7) has an indegree of 3.
#   - The graph includes multiple cycles, a self-loop (34 points to itself),
#     and a bidirectional connection (7 <--> 12).
graph = {
    3:   [7, 34],           # indegree 0
    7:   [12, 45, 34, 56],    # outdegree 4
    12:  [7, 56, 78],        # outdegree 3
    34:  [34, 23, 91],       # outdegree 3 with a self-loop
    56:  [78],
    78:  [91],
    91:  [56],
    45:  [23],
    23:  [7],
    67:  [91]               # indegree 0
}

# Define the starting nodes for the main page.
# (List three nodes; here two have indegree 0: 3 and 67)
starting_nodes = [3, 67, 7]

# ===============================================
# Site generation functions
# ===============================================

OUTPUT_FOLDER = "graph_site"

def create_css_file(output_folder):
    """
    Creates a CSS file for styling the site.
    """
    css_content = """
/* Styling for the graph explorer site */
body {
  font-family: Arial, sans-serif;
  margin: 1em;
  padding: 0;
  text-align: center;
  background-color: #fdf8ee; /* light cream background */
}

h1.node-value {
  font-size: 3em;
  margin: 0.5em 0;
}

.neighbor-links {
  margin-top: 1em;
}

.neighbor-link {
  display: inline-block;
  text-decoration: none;
  color: #333;
  border: 2px solid #333;
  border-radius: 999px;
  padding: 0.5em 1em;
  margin: 0.2em;
  transition: background-color 0.2s, color 0.2s;
}

.neighbor-link:hover {
  background-color: #333;
  color: #fff;
}

.index-list {
  list-style: none;
  padding: 0;
}

.index-list li {
  margin: 0.5em 0;
}

a {
  color: #333;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Styling for the D3 visualization */
svg {
  border: 1px solid #ccc;
  background-color: #fff;
}
    """
    with open(os.path.join(output_folder, "styles.css"), "w", encoding="utf-8") as f:
        f.write(css_content)

def generate_node_page(node_value, neighbors, output_folder):
    """
    Generate a node page for a given node.
    
    Each page shows the node's value and buttons (links) for each neighbor.
    """
    # Build neighbor links (each button shows the neighbor's value)
    neighbor_links = ""
    for neighbor in neighbors:
        neighbor_links += f'<a class="neighbor-link" href="node_{neighbor}.html">{neighbor}</a>\n'
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Node {node_value}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1 class="node-value">Node {node_value}</h1>
    <div class="neighbor-links">
        {neighbor_links}
    </div>
</body>
</html>
"""
    filename = os.path.join(output_folder, f"node_{node_value}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_index_page(starting_nodes, output_folder):
    """
    Generate the starting page that lists a few nodes.
    """
    # Build list items for starting nodes
    list_items = ""
    for node in starting_nodes:
        list_items += f'<li><a href="node_{node}.html">{node}</a></li>\n'
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Graph Explorer</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>Graph Explorer</h1>
    <h2>Starting Nodes</h2>
    <ul class="index-list">
        {list_items}
    </ul>
</body>
</html>
"""
    filename = os.path.join(output_folder, "index.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_viz_page(graph, output_folder):
    """
    Generate a D3 visualization page for the graph.
    
    The page (viz.html) uses D3 to show a force-directed graph with arrows.
    Nodes are draggable and cannot be highlighted.
    """
    # Create nodes and links arrays for the D3 visualization.
    nodes = [{"id": str(node)} for node in graph.keys()]
    links = []
    for source, targets in graph.items():
        for target in targets:
            links.append({"source": str(source), "target": str(target)})

    viz_data = {"nodes": nodes, "links": links}
    viz_json = json.dumps(viz_data)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Graph Visualization</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
      /* Prevent text selection in the D3 visualization */
      .labels text {{
         user-select: none;
      }}
    </style>
</head>
<body>
    <h1>Graph Visualization</h1>
    <svg width="800" height="600"></svg>
    <script>
        // Embedded graph data
        const graph = {viz_json};

        const svg = d3.select("svg");
        const width = +svg.attr("width");
        const height = +svg.attr("height");

        // Define arrow marker for directed edges
        svg.append("defs").append("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 25)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#333");

        // Set up the simulation
        const simulation = d3.forceSimulation(graph.nodes)
            .force("link", d3.forceLink(graph.links).id(d => d.id).distance(120))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        // Draw links (edges) with a visible stroke color
        const link = svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(graph.links)
            .enter().append("line")
            .attr("stroke-width", 2)
            .attr("stroke", "#333")
            .attr("marker-end", "url(#arrow)");

        // Draw nodes (circles) with a white fill and dark stroke
        const node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(graph.nodes)
            .enter().append("circle")
            .attr("r", 20)
            .attr("fill", "#fff")
            .attr("stroke", "#333")
            .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));

        // Add labels to nodes with unselectable text
        const label = svg.append("g")
            .attr("class", "labels")
            .selectAll("text")
            .data(graph.nodes)
            .enter().append("text")
            .attr("dy", 4)
            .attr("text-anchor", "middle")
            .attr("fill", "#333")
            .style("user-select", "none")
            .text(d => d.id);

        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});

        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>
"""
    filename = os.path.join(output_folder, "viz.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_node_pages(graph, output_folder):
    """
    Generate a page for each node in the graph.
    """
    for node_value, neighbors in graph.items():
        generate_node_page(node_value, neighbors, output_folder)

def main():
    """
    Main entry point:
    - Create or wipe the output folder
    - Write the CSS, index, node, and viz pages
    """
    # Remove old site folder if it exists
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Create the CSS file
    create_css_file(OUTPUT_FOLDER)

    # Generate the starting page
    generate_index_page(starting_nodes, OUTPUT_FOLDER)

    # Generate a page for each node in the graph
    generate_node_pages(graph, OUTPUT_FOLDER)

    # Generate the D3 visualization page (unlinked from the main index)
    generate_viz_page(graph, OUTPUT_FOLDER)

    print(f"Website generated in folder: {OUTPUT_FOLDER}")
    print("Open 'index.html' inside that folder in your browser to explore the graph!")
    print("Open 'viz.html' to see the interactive D3 visualization.")

if __name__ == "__main__":
    main()
