import re  # Used for interpreting the input file
from math import sqrt
import numpy as np
import random  # Used to generate random numbers and performing weighted choices
import matplotlib.pyplot as plt


# Location: Class to keep track of locations to visit
# 1. id: integer value used as a unique identifier
# 2. x: float value to keep track of latitude coordinate
# 3. y: float value to keep track of longitude coordinate
class Location:
    def __init__(self, id: int, x: float, y: float):
        self.id = id
        self.x = x
        self.y = y

    def __repr__(self):
        return f"id: {self.id}, x: {self.x}, y: {self.y}"

    def __str__(self):
        return f"id: {self.id}, x: {self.x}, y: {self.y}"


# Roads: Class to keep track of the distances and pheromones trails between locations
# distances: ndarray to keep track of distances between locations
# pheromones: ndarray to keep track of pheromones trails between locations
# size: integer to keep track of the numbers of location (width and height of the arrays)
class Roads:
    def __init__(self, locations: list, inital_pheromone: float):
        self.size = len(locations)
        self.distances = np.zeros(shape=(self.size, self.size), dtype=float)
        self.pheromones = np.zeros(shape=(self.size, self.size), dtype=float)
        for i in range(self.size):
            for j in range(self.size):
                origin = locations[i]
                destination = locations[j]
                self.distances[i][j] = sqrt((destination.x - origin.x) ** 2 + (destination.y - origin.y) ** 2)
                self.pheromones[i][j] = inital_pheromone

    def __repr__(self):
        return f"id: {self.distances}\n x: {self.pheromones}\n"

    def __str__(self):
        return f"id: {self.distances}\n x: {self.pheromones}\n"


# Organism: Class to keep track of the attributes in the organism
# 1. path: list of integers to keep track on the order locations where visited (the values are indices in the lookup)
# 2. lookup: instance of the Roads class to keep track on pheromones and distances
# 3. travel_distance:  value to keep track of the summarized travel distance of the path
class Organism:
    def __init__(self, path: list, lookup: Roads, travel_distance: float):
        self.path = path
        self.lookup = lookup
        self.travel_distance = travel_distance

    def __repr__(self):
        return f"path: {self.path}, travel distance: {self.travel_distance}\n"

    def __str__(self):
        return f"path: {self.path}, travel distance: {self.travel_distance}\n"

    def get_location(self):
        return self.path[-1]

    def chose_destination(self, alpha, beta):
        # Calculate the weights
        weights = []
        destinations = []
        origin = self.get_location()
        for destination in range(self.lookup.size):
            if destination not in self.path:
                pheromone = self.lookup.pheromones[origin][destination]
                distance = self.lookup.distances[origin][destination]
                weight = pheromone ** alpha * ((1 / distance) ** beta)
                weights.append(weight)
                destinations.append(destination)

        # If all destinations have already been visited return to start location
        if len(destinations) == 0:
            return 0

        # Randomly select a destination based on their probability.
        # (element_probability = element_weight / sum_of_all_weights)
        next_destination = random.choices(population=destinations, weights=weights, k=1)[0]
        return next_destination

    def travel(self, alpha, beta):
        destination = self.chose_destination(alpha, beta)
        origin = self.get_location()
        self.travel_distance += self.lookup.distances[origin][destination]
        self.path.append(destination)


# Function that returns a population with randomized paths that visits all locations, but begins and ends at location 1
# 1. lookup: instance of the Roads class to keep track on pheromones and distances
# 2. population_size: is an integer value that determine the size of the population
def create_population(lookup: Roads, population_size: int):
    population = []
    for i in range(population_size):
        population.append(Organism([0], lookup, 0.0))
    return population


# Function that sort the population according to the organisms' fitness value
# 1. population: list of instances of the Organism class
def sort_population(population: list):
    population.sort(key=lambda organism: organism.travel_distance, reverse=False)


# Function that emit pheromone trails (decision weights) between the locations
# 1. population: list of instances of the Organism class
# 2. lookup: instance of the Roads class to keep track on pheromones and distances
# 3. pheromone_persistence: float value that determines how long the pheromone will last before evaporating away
def pheromones_update(population: list, lookup: Roads, pheromone_persistence: float):
    lookup.pheromones = lookup.pheromones * pheromone_persistence

    for organism in population:
        for i in range(1, len(organism.path)):
            origin = organism.path[i - 1]
            destination = organism.path[i]
            lookup.pheromones[origin][destination] += 1 / organism.travel_distance
            lookup.pheromones[destination][origin] += 1 / organism.travel_distance


# Function that interpret the problem specification from "input.txt"
# 1. parameters: dictionary to keep track of parameters (none of them is relevant in our case)
# 2. locations: list of instances of the Location class to keep track of the locations that should be visited
def specification(parameters: dict, locations: list):
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

        # if line consists of an integer followed by an
        elif re.search(r"^\d+ \d+.\d+ \d+.\d+$", line):
            id, x, y = line.rstrip("\n").split(" ", 3)
            locations.append(Location(int(id), float(x), float(y)))


# Display the progress graph
def progress_graph(progress: list):
    plt.rcParams.update({'font.size': 22})
    plt.plot(progress)
    plt.xlabel('Generation')
    plt.ylabel('Distance')
    plt.title("Traveling Salesman Problem with Ant Colony Optimization")
    plt.show()


# Display the path graph
def path_graph(path: list, locations: list):
    plt.rcParams.update({'font.size': 22})
    fig, ax = plt.subplots()
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Traveling Salesman Problem with Ant Colony Optimization")

    x_axis = []
    y_axis = []
    labels = []
    for destination in path:
        x_axis.append(locations[destination].x)
        y_axis.append(locations[destination].y)
        labels.append(locations[destination].id)

    # Add dots that represent locations to the graph
    ax.plot(x_axis, y_axis, color="red")
    ax.scatter(x_axis, y_axis, s=15, color="red")

    # Add a label for each location in the diagram
    # for i in range(len(labels)):
    #     ax.text(x_axis[i] + 0.2, y_axis[i] + 0.2, labels[i], fontsize=12)

    plt.show()


# Entry point of the code
if __name__ == "__main__":
    parameters = dict()
    locations = []
    specification(parameters, locations)

    # Ant Colony Optimization Parameters
    alpha = 1.3
    beta = 1.6
    pheromone_persistence = 0.85
    population_size = 250
    iterations = 200

    # Create the lookup for the roads and their initial pheromones values
    roads = Roads(locations, 1)

    progress = []
    best = None
    for iteration in range(1, iterations + 1):
        # Create a new population and let them travel to all locations and then back to the starting location
        population = create_population(roads, population_size)
        for organism in population:
            for location in locations:
                organism.travel(alpha, beta)

        # Sort the organisms in the population in based on the travel distance
        sort_population(population)
        progress.append(population[0].travel_distance)
        if best is None or population[0].travel_distance < best.travel_distance:
            best = population[0]
        print(f"Iteration: {iteration}, Travel Distance: {population[0].travel_distance}")

        # Emit pheromones
        pheromones_update(population, roads, pheromone_persistence)

    # Display the result
    progress_graph(progress)
    path_graph(best.path, locations)
