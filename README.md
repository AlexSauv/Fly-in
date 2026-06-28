*This project has been created as part of the 42 curriculum by Alsauvan*

# Fly-In: Multi-Drone Routing Optimization

## 📝 Description

The **Fly-In** project is an optimization and simulation platform designed to coordinate a fleet of autonomous drones across a network of connected hubs. Operating in a discrete, turn-based environment, multiple drones must safely travel from a single starting base (`start_hub`) to a final destination (`end_hub`) while minimizing the total number of simulation turns.

The core difficulty lies in dynamic conflict resolution and strict constraint adherence. The routing framework manages:

**Spatial-Temporal Constraints:** Ensuring that zone capacities (`max_drones`) are never breached during any specific turn.
- **Connection Traffic Limits:** Throttling the concurrent flow of drones on standard edges (`max_link_capacity`).
- **Heterogeneous Zone Costs:** Dynamically adjusting path costs depending on terrain types (Normal: 1 turn, Restricted: 2 turns, Priority: 1 turn but prioritized cost (0.5 weight), Blocked: Inaccessible).

### Algorithm Explanation & Implementation Strategy

#### Djikstra Time-Dependant

The pathfinding core relies on a customized Time-Dependent Dijkstra Algorithm engineered to navigate spatial-temporal constraints without collisions. The algorithm will look up multiple hypothetical paths possible and sort them depending
on cost turn and priorities with heapq, it will exclude dead ends paths through the programs and look for hypothetical shortest paths unvisited until the end hub.

#### 1.Space-Time calculation
Standard shortest-path algorithms are blind to temporal conflicts. To prevent collisions before drones take off, our pathfinder implements a custom Time-Dependent Dijkstra depending on reservation dictionnaries for hubs and connections for each turns.

- Dynamic Occupancy Look-up: Centralized dictionaries (planned_hub and planned_link) record precisely how many units are scheduled on any zone or connection during an exact time-step.

#### 2. Conflict Resolution & Capacity Checking

- Simultaneous Actions: Drones leaving an overloaded hub free up slot capacity on that exact turn, enabling oncoming drones to transition smoothly into the newly vacated spot.

- Strategic Waiting: If all forward paths are saturated, the Dijkstra algorithm evaluates a "stay-in-place" virtual edge, verifying if the current hub can let stay the drone for an extra turn until bottlenecks clear out.

- Restricted Zone Overheads: Moving into a restricted zone costs 2 turns. The algorithm reserves transit windows ahead of time, ensuring destination slots are booked for turn + 2 to avoid illegal middle-of-the-link standstills.

- Priorities: Priority cost favor PRIORITY zones (cost 0.5 instead 1.0), driving the fly toward optimal path and avoid unnecessary moves.

- Infinite Loop Protection: A safety benchmark limit_turn (scaled linearly to nb_drones * 5) automatically terminates deadlocked or non-viable exploration branches.

### Visual Representation
The simulation features a rich graphical user interface built via the Arcade framework. It enhances peer evaluation by providing:

Real-time sprite indicators showing drone positions, transit vectors, and hub queues.

Dynamic color-coding maps mirroring custom metadata criteria loaded from map files.

Automated generation of a conforming output_file.txt log sequence detailing step-by-step turn mechanics.

#### Output_file example
```bash
D1-waypoint1 
D1-waypoint2, D2-waypoint1 
D1-goal, D2-waypoint2 
D2-goal 
```

## 🛠️ Instructions

### Prerequisites
Before running the project, ensure you have Python 3.10 or later installed. It must use a virtual environment (`venv`).

### Installation & Setup
To isolate dependencies and install all depencies, run:

```bash 
make install
```
This command initializes a local virtual environment (./venv) and pulls down required libraries such as pydantic, arcade, flake8, and mypy.

### Execution
To run the default simulation layout from the first map (01_linear_path.txt), use:
```bash 
make run ARGS=file_name_map.txt
```
To test custom configurations or harder maps, pass the file path via the ARGS parameter:
```bash 
python3 fly-in.py file_name_map.txt
```

### Tools

To delete pycache and mypy_cache

```bash 
make clean
```

To delete also the environment
```bash 
make clean-strict
```


To run mypy and flake8 use:

```bash 
make lint
```

or mypy and flake8 strict use:

```bash 
make lint-strict
```


## 📚 Resources

#### *For algorithm understanding*
- https://www.geeksforgeeks.org/python/python-program-for-dijkstras-shortest-path-algorithm-greedy-algo-7/
- https://www.datacamp.com/tutorial/dijkstra-algorithm-in-python
- https://www.w3schools.com/dsa/dsa_algo_graphs_dijkstra.php
- https://major-prepa.com/python/algorithme-dijkstra/
- https://ahmedhanibrahim.wordpress.com/2016/04/15/solving-time-dependent-graph-using-modified-dijkstra-algorithm/
- [Youtube tutorial videos](https://www.youtube.com/watch?v=EaphyqKU4PQ)

#### *For Graphic Representation*
- https://api.arcade.academy/en/3.3.3/example_code/sprite_collect_coins_background.html#sprite-collect-coins-background
- https://api.arcade.academy/en/stable/example_code/sprite_follow_simple.html#sprite-follow-simple
- https://api.arcade.academy/en/3.3.2/api_docs/resources.html
- stackoverflow.com
- Youtube tutorial videos

#### *For OOP reminder*
- https://pydantic.dev/docs/validation/2.3/usage/types/number_types/
- GeekForGeeks
- W3Schools

#### *How AI  was used*
- For readme rendering and english rephrases
- Used for understanding deeper few concepts
