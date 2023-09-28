import re  # Used for interpreting the input file
import time  # Used for measuring the execution time


# Sudoku: Class to keep track of the sudoku board
# id: string as a unique identifier
# board: list of list that contains integers to keep track of the board (0 represent empty squares)
# lookup_rows: list of list that contains integers to keep track of used row values
# lookup_columns: list of list that contains integers to keep track of used row values
# lookup_boxes: list of list that contains integers to keep track of used box values
# lookup_empty: list of tuples that contains integers to keep track of the position of empty values on the board
class Sudoku:
    def __init__(self, id: str, board):
        self.id = id
        self.board = board
        self.lookup_rows = [[], [], [], [], [], [], [], [], []]
        self.lookup_columns = [[], [], [], [], [], [], [], [], []]
        self.lookup_boxes = [[], [], [], [], [], [], [], [], []]
        self.lookup_empty = []

        # Assign values to the lookups based on the values on the board
        for i in range(9):
            for j in range(9):
                value = self.board[i][j]

                # If the board square is empty (i.e. has a value of 0) add its position to the lookup
                if value == 0:
                    self.lookup_empty.append((i, j))

                # If the board square is not empty add its value to the lookup
                # Use the 'floor division' operand to calculate the correct index for the box lookup
                else:
                    self.lookup_rows[i].append(value)
                    self.lookup_columns[j].append(value)
                    self.lookup_boxes[(i // 3) + (j // 3) * 3].append(value)

    def __repr__(self):
        matrix_horizontal_line = "|-------|-------|-------|"
        result = f"ID: {self.id}\n{matrix_horizontal_line}\n"
        # Append to result string row-wise from matrix values
        for i in range(9):
            result += f"| {self.board[i][0]} {self.board[i][1]} {self.board[i][2]} " \
                      f"| {self.board[i][3]} {self.board[i][4]} {self.board[i][5]} " \
                      f"| {self.board[i][6]} {self.board[i][7]} {self.board[i][8]} |\n"
            if i in [2, 5, 8]:
                result += f"{matrix_horizontal_line}\n"
        # Return the string representation of the sudoku board
        return result

    def __str__(self):
        matrix_horizontal_line = "|-------|-------|-------|"
        result = f"ID {self.id}\n{matrix_horizontal_line}\n"
        # Append to result string row-wise from matrix values
        for i in range(9):
            result += f"| {self.board[i][0]} {self.board[i][1]} {self.board[i][2]} " \
                      f"| {self.board[i][3]} {self.board[i][4]} {self.board[i][5]} " \
                      f"| {self.board[i][6]} {self.board[i][7]} {self.board[i][8]} |\n"
            if i in [2, 5, 8]:
                result += f"{matrix_horizontal_line}\n"
        # Return the string representation of the sudoku board
        return result


# Function that interpret the problem specification from "input.txt"
# 1. parameters: dictionary to keep track of parameters (none of them is relevant in our case)
# 2. sudokus: list to keep track of instances of the Sudoku class
def specification(parameters: dict, sudokus: list):
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

        # if line consists of the word "SUDOKU" followed by a whitespace an integer it represents a sudoku game
        elif re.search(r"SUDOKU \d+$", line):
            id = line.rstrip("\n")
            board = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0]]

            # for each row in matrix
            for i in range(9):
                line = file.readline()
                for j in range(9):
                    value = int(line[j])
                    if value != 0:
                        board[i][j] = value

            sudokus.append(Sudoku(id, board))


# Function that solves the sudoku using backtracking
# sudoku: Instance of the Sudoku class to keep track on the current board state
def solve(sudoku: Sudoku):
    # If there are no more empty board squares we have solved the sudoku
    if len(sudoku.lookup_empty) <= 0:
        return True

    # Start looking for possible values for an empty board square using the lookup (row, column, box)
    i, j = sudoku.lookup_empty[0]  # row, column
    k = (i // 3) + (j // 3) * 3  # box
    for value in range(1, 10):
        # If value exists in lookup proceed to the next possible value
        if value in sudoku.lookup_rows[i] or\
           value in sudoku.lookup_columns[j] or\
           value in sudoku.lookup_boxes[k]:
            continue

        # If value do not exist in the lookup add it to the board and update the lookup accordingly
        # Note: use pop(0) and insert(0, (i,j)) when updating the empty square lookup to optimize the execution time
        sudoku.board[i][j] = value
        sudoku.lookup_empty.pop(0)
        sudoku.lookup_rows[i].append(value)
        sudoku.lookup_columns[j].append(value)
        sudoku.lookup_boxes[k].append(value)

        # Recursive call to explore deeper in the search tree
        solved = solve(sudoku)

        # If the branch contained a solution return true
        if solved:
            return True

        # Otherwise, reset the sudoku board and proceed to the next possible value
        # Note: use pop(0) and insert(0, (i,j)) when updating the empty square lookup to optimize the execution time
        sudoku.board[i][j] = 0
        sudoku.lookup_empty.insert(0, (i, j))
        sudoku.lookup_rows[i].remove(value)
        sudoku.lookup_columns[j].remove(value)
        sudoku.lookup_boxes[k].remove(value)

    # If the possible values were depleted for the empty square return false (i.e. branch does not contain a solution)
    return False


# Entry point of the code
if __name__ == "__main__":
    parameters = dict()
    sudokus = []
    specification(parameters, sudokus)

    # Solve the sudokus and measure the required execution time
    start_time = time.time()
    for sudoku in sudokus:
        solve(sudoku)
    end_time = time.time()

    # Display the solved sudoku games
    for sudoku in sudokus:
        print(sudoku)
    print(f"Backtracking execution time.......: {((end_time - start_time) * 10 ** 3):.5f} milliseconds")