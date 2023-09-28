import re  # Used for interpreting the input file
from queue import PriorityQueue  # used for accessing a datastructure that adds elements according to a priority value


# City: class that represent cities (i.e. the vertices in the graph)
# 1. name: string as a unique identifier for the city
# 2. distance_to_goal: integer to keep track of the strait line distance to the goal (i.e. the city Valladolid)
# 3. roads: list to keep track on the instances of the Road class
class City:
    def __init__(self, name: str, distance_to_goal: int, roads: list):
        self.name = name
        self.distance_to_goal = distance_to_goal
        self.roads = roads

    def __repr__(self):
        return f"[{self.name}, {self.distance_to_goal}, {self.roads}]"

    def __str__(self):
        return f"[{self.name}, {self.distance_to_goal}, {self.roads}]"

    def add_road(self, destination, distance):
        self.roads.append(Road(destination, distance))

    def add_distance_to_goal(self, distance_to_goal):
        self.distance_to_goal = distance_to_goal


# Road: class that represent roads between cities (i.e. the edges in the graph)
# 1. destination: string that represent the end destination of the road
# 2. distance: integer that represent the distance to the end destination
class Road:
    def __init__(self, destination: str, distance: int):
        self.destination = destination
        self.distance = distance

    def __repr__(self):
        return f"{self.destination} {self.distance}"

    def __str__(self):
        return f"{self.destination} {self.distance}"


# Node: class to keep track of possible paths
# 1. current_city: the current city
# 2. visited_cities: list to keep track of previously visited cities (to prevent loops in the search)
# 3. traveled_distance: the total distance traveled from the start city to the current city
# 4. heuristic_distance: the heuristic distance (different depending on greedy-first search or A* search)
class Node:
    def __init__(self, current_city: City, visited_cities: list, traveled_distance: int, heuristic_distance):
        self.current_city = current_city
        self.visited_cities = visited_cities
        self.traveled_distance = traveled_distance
        self.heuristic_distance = heuristic_distance

    def __repr__(self):
        return f"Current city.......: {self.current_city}\n" \
               f"Visited cities.....: {self.visited_cities}\n" \
               f"Traveled distance..: {self.traveled_distance}\n" \
               f"Heuristic distance.: {self.heuristic_distance}"


# Function that interpret the problem specification from "input.txt"
# 1. parameters: dictionary to keep track of parameters (none of them is relevant in our case)
# 2. cities: hashmap to keep track of instances of the City class (the city name is the key)
def specification(parameters: dict, cities: dict):
    file = open('input.txt', 'r')
    end_of_file = False
    while not end_of_file:
        # Get next line from file
        line = file.readline()

        # break loop if "end of file" is reached
        if not line:
            end_of_file = True

        # if line contains a semicolon it represent a parameter
        elif re.search(":", line):
            key, value = line.rstrip("\n").split(": ", 2)
            parameters[key] = value

        # if line consists of two alphabetical words followed by an integer it represents a road
        elif re.search(r"^[a-zA-Z]+ [a-zA-Z]+ \d+$", line):
            start_city, end_city, distance = line.rstrip("\n").split(' ', 3)
            # Add the cities to the hashmap if they are not included yet
            if start_city not in cities:
                cities[start_city] = City(start_city, 0, [])
            if end_city not in cities:
                cities[end_city] = City(end_city, 0, [])
            # Add the roads to the cities
            cities[start_city].add_road(end_city, int(distance))
            cities[end_city].add_road(start_city, int(distance))

        # if line consists of one alphabetical word followed by an integer it represents the distance to the goal
        elif re.search(r"^[a-zA-Z]+ \d+$", line):
            city, distance = line.rstrip("\n").split(' ', 2)
            cities[city].add_distance_to_goal(int(distance))


# Function that performs a greedy first search or A* search to find a path to Valladolid
# 1. cities: hashmap to keep track of instances of the City class (the city name is the key)
# 2. start_city_name: string to keep track of starting city in the search
# 3. algorithm: string to keep track on used algorithm (should contain either "A*" or "GFS")
def informed_search(cities: dict, start_city_name: str, algorithm: str):
    if algorithm.upper() != "A*" and algorithm.upper() != "GFS":
        raise Exception(f"Error! \"{algorithm}\" is not an implemented search algorithm.\n"
                        f"Option 1: \"A*\" to use A* search.\n"
                        f"Option 2: \"GFS\" to use greedy-first search.\n")

    # Set the initial location and final destination (heuristic value will not matter in the first node)
    # Unfortunately the destination is hardcoded, since we only know the strait line distance for that city
    end_city_name = "Valladolid"
    node = Node(cities[start_city_name], [start_city_name], 0, 0)

    # Initiate the priority queue (the lowest value will be popped first)
    queue = PriorityQueue()
    queue.put((node.heuristic_distance, node))

    # start search
    while queue.not_empty:
        node = queue.get()[1]
        current_city = node.current_city
        for road in current_city.roads:
            next_city = cities[road.destination]
            if next_city.name not in node.visited_cities:

                # Determine the heuristic value
                heuristic_distance = 0
                if algorithm.upper() == "GFS":
                    heuristic_distance = next_city.distance_to_goal
                else:
                    heuristic_distance = node.traveled_distance + road.distance + next_city.distance_to_goal

                child_node = Node(
                    current_city=next_city,
                    visited_cities=node.visited_cities + [next_city.name],
                    traveled_distance=node.traveled_distance + road.distance,
                    heuristic_distance=heuristic_distance)

                # Return the child node if a path to the destination was found, otherwise continue the search
                if next_city.name == end_city_name:
                    return child_node
                else:
                    queue.put((child_node.heuristic_distance, child_node))

    # Return null if no path to the end city was found
    return None


# Entry point of the code
if __name__ == "__main__":
    parameters = dict()
    cities = dict()
    specification(parameters, cities)

    solution_node = informed_search(cities, "Malaga", "A*")
    print(f"--------------- Search Using A* ---------------\n{solution_node}\n")

    solution_node = informed_search(cities, "Malaga", "GFS")
    print(f"--------------- Search Using GFS ---------------\n{solution_node}\n")