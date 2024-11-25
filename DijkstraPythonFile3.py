import xmltodict as xtd 
import folium
import numpy as np
import webbrowser
import os, sys

# Parsing raw data from the .OSM file
with open('Maps/mapHSR.osm', "rb") as osm_fn:
    map_osm = xtd.parse(osm_fn)['osm']

# Parsing bounds from .OSM file
# Extracts the geographical bounds (latitude and longitude) from the OSM file.
ymax = map_osm['bounds']['@maxlat']
ymin = map_osm['bounds']['@minlat']
xmax = map_osm['bounds']['@maxlon']
xmin = map_osm['bounds']['@minlon']
parsed_bounds = [xmin, xmax, ymin, ymax]

# Parsing nodes from the OSM data
# Extracts individual nodes (points with lat/lon) and their IDs.
Node = map_osm['node']
Nnodes = len(Node)
Nodeid = [0] * Nnodes
xy = []
for i in range(Nnodes):
    Nodeid[i] = float(Node[i]['@id'])
    x = float(Node[i]['@lat'])
    y = float(Node[i]['@lon'])
    xy.append([x, y])
parsed_node = {'id': Nodeid, 'xy': xy}

# Parsing ways from the OSM data
# Extracts roadways or paths (ways) composed of multiple nodes and their tags.
Way = map_osm['way']
Nways = len(Way)
Wayid = [0] * Nways
nodes_in_way = [0] * Nways
tags = [0] * Nways
for i in range(Nways):
    tempWay = Way[i]
    Wayid[i] = float(tempWay['@id'])
    Nnd = len(tempWay['nd'])
    ndTemp = [0] * Nnd
    for j in range(Nnd):
        ndTemp[j] = float(tempWay['nd'][j]['@ref'])
    nodes_in_way[i] = ndTemp
    if 'tag' in tempWay.keys():
        if isinstance(tempWay['tag'], list):
            tags[i] = tempWay['tag']
        else:
            tags[i] = [tempWay['tag']]
    else:
        tags[i] = []
parsed_way = {'id': Wayid, 'nodes': nodes_in_way, 'tags': tags}

# Parsing relations from the OSM data
# Extracts relations between ways or nodes, typically for complex structures.
Relation = map_osm['relation']
Nrelation = len(Relation)
Relationid = [0] * Nrelation
for i in range(Nrelation):
    currentRelation = Relation[i]
    currentId = currentRelation['@id']
    Relationid[i] = float(currentId)
parsed_relation = {'id': Relationid}

# Compiling parsed OSM data
parsed_osm = {
    'bounds': parsed_bounds,
    'relation': parsed_relation,
    'way': parsed_way,
    'node': parsed_node,
    'attributes': map_osm.keys()
}

bounds = parsed_osm['bounds']
way = parsed_osm['way']
node = parsed_osm['node']
relation = parsed_osm['relation']

# Mapping node IDs to their indices for quick lookup
ways_num = len(way['id'])
ways_node_set = way['nodes']
node_ids = dict()
n = len(node['id'])
for i in range(n):
    node_ids[node['id'][i]] = i

# Defining road types considered for connectivity
road_vals = ['highway', 'motorway', 'motorway_link', 'trunk', 'trunk_link',
             'primary', 'primary_link', 'secondary', 'secondary_link',
             'tertiary', 'road', 'residential', 'living_street',
             'service', 'services', 'motorway_junction']

# Function to create a connectivity matrix between nodes
# This function builds a matrix representing connections between nodes in the OSM map.
def create_connectivity():
    """Create a connectivity matrix representing node connections based on the parsed OSM data.

    Returns:
        np.ndarray: A matrix with distances between connected nodes.
    """
    connectivity_matrix = np.full((Nnodes, Nnodes), float('inf'))
    np.fill_diagonal(connectivity_matrix, 0)

    for currentWay in range(ways_num):
        skip = True
        for i in way['tags'][currentWay]:
            if i['@k'] in road_vals:
                skip = False
                break
        if skip:
            continue

        nodeset = ways_node_set[currentWay]
        nodes_num = len(nodeset)

        for firstnode_local_index in range(nodes_num):
            firstnode_id = nodeset[firstnode_local_index]
            firstnode_index = node_ids.get(firstnode_id, -1)
            if firstnode_index == -1:
                continue

            for othernode_local_index in range(firstnode_local_index + 1, nodes_num):
                othernode_id = nodeset[othernode_local_index]
                othernode_index = node_ids.get(othernode_id, -1)
                if othernode_index == -1:
                    continue

                if (firstnode_id != othernode_id and connectivity_matrix[firstnode_index, othernode_index] == float('inf')):
                    connectivity_matrix[firstnode_index, othernode_index] = 1
                    connectivity_matrix[othernode_index, firstnode_index] = 1

    return connectivity_matrix

# Function implementing Dijkstra's algorithm
# This function finds the shortest path from a source node to other nodes.
def dijkstra(source, connectivity_matrix, p):
    """Apply Dijkstra's algorithm to find the shortest paths from the source node.

    Args:
        source (int): The starting node index.
        connectivity_matrix (np.ndarray): The matrix representing node connections.
        p (dict): A dictionary for storing path predecessors.
    """
    s = dict()
    s[source] = True
    p[source] = source

    v = len(connectivity_matrix)
    u = source
    d_u = float('inf')
    for i in range(v):
        if i != source and connectivity_matrix[source][i] < d_u:
            u = i
            d_u = connectivity_matrix[source][i]
    s[u] = True
    p[u] = source

    i = v - 2
    while i > 0:
        u_x = source
        d_u = float('inf')

        for j in range(v):
            if not s.get(j, False) and connectivity_matrix[source][u] != float('inf') and connectivity_matrix[u][j] != float('inf'):
                k = connectivity_matrix[source][u] + connectivity_matrix[u][j]
                connectivity_matrix[source][j] = min(connectivity_matrix[source][j], k)
                connectivity_matrix[j][source] = connectivity_matrix[source][j]

                if connectivity_matrix[source][j] == k:
                    p[j] = u
                elif connectivity_matrix[source][j] == 1:
                    p[j] = source

                if connectivity_matrix[source][j] < d_u:
                    u_x = j
                    d_u = connectivity_matrix[source][j]

        if u_x == source:
            break
        s[u_x] = True
        u = u_x
        i -= 1

# Function to plot routes from a source node
# Generates the shortest path tree for visualization.
def plot_routes(s, connectivity_matrix):
    """Generate route information from the source node using the connectivity matrix.

    Args:
        s (int): The source node index.
        connectivity_matrix (np.ndarray): The matrix representing node connections.

    Returns:
        tuple: A list of nodes with distances and a dictionary of path predecessors.
    """
    p = dict()
    dijkstra(s, connectivity_matrix, p)

    nodes_routes_values = []
    for i in p.keys():
        adder = [i, 0]
        while p[i] != i:
            adder[1] += 1
            i = p[i]
        nodes_routes_values.append(adder)

    # Add this line to print nodes_routes_values for verification
    print("nodes_routes_values:", nodes_routes_values)

    return nodes_routes_values, p

print("Please wait while all Nodes Map is Generating...")

# Function to build a map displaying all nodes
# Generates an HTML map showing all nodes parsed from the OSM file.


def BuildAllNodesMap():
    """
    Generates an interactive map using Folium that displays all nodes as circle markers.

    Each node is represented by a green circle marker, and the map is centered at the midpoint
    of the given geographic bounds.

    Returns:
        folium.Map: A Folium map object with all nodes marked.
    """
    x1, y1 = (float(bounds[2]), float(bounds[0]))
    x2, y2 = (float(bounds[3]), float(bounds[1]))
    center = ((x1 + x2) / 2, (y1 + y2) / 2)
    map_0 = folium.Map(location=center, zoom_start=16)

    for i in range(n):
        xy = (node['xy'][i][0], node['xy'][i][1])
        folium.CircleMarker(xy, radius=3, color="green", fill=True, fill_color="green", popup=str(i)).add_to(map_0)
    return map_0

# Function to build a map displaying the closest nodes to a source node

def BuildAllClosestNodesMap(SourceNode, nodes_routes_values):
    """
    Generates a map that displays nodes connected to a specified source node.

    The source node is marked in blue, while the connected nodes are marked in red.

    Args:
        SourceNode (int): The index of the source node.
        nodes_routes_values (list of tuples): A list of node index pairs representing routes connected to the source.

    Returns:
        folium.Map: A Folium map object with the source node and its connected nodes marked.
    """
    x1, y1 = (float(bounds[2]), float(bounds[0]))
    x2, y2 = (float(bounds[3]), float(bounds[1]))
    center = ((x1 + x2) / 2, (y1 + y2) / 2)
    map_0 = folium.Map(location=center, zoom_start=16)

    for i, j in nodes_routes_values:
        xy = (node['xy'][i][0], node['xy'][i][1])
        if i != SourceNode:
            folium.CircleMarker(xy, radius=3, color="red", fill=True, fill_color="red", popup=str(i)).add_to(map_0)
        else:
            folium.CircleMarker(xy, radius=3, color="blue", fill=True, fill_color="blue", popup=str(i)).add_to(map_0)
    return map_0

# Function to build a map displaying the final path between a source and a destination

def BuildFinalPathMap(i, p):
    """
    Generates a map displaying the path between a source node and a destination node.

    The path is shown as a blue polyline with the starting node marked with an orange circle,
    and the ending node represented with a blue circle marker.

    Args:
        i (int): The index of the destination node.
        p (dict): A dictionary representing the parent relationships of nodes used to trace the path.

    Returns:
        folium.Map: A Folium map object with the path between the source and destination nodes.
    """
    node_cds = [(node['xy'][i][0], node['xy'][i][1])]
    while p[i] != i:
        node_cds.append((node['xy'][p[i]][0], node['xy'][p[i]][1]))
        i = p[i]

    map_0 = folium.Map(location=node_cds[-1], zoom_start=15)

    folium.CircleMarker(node_cds[-1], radius=5, color="blue", fill=True, fill_color="orange").add_to(map_0)
    folium.Marker(node_cds[0], icon=folium.Icon(color="blue", icon="circle", prefix='fa')).add_to(map_0)
    
    folium.PolyLine(locations=node_cds, weight=5, color="blue", opacity="0.75", dash_array=10).add_to(map_0)
    
    return map_0

# Function to open an HTML file in the default web browser

def OpenHTMLMapinBrowser(filename):
    """
    Opens a saved HTML file in the default web browser.

    Args:
        filename (str): The path to the HTML file to be opened.
    """
    url = "file://" + os.path.realpath(filename)
    webbrowser.open(url, new=2)

# Main code to generate and display maps
map1 = BuildAllNodesMap()
map1.save("AllNodeMap.html")
OpenHTMLMapinBrowser("AllNodeMap.html")

while True:
    SourceNode = int(input("Enter a source Node or 0 to exit:"))
    connectivity_matrix = create_connectivity()
    nodes_routes_values, p = plot_routes(SourceNode, connectivity_matrix)
    print(p)

    if not SourceNode:
        print("Map Ended")
        sys.exit(1)

    map2 = BuildAllClosestNodesMap(SourceNode, nodes_routes_values)
    map2.save("AllClosestNodeMap.html")
    OpenHTMLMapinBrowser("AllClosestNodeMap.html")

    while True:
        DestinationNode = int(input("Enter the selected Destination Node from the map or -1 to select a new node or 0 to exit :"))
        
        if DestinationNode == -1:
            break
        
        if not DestinationNode:
            print("Map Ended")
            sys.exit(1)
            
        map3 = BuildFinalPathMap(DestinationNode, p)
        map3.save("OutputMap.html")
        OpenHTMLMapinBrowser("OutputMap.html")
