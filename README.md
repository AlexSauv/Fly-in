*This project has been created as part of the 42 curriculum by Alsauvan*

# Fly-In: Multi-Drone Routing Optimization

## 📝 Description

The purpose of this project is to understand time-dependent algorithms and computational complexity through the simulation of a drone fleet navigating diverse maps with structural restrictions. 

Drones operate simultaneously in discrete turns, with the ability to either move to an adjacent zone or strategically wait in place. The core challenge lies in designing an intelligent routing system capable of solving spatial conflicts, respecting strict capacity constraints (both for zones and connections), and dynamically discovering alternative paths. The ultimate goal is to optimize the throughput of the fleet to complete the simulation in the fewest possible turns.

### Algorithm Choices & Implementation Strategy

#### Djikstra Time-Dependant

The pathfinding core relies on a customized Time-Dependent Dijkstra Algorithm engineered to navigate spatial-temporal constraints without collisions.

#### 1.Space-Time calculation

For each drones the pathfinder will be able to evaluate capacity of a target hub during each turn. To handle dynamic occupancy my algorithm will register into a dict: (hub_name, the current turn) and the drone occupancy. 

#### 2. Conflict Resolution & Capacity Checking

##### During the plannification the algorithm will tracks enforce constraints to recalculate paths for drones:

- ##### Zone Capacities: Drone actions will evaluate the capacity of the target hub. At the exact turn of their planned arrival (next_turn). If the reservation count reaches the limit, the path is discarded.

- ##### Connection Capacities: For links restricted by max_link_capacity, the algorithm continuously checks the availability across the entire duration of the transit (crucial for RESTRICTED zones which require a 2-turn movement cost).

- ##### Strategie Waiting: Drones can choose to stay in their current hub for 1 turn (next_turn_stay = curr_turn + 1) if paths ahead are bottlenecked, provided the current hub's capacity permits it.

#### 3. Queue Priority & Safety Mechanics

- ##### Priorities: Priority cost favor PRIORITY zones (cost 0.5 instead 1.0), driving the fly toward optimal path.

- ##### Determination Sorting: The heapq multi-tuple structure uses an internal unique counter flag to prevent TypeError exceptions when evaluatiing identical priority paths 

- ##### Infinite Loop Protection: A safety benchmark limit_turn (scaled linearly to nb_drones * 5) automatically terminates deadlocked or non-viable exploration branches.


## 🛠️ Instructions

### Prerequisites
Before running the project, ensure you have Python 3.10 or later installed. It must use a virtual environment (`venv`).

### Installation & Setup
The program has to be execute with the Makefile, in order to work properly it has to install packages with make install, it should activate the virtual environment if it is not the case and then can be run with two differents possibility: first with - make run, the second with - python3 fly-in.py file_name_map.txt

To install all required dependencies automatically, run:
```bash 
make install
```

### Execution
```bash 
make run
```
```bash 
python3 fly-in.py file_name_map.txt
```



## 📚 Resources

#### *For algorithm understanding*
- https://www.geeksforgeeks.org/python/python-program-for-dijkstras-shortest-path-algorithm-greedy-algo-7/
- https://www.datacamp.com/tutorial/dijkstra-algorithm-in-python
- https://www.w3schools.com/dsa/dsa_algo_graphs_dijkstra.php
- https://major-prepa.com/python/algorithme-dijkstra/
- Youtube tutorial videos

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
- Last resort for debugging graph rendering
- Used for understanding deeper few concepts


• A “Description” section that clearly presents the project, including its goal and a
brief overview.
• An “Instructions” section containing any relevant information about compilation,
installation, and/or execution.
• A “Resources” section listing classic references related to the topic (documentation, articles, tutorials, etc.), as well as a description of how AI was used —
specifying for which tasks and which parts of the project.
➠ Additional sections may be required depending on the project (e.g., usage
examples, feature list, technical choices, etc.).
Any required additions will be explicitly listed below.
• A detailed description of your algorithm choices and implementation strategy must
also be included.
• Documentation of the visual representation features and how they enhance the user
experience.
Your README must be written in English.
