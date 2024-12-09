import streamlit as st
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(layout="wide", page_title="Tree View")

# Title of the app
st.title("Visual Tree Hierarchy View with Fixed Perpendicular Connections")

# Sidebar inputs for the root node and tree structure
st.sidebar.header("Tree Hierarchy Input")
root_node = st.sidebar.text_input("Enter Root Node:", "Root")
sub_tree_input = st.sidebar.text_area(
    "Enter Sub-tree Nodes (parent: child1, child2):",
    """
Root: Node1, Node2, Node3, Node4
Node1: Node1.1, Node1.2
Node2: Node2.1, Node2.2
Node3: Node3.1, Node3.2
Node4: Node4.1, Node4.2
"""
)

# Function to parse input into a dictionary
def parse_tree_input(input_text):
    tree_dict = {}
    for line in input_text.strip().split("\n"):
        if ":" in line:
            parent, children = line.split(":")
            tree_dict[parent.strip()] = [child.strip() for child in children.split(",")]
    return tree_dict

# Recursive function to generate x, y positions for nodes and edges
def build_tree_positions(tree_dict, node, x=0, y=0, dx=2.0, level=0, pos=None, edges=None):
    if pos is None:
        pos = {}
    if edges is None:
        edges = []

    pos[node] = (x, y)

    if node in tree_dict:
        num_children = len(tree_dict[node])
        start_x = x - dx * (num_children - 1) / 2

        for i, child in enumerate(tree_dict[node]):
            child_x = start_x + i * dx
            child_y = y - 1.2  # Adjust vertical spacing closer
            edges.append(((x, y), (child_x, y - 0.4), (child_x, child_y)))  # Adjust perpendicular line height
            build_tree_positions(tree_dict, child, child_x, child_y, dx / 1.8, level + 1, pos, edges)

    return pos, edges

# Parse user input
tree_structure = parse_tree_input(sub_tree_input)

# Build positions and edges
if root_node and tree_structure:
    positions, edges = build_tree_positions(tree_structure, root_node)

    # Extract node positions
    x_nodes = [positions[node][0] for node in positions]
    y_nodes = [positions[node][1] for node in positions]
    node_names = list(positions.keys())

    # Extract edge coordinates for perpendicular lines
    edge_x = []
    edge_y = []
    for vertical, horizontal, final in edges:
        edge_x += [vertical[0], horizontal[0], None, horizontal[0], final[0], None]
        edge_y += [vertical[1], horizontal[1], None, horizontal[1], final[1], None]

    # Create Plotly figure
    fig = go.Figure()

    # Add edges as perpendicular lines
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=3, color='gray'),
        hoverinfo='none',
        name="Edges",
    ))

    # Add nodes as transparent circles with white text
    fig.add_trace(go.Scatter(
        x=x_nodes, y=y_nodes,
        mode='markers+text',
        text=node_names,
        textfont=dict(size=26, color='white'),  # Increased font size
        textposition="middle center",
        marker=dict(size=40, color='black', line=dict(width=2, color='rgba(0,0,0,0)')),  # Transparent border
        name="Nodes",
    ))

    # Update layout for a clean look with black background
    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(t=20, b=20, l=20, r=20),
        plot_bgcolor="black",  # Black chart background
        paper_bgcolor="black",  # Black surrounding background
        width=1400,  # Increase figure width
        height=800  # Increase figure height
    )

    # Display the Plotly tree in Streamlit
    st.write("### Visual Tree View with Fixed Line Connections:")
    st.plotly_chart(fig)

else:
    st.warning("Please provide a valid root node and sub-tree structure.")
