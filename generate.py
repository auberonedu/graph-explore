import os
import shutil
import json

# ===============================================
# Configure your directed graph here!
# -----------------------------------------------
graph = {
    3:   [7, 34],
    7:   [12, 45, 34, 56],
    12:  [7, 56, 78],
    34:  [34, 23, 91],
    56:  [78],
    78:  [91],
    91:  [56],
    45:  [23],
    23:  [7],
    67:  [91]
}

starting_nodes = [3, 67, 7]

# ===============================================
# Site generation functions
# ===============================================

OUTPUT_FOLDER = "graph_site"

def create_css_file(output_folder):
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
  display: inline-block;
  background: #fff;
  border: 2px solid #333;
  border-radius: 999px;
  padding: 0.5em 1em;
  margin: 0.5em;
  cursor: pointer;
}

.index-list li a {
  color: #333;
  text-decoration: none;
}

.index-list li:hover {
  background: #333;
  color: #fff;
}

/* Styling for the D3 visualization */
svg {
  border: 1px solid #ccc;
  background-color: #fff;
}

/* Prevent text selection in the D3 visualization */
.labels text {
   user-select: none;
}
    """
    with open(os.path.join(output_folder, "styles.css"), "w", encoding="utf-8") as f:
        f.write(css_content)

def generate_node_page(node_value, neighbors, output_folder):
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
    list_items = ""
    for node in starting_nodes:
        list_items += f'<li onclick="window.location.href=\'node_{node}.html\'">{node}</li>\n'
    
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
    <p>You can also open <code>viz.html</code> for a visual representation of the graph.</p>
</body>
</html>
"""
    filename = os.path.join(output_folder, "index.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_viz_page(graph, output_folder):
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
</head>
<body>
    <h1>Graph Visualization</h1>
    <svg width="800" height="600"></svg>
    <script>
        const graph = {viz_json};

        const svg = d3.select("svg");
        const width = +svg.attr("width");
        const height = +svg.attr("height");

        // Define arrow marker for directed edges
        svg.append("defs").append("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 22)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#333");

        // Create a container for the links
        const link = svg.append("g")
            .attr("class", "links")
            .selectAll("path")
            .data(graph.links)
            .enter().append("path")
            .attr("stroke-width", 2)
            .attr("stroke", "#333")
            .attr("fill", "none")
            .attr("marker-end", "url(#arrow)");

        // Create a container for nodes (each is a <g> with a circle and text)
        const node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(graph.nodes)
            .enter().append("g")
            .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));

        node.append("circle")
            .attr("r", 20)
            .attr("fill", "#fff")
            .attr("stroke", "#333");

        node.append("text")
            .attr("dy", 4)
            .attr("text-anchor", "middle")
            .attr("fill", "#333")
            .text(d => d.id);

        // Set up the simulation
        const simulation = d3.forceSimulation(graph.nodes)
            .force("link", d3.forceLink(graph.links).id(d => d.id).distance(120))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        simulation.on("tick", () => {{
            link.attr("d", function(d) {{
                if (d.source.id === d.target.id) {{
                    // Self-loop logic
                    const r = 25; // Loop radius
                    const offsetX = d.source.x + 20; // Shift slightly to the right
                    const offsetY = d.source.y - 20; // Shift slightly upward
                    return `M ${{offsetX}},${{offsetY}} A ${{r}},${{r}} 0 1,1 ${{offsetX - 1}},${{offsetY}}`;
                }} else {{
                    // Normal straight path
                    return `M ${{d.source.x}},${{d.source.y}} L ${{d.target.x}},${{d.target.y}}`;
                }}
            }});

            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
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
    for node_value, neighbors in graph.items():
        generate_node_page(node_value, neighbors, output_folder)

def main():
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    create_css_file(OUTPUT_FOLDER)
    generate_index_page(starting_nodes, OUTPUT_FOLDER)
    generate_node_pages(graph, OUTPUT_FOLDER)
    generate_viz_page(graph, OUTPUT_FOLDER)

    print(f"Website generated in folder: {OUTPUT_FOLDER}")
    print("Open 'index.html' to explore the graph or 'viz.html' to see the interactive visualization.")

if __name__ == "__main__":
    main()
