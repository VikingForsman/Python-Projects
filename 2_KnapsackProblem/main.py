import re  # Used for interpreting the input file
import time  # Used for measuring the execution time
import tracemalloc  # Used for measuring the peak memory usage
from collections import deque  # used for simulating a stack


# Item: class that represent items
# 1. id: integer as a unique identifier for the item
# 2. benefit: integer to keep track of the item's benefit
# 3. weight:  integer to keep track of the item's weight
class Item:
    def __init__(self, id: int, benefit: int, weight: int):
        self.id = id
        self.benefit = benefit
        self.weight = weight

    def __repr__(self):
        return f"[i:{self.id} b:{self.benefit} w:{self.weight}]"

    def __str__(self):
        return f"[i:{self.id} b:{self.benefit} w:{self.weight}]"


# Node: class that represent possible solutions
# 1. chosen_items: integer list to keep track on the items in knapsack (uses item id)
# 2. total_benefit: integer to keep track of the summarized benefit of all chosen items
# 3. total_weight: integer to keep track of the summarized weight of all chosen items
# 4. depth: integer to keep track of current depth in the search (tree structure)
class Node:
    def __init__(self, chosen_items: list, total_benefit: int, total_weight: int, depth: int):
        self.chosen_items = chosen_items
        self.total_benefit = total_benefit
        self.total_weight = total_weight
        self.depth = depth

    def __repr__(self):
        return f"Chosen items.....: {self.chosen_items}\n" \
               f"Total Benefit....: {self.total_benefit}\n" \
               f"Total Weight.....: {self.total_weight}\n" \
               f"Depth............: {self.depth}\n"

    def __str__(self):
        return f"Chosen items.....: {self.chosen_items}\n" \
               f"Total Benefit....: {self.total_benefit}\n" \
               f"Total Weight.....: {self.total_weight}\n" \
               f"Depth............: {self.depth}\n"


# Function that interpret the problem specification from "input.txt"
# 1. parameters: dictionary to keep track of parameters (only "MAXIMUM WEIGHT" is relevant in our case)
# 2. items: list to keep track of instances of the Item class
def specification(parameters: dict, items: list):
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

        # if line consists of three integer values separated by spaces it represent an item
        elif re.search(r"^\d+ \d+ \d+$", line):
            id, benefit, weight = line.rstrip("\n").split(' ', 3)
            items.append(Item(int(id), int(benefit), int(weight)))


# Function that finds a solution using either breadth-first search (BFS) or depth-first search (DFS)
# 1. items: list to keep track of instances of the Item class
# 2. max_weight: integer to keep track on the maximum weight of the knapsack
# 3. algorithm: string to keep track on used algorithm (should contain either "BFS" or "DFS")
def uninformed_search(items: list, max_weight: int, algorithm: str):
    # Choose which algorithm to use
    if algorithm.upper() != "BFS" and algorithm.upper() != "DFS":
        raise Exception(f"Error! \"{algorithm}\" is not an implemented search algorithm.\n"
                        f"Option 1: \"BFS\" to use breadth-first search.\n"
                        f"Option 2: \"DFS\" to use depth-first search.\n")

    # Node to keep track of the solution with the best benefit value, start with empty an empty knapsack
    node_solution = Node([], 0, 0, 0)

    # Node queue/stack to keep track of nodes to search, start with empty an empty knapsack
    nodes = deque()
    nodes.append(node_solution)

    # Begin search
    while len(nodes) > 0:
        # Explore the next node from the stack (DFS) or queue (BFS)
        if algorithm.upper() == "BFS":
            node = nodes.popleft()  # FIFO: append() increment on the right side, and popleft() remove left side
        else:
            node = nodes.pop()  # LIFO: append() increment on the right side, and pop() removes on the right side

        # Update solution node if the benefit of the current node is higher
        # Choose solution with the least weight if they have equal benefit
        if node.total_benefit == node_solution.total_benefit and node.total_weight < node_solution.total_weight:
            node_solution = node
        elif node.total_benefit > node_solution.total_benefit:
            node_solution = node

        # Continue search if there are still more items to potentially put in the knapsack
        if node.depth < len(items):
            item = items[node.depth]
            # Scenario 1: take item
            child_left = Node(
                chosen_items=node.chosen_items + [item.id],
                total_benefit=node.total_benefit + item.benefit,
                total_weight=node.total_weight + item.weight,
                depth=node.depth + 1)

            # Scenario 2: do not take item
            child_right = Node(
                chosen_items=node.chosen_items + [],
                total_benefit=node.total_benefit,
                total_weight=node.total_weight,
                depth=node.depth + 1)

            # Only append the children if their total weight is lower or equal to the knapsack's max weight
            if child_left.total_weight <= max_weight:
                nodes.append(child_left)
                nodes.append(child_right)
            else:
                nodes.append(child_right)

    return node_solution


# Entry point of the code
if __name__ == "__main__":
    parameters = dict()
    items = []
    specification(parameters, items)

    # Measure memory usage and execution time for breadth-first search
    start_time = time.time()
    tracemalloc.start()
    solution_node = uninformed_search(items, int(parameters["MAXIMUM WEIGHT"]), "BFS")
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    end_time = time.time()
    print(f"Breadth-first search execution time.......: {((end_time - start_time) * 10 ** 3):.5f} milliseconds")
    print(f"Breadth-first search peak memory usage....: {(peak_memory / 10 ** 3):.5f} kilobytes")
    print(solution_node)

    # Measure memory usage and execution time for depth-first search
    start_time = time.time()
    tracemalloc.start()
    solution_node = uninformed_search(items, int(parameters["MAXIMUM WEIGHT"]), "DFS")
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    end_time = time.time()
    print(f"Depth-first search execution time.......: {((end_time - start_time) * 10 ** 3):.5f} milliseconds")
    print(f"Depth-first search peak memory usage....: {(peak_memory / 10 ** 3):.5f} kilobytes")
    print(solution_node)
