import streamlit as st
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(layout="wide", page_title="Left-to-Right Tree View")

# Title of the app
st.title("Visual Tree Hierarchy View (Left to Right)")

# Sidebar inputs for the root node and tree structure
st.sidebar.header("Tree Hierarchy Input")
root_node = st.sidebar.text_input("Enter Root Node:", "Root")
sample_v = '$9000'
sub_tree_input = st.sidebar.text_area(
    "Enter Sub-tree Nodes (parent: child1, child2):",
    f"""
Root: Holdings, Investment, Market Value & P/L
Holdings: Original Quantity, New Quantity
Investment: Original Investment, New Investment
Market Value & P/L: Market Value, New Market Value, New Profit/Loss
New Profit/Loss: {sample_v}
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
def build_tree_positions(tree_dict, node, x=0, y=0, dy=4, level=0, pos=None, edges=None):
    if pos is None:
        pos = {}
    if edges is None:
        edges = []

    pos[node] = (x, y)

    if node in tree_dict:
        num_children = len(tree_dict[node])
        start_y = y - dy * (num_children - 1) / 5

        for i, child in enumerate(tree_dict[node]):
            child_x = x + 1.25# Move child nodes to the right
            child_y = start_y + i * dy
            edges.append(((x, y), (x + 0.25, child_y), (child_x, child_y)))  # Adjust left-to-right lines
            build_tree_positions(tree_dict, child, child_x, child_y, dy / 1.5, level + 1, pos, edges)

    return pos, edges

# Parse user input
tree_structure = parse_tree_input(sub_tree_input)

def display_tree(root_node, tree_structure):
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

        # Separate nodes into two groups: with digits and without digits
        nodes_with_digits = [(x, y, name) for x, y, name in zip(x_nodes, y_nodes, node_names) if any(char.isdigit() for char in name)]
        nodes_without_digits = [(x, y, name) for x, y, name in zip(x_nodes, y_nodes, node_names) if not any(char.isdigit() for char in name)]


        # Add nodes without digits (default font)
        fig.add_trace(go.Scatter(
            x=[x-0.4 for x, _, _ in nodes_without_digits],
            y=[y+0.2  for _, y, _ in nodes_without_digits],
            mode='markers+text',
            text=[name for _, _, name in nodes_without_digits],
            textfont=dict(size=18, color='orange'),  # Default font size
            textposition="middle center",
            marker=dict(size=40, color='black', line=dict(width=2, color='rgba(0,0,0,0)')),
            name="Nodes without Digits",
        ))

        # Add edges as perpendicular lines
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=2, color='gray'),
            hoverinfo='none',
            name="Edges",
        ))


        # Add nodes with digits (enlarged font)
        fig.add_trace(go.Scatter(
            x=[x-0.4 for x, _, _ in nodes_with_digits],
            y=[y+0.2 for _, y, _ in nodes_with_digits],
            mode='markers+text',
            text=[name for _, _, name in nodes_with_digits],
            textfont=dict(size=32, color='green'),  # Enlarged font size
            textposition="middle center",
            marker=dict(size=120, color='black', line=dict(width=2, color='rgba(0,0,0,0)')),
            name="Nodes with Digits",
        ))

        


        

        # top_left = False
        # x_nodes = [x_nodes[0]] + [x_node for i,x_node in enumerate(x_nodes) if i != 0]

        # # Add nodes as circles with text
        # fig.add_trace(go.Scatter(
        #     x=[x_nodes[0]], y=[y_nodes[0]],
        #     mode='markers+text',
        #     text=node_names,
        #     textfont=dict(size=26, color='white'),  # Increased font size
        #     textposition="middle center",
        #     marker=dict(size=40, color='black', line=dict(width=2, color='rgba(0,0,0,0)')),  # Transparent border
        #     name="Nodes",
        # ))

        

        
        # Update layout for a clean look with black background
        fig.update_layout(
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(t=20, b=20, l=20, r=20),
            plot_bgcolor="black",  # Black chart background
            paper_bgcolor="black",  # Black surrounding background
            width=650,  # Increase figure width
            height=800  # Increase figure height
        )

        # Display the Plotly tree in Streamlit
        st.write("### Left-to-Right Visual Tree View:")
        st.plotly_chart(fig)

    else:
        st.warning("Please provide a valid root node and sub-tree structure.")

display_tree(root_node, tree_structure)