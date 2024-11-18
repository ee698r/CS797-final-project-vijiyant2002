# Map_Navigation_using_Dijkstra_Algorithm

Implementing Dijkstra's Algorithm for shortest path on a map.

## Project Details

Maps - Map is taken/exported from OpenStreetMap while is a free and open service to use.  
       The file exported is in .osm format which is used in the program.
       
Algorithm - For Shortest Path we are using Dijkstra's Algorithm.  
            The connection between nodes are stored in a Nodes x Nodes adjacency Matrix.

## How to Run the Project

There are 2 files:
 - .py File can be compiled and run using ide.
 - .ipynb File open it in jupyter or colab and then compile all the cells.

# OSM Map Processing

## Dependencies
To run this script, the following Python packages and libraries are required:

1. **xmltodict**: For parsing XML data from OSM files.
2. **folium**: For generating and visualizing maps.
3. **numpy**: For creating and managing the connectivity matrix.
4. **webbrowser**: To open generated HTML maps in the default web browser.
5. **os**: For handling file paths.
6. **sys**: For system-specific parameters and functions.

Ensure that you have Python 3 installed as the code is compatible with Python 3.x.

## Installation Instructions
Follow these steps to set up your environment:

1. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv osm-map-env
   source osm-map-env/bin/activate  # On Windows use: osm-map-env\Scripts\activate
   ```

2. **Install the required packages:**
   Run the following commands to install the necessary Python libraries:
   ```bash
   pip install xmltodict folium numpy
   ```

3. **Ensure the standard Python libraries (`webbrowser`, `os`, `sys`) are available:**
   These libraries come with Python by default, so no separate installation is needed.

## Running the Script
1. Place the OSM data file (`mapHSR.osm`) in a directory named `Maps`.
2. Run the Python script:
   ```bash
   python script_name.py
   ```
   Replace `script_name.py` with the name of your Python file.

3. Follow the prompts to interact with the generated maps.

## Note
Ensure that you have an active internet connection when running the script, as `folium` may require access to external map tiles.


## Usage Examples

When Compiled the map is analysed and all the nodes are stored in a list.  
Then an adjacency matrix of node x node is generated and mapped.  
In this at first all the nodes are assumed start point and a path to other nodes are generated.  


Then we ask user for the source node using a map automatically opened in a browser.  
![image](https://user-images.githubusercontent.com/53964760/129915134-56acd5a4-0209-4d7e-8f34-52aeac29196f.png)  
(Nodes are in green dots)  


After that a multiple destination nodes are displayed to the user in the browser.  
![image](https://user-images.githubusercontent.com/53964760/129915357-cfc77779-ddec-4cd1-adf6-b4e1796228ae.png)
(Blue dot is the source and red dots are the possible destination)  


After the user selects a destination, the shortest path is displayed in the map.  
![image](https://user-images.githubusercontent.com/53964760/129915584-7b4f62ea-7da1-4051-9ae8-a86d113d7c62.png)


The whole process is running in the console when the .py file is compiled.  
![image](https://user-images.githubusercontent.com/53964760/129915621-e269a227-e960-4538-8aa3-80231b991b52.png)


Detailed documentation is available [D:\VS code\python files\DijkstraOnMaps-main\docs\build\html\index.html](docs/index.md).