#!/usr/bin/python           # This is server.py file

import socket  # Import socket module
import numpy as np
import time
from multiprocessing.pool import ThreadPool
import copy
import os


def receive(socket):
    msg = ''.encode()  # type: str

    try:
        data = socket.recv(1024)  # type: object
        msg += data
    except:
        pass
    return msg.decode()


def send(socket, msg):
    socket.sendall(msg.encode())


# Function that get the non-empty pits of the current player
# 1. board: list of integers that represents the current state of the mancala board
# 2. player_turn: integer that to keep track of the current player
def get_valid_pits(board: list[int], player_turn: int):
    pits = []
    if player_turn == 1:
        for i in range(0, 6):
            if board[i] != 0:
                pits.append(i)
    else:
        for i in range(7, 13):
            if board[i] != 0:
                pits.append(i)
    return pits


# Function that returns the opposite players turn
# 1. player_turn: integer that to keep track of the current player
def switch_player_turn(player_turn):
    return 2 if player_turn == 1 else 1


# Function that capture the stones of both the pit and opposite pit
# 1. board: list of integers that represents the current state of the mancala board
# 2. pit: integer that keeps track of the pit that initiated the capture of the opposite pit
# 3. player_turn: integer that to keep track of the current player
def capture_opposite_pit(board: list[int], pit: int, player_turn: int):
    opposite_pit = 12 - pit
    if player_turn == 1:
        board[6] += board[opposite_pit] + board[pit]
    else:
        board[13] += board[opposite_pit] + board[pit]
    board[opposite_pit], board[pit] = 0, 0


# Function that takes the stones on the side that is not empty and places them in the corresponding players store
# 1. board: list of integers that represents the current state of the mancala board
def capture_non_empty_side(board: list[int]):
    stones1 = sum(board[0:6])
    stones2 = sum(board[7:13])
    if stones1 == 0:
        board[13] += stones2
        for i in range(7, 13):
            board[i] = 0
    elif stones2 == 0:
        board[6] += stones1
        for i in range(0, 6):
            board[i] = 0


# Function that performs a move and returns the updated mancala board and player turn as a tuple
# 1. board: list of integers that represents the current state of the mancala board
# 2. pit: integer that keeps track of the pit that initiates the move
# 3. player_turn: integer that to keep track of the current player
def perform_move(board: list[int], pit: int, player_turn: int):
    updated_board = copy.deepcopy(board)
    stones = updated_board[pit]
    updated_board[pit] = 0

    # Distribute stones in the pit
    previous_pit = pit
    while stones > 0:
        current_pit = (previous_pit + 1) % len(board)
        if player_turn == 1 and current_pit == 13:
            current_pit = 0
        elif player_turn == 2 and current_pit == 6:
            current_pit = 7
        updated_board[current_pit] += 1
        previous_pit = current_pit
        stones -= 1

    # Special case when last stone is placed in an empty pit on the current player's side (see Mancala rules)
    if last_stone_in_empty_pit(updated_board, current_pit, player_turn):
        capture_opposite_pit(updated_board, current_pit, player_turn)

    # Special case when one of the player's side lacks stone in any of its pits (see Mancala rules)
    if end_of_game(updated_board):
        capture_non_empty_side(updated_board)

    # special case when last stone is placed in the current player's store (see Mancala rules)
    if last_stone_in_store(current_pit, player_turn):
        return updated_board, player_turn
    else:
        return updated_board, switch_player_turn(player_turn)


# Function that checks if a pit belongs to the current player
# 1. pit: integer that keeps track of the pit
# 2. player_turn: integer that to keep track of the current player
def pit_owner(pit: int, player_turn: int):
    return (player_turn == 1 and 0 <= pit <= 5) or (player_turn == 2 and 7 <= pit <= 12)


# Function that checks if the board fulfils the end condition of the game
# 1. board: list of integers that represents the current state of the mancala board
def end_of_game(board: list[int]):
    return sum(board[0:6]) == 0 or sum(board[7:13]) == 0


# Function that checks if the last stone was placed in the store of the current player
# 1. pit: integer that keeps track of the pit where the stone was placed
# 2. player_turn: integer that to keep track of the current player
def last_stone_in_store(pit: int, player_turn: int):
    return (player_turn == 1 and pit == 6) or (player_turn == 2 and pit == 13)


# Function that checks if the last stone was placed in an empty pit that belongs to the current player
# 1. board: list of integers that represents the current state of the mancala board
# 2. pit: integer that keeps track of the pit where the stone was placed
# 3. player_turn: integer that to keep track of the current player
def last_stone_in_empty_pit(board: list[int], pit: int, player_turn: int):
    return board[pit] == 1 and pit_owner(pit, player_turn)


# Function that evaluate the benefit of mancala board from the perspective of the intelligent bot
# 1. board: list of integers that represents the current state of the mancala board
# 2. player: bool that keeps track if it is the intelligent bot or its opponent that is 'playing' during the evaluation
# 3. player_turn: integer that to keep track of the current player
def utility_evaluation(board: list[int], player: bool, player_turn: int):
    utility = 0
    pits1 = sum(board[0:6])
    pits2 = sum(board[7:13])
    store1 = board[6]
    store2 = board[13]

    if player_turn == 1:
        utility += (end_of_game(board) and store1 > store2) * 1000
        utility += (store1 - store2) * 100
        utility += (pits1 - pits2) * 10

    else:
        utility += (end_of_game(board) and store2 > store1) * 1000
        utility += (store2 - store1) * 100
        utility += (pits2 - pits1) * 10

    return utility if player else -utility


# Function that search for the most beneficial move from the perspective of the intelligent bot using a minmax algorithm
# 1. board: list of integers that represents the current state of the mancala board
# 2. depth: integer that keeps track of the depth of the search
# 3. alpha: float value used for pruning to reduce the size of the search
# 4. beta: float value used for pruning to reduce the size of the search
# 5. player: bool that keeps track if it is the intelligent bot or its opponent that is 'playing' during the search
# 6. player_turn: integer that to keep track of the current player
def min_max(board: list[int], depth: int, alpha: float, beta: float, player: bool, player_turn: int):
    # The base case of the recursive function has been meet, return an evaluation
    if end_of_game(board) or depth == 0:
        return utility_evaluation(board, player, player_turn)

    # Find the most beneficial move from the player's perspective, use alpha beta pruning to limit the search
    elif player:
        maximum_utility = float('-inf')
        for pit in get_valid_pits(board, player_turn):
            (updated_board, updated_player_turn) = perform_move(board, int(pit), player_turn)
            updated_player = player_turn == updated_player_turn
            utility = min_max(updated_board, depth - 1, alpha, beta, updated_player, updated_player_turn)

            # Get the most beneficial move from the topmost call in the recursive function
            # Note that 'maximum_depth' is assigned outside the function and that 'move' will be globally accessible
            if depth == maximum_depth and utility > maximum_utility:
                global move
                move = pit

            maximum_utility = max(maximum_utility, utility)
            alpha = max(alpha, utility)
            if beta <= alpha:
                break
        return maximum_utility

    # Find the least beneficial move from the player's perspective, use alpha beta pruning to limit the search
    else:
        minimum_utility = float('inf')
        for pit in get_valid_pits(board, player_turn):
            (updated_board, updated_player_turn) = perform_move(board, int(pit), player_turn)
            updated_player = player_turn != updated_player_turn
            utility = min_max(updated_board, depth - 1, alpha, beta, updated_player, updated_player_turn)

            minimum_utility = min(minimum_utility, utility)
            beta = min(beta, utility)
            if beta <= alpha:
                break
        return minimum_utility


# VARIABLES
playerName = 'viking_forsman'
host = '127.0.0.1'
port = 30000  # Reserve a port for your service.
s = socket.socket()  # Create a socket object
pool = ThreadPool(processes=1)
gameEnd = False
MAX_RESPONSE_TIME = 5

print('The player: ' + playerName + ' starts!')
s.connect((host, port))
print('The player: ' + playerName + ' connected!')

while not gameEnd:

    asyncResult = pool.apply_async(receive, (s,))
    startTime = time.time()
    currentTime = 0
    received = 0
    data = []
    while received == 0 and currentTime < MAX_RESPONSE_TIME:
        if asyncResult.ready():
            data = asyncResult.get()
            received = 1
        currentTime = time.time() - startTime

    if received == 0:
        print('No response in ' + str(MAX_RESPONSE_TIME) + ' sec')
        gameEnd = 1

    if data == 'N':
        send(s, playerName)

    if data == 'E':
        gameEnd = 1

    if len(data) > 1:

        # Read the board and player turn
        board = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        playerTurn = int(data[0])
        i = 0
        j = 1
        while i <= 13:
            board[i] = int(data[j]) * 10 + int(data[j + 1])
            i += 1
            j += 2

        # Using your intelligent bot, assign a move to "move"
        #
        # example: move = '1';  Possible moves from '1' to '6' if the game's rules allows those moves.
        # TODO: Change this
        ################
        maximum_depth = 3
        min_max(board, maximum_depth, float('-inf'), float('inf'), True, playerTurn)
        # Update move variable to correspond with the server's value system (1 to 6 regardless of side)
        move = (move + 1) % 7
        ################
        send(s, str(move))
