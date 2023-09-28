import re  # Used for interpreting the input file
from copy import copy
from math import sqrt  # Used for calculating distances between locations
import matplotlib.pyplot as plt  # Used to graphically present the progress of the algorithm
import random  # Used to generate random numbers


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


# Organism: Class to keep track of the attributes in the organism
# 1. path: list of integers to keep track on the order locations where visited (the values are indices in the lookup)
# 2. lookup: list of instances of the Location class to keep track of locations
# 3. fitness: float value to keep track of the summarized travel distance of the path
class Organism:
    def __init__(self, path: list, lookup: list):
        self.path = path
        self.lookup = lookup
        self.fitness = 0
        self.evaluate()

    # Get location from the lookup
    def get_location(self, index: int):
        return self.lookup[self.path[index]]

    # Choose a random section of partners path and combine it with own path
    def crossover(self, partner):
        start = random.randint(1, len(self.path) - 2)
        end = random.randint(start, len(self.path) - 1)
        section1 = partner.path[start:end]
        section2 = [i for i in self.path if i not in section1]
        self.path = section2[:start] + section1 + section2[start:]

    # Choose a random section of own path and reverse the order of the elements in that section
    def mutate(self):
        start = random.randint(1, len(self.path) - 2)
        end = random.randint(start, len(self.path) - 1)
        self.path = self.path[:start] + self.path[end - 1:start - 1:-1] + self.path[end:]

    # Calculate the fitness value (the travel distance of the path)
    def evaluate(self):
        self.fitness = 0
        for i in range(1, len(self.path)):
            origin = self.get_location(i - 1)
            destination = self.get_location(i)
            distance = sqrt((destination.x - origin.x) ** 2 + (destination.y - origin.y) ** 2)
            self.fitness += distance

    def __repr__(self):
        return f"path: {self.path}, fitness: {self.fitness}\n"

    def __str__(self):
        return f"path: {self.path}, fitness: {self.fitness}\n"


# Function that returns a population with randomized paths that visits all locations, but begins and ends at location 1
# 1. lookup: list of instances of the Location class to keep track of locations
# 2. population_size: integer value that determine the size of the population
def create_population(lookup: list, population_size: int):
    indices = list(range(1, len(lookup)))
    population = []
    for i in range(population_size):
        path = copy(indices)
        random.shuffle(path)
        path = [0] + path + [0]
        population.append(Organism(path, lookup))

    return population


# Function that sort the population according to the organisms' fitness value
# 1. population: list of instances of the Organism class
def sort_population(population: list):
    population.sort(key=lambda organism: organism.fitness, reverse=False)


# Function that evolve the population using elitism, crossovers, and mutations
# 1. population: list of instances of the Organism class
# 2. elitism_percentage: float value to determine the percentage of the population that will be unaltered
# 3. mutation_percentage: float value that determine the percentage of a mutation occurring
def evolve_population(population: list, elitism_percentage: float, mutation_percentage: float):
    n = int(len(population) * elitism_percentage)
    population_elitism = population[0:n]
    population_crossover = population[n:]

    for organism in population_crossover:
        partner = population_elitism[random.randint(0, n-1)]
        organism.crossover(partner)
        if random.random() <= mutation_percentage:
            organism.mutate()
        organism.evaluate()

    population = population_elitism + population_crossover


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


# Function that display the progress graph
# 1. progress: list with float values that represent the best fitness (travel distance) of the corresponding generation
def progress_graph(progress: list):
    plt.rcParams.update({'font.size': 22})
    plt.plot(progress)
    plt.xlabel('Generation')
    plt.ylabel('Distance')
    plt.title("Traveling Salesman Problem with Genetic algorithm")
    plt.show()


# Function that display the path graph
# 1. path: list of integers to keep track on the order locations where visited (the values are indices in the lookup)
# 2. lookup: list of instances of the Location class to keep track of locations
def path_graph(path: list, locations: list):
    plt.rcParams.update({'font.size': 22})

    fig, ax = plt.subplots()
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Traveling Salesman Problem with Genetic algorithm")

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

    # Genetic Algorithm Parameters
    population_size = 250
    elitism_percentage = 0.02

    mutation_percentage = 0.15
    generations = 200

    # Create an initial population with random values
    population = create_population(locations, population_size)
    sort_population(population)

    # Find solution using a genetic algorithm and keep track of
    best = population[0]
    progress = [best.fitness]
    print(f"Generation: {0}, Fitness: {best.fitness}")
    for generation in range(1, generations+1):
        # Evolve the population (elitism, crossovers, and mutations)
        evolve_population(population, elitism_percentage, mutation_percentage)

        # Sort the population according to the organisms' fitness values
        sort_population(population)

        # Save the best in the generation
        best = population[0]
        progress.append(best.fitness)

        # Print the generational progress
        if generation % 10 == 0:
            print(f"Generation: {generation}, Fitness: {best.fitness}")
    print(best)

    # Display the result
    progress_graph(progress)
    path_graph(best.path, locations)
