import os  # Planted (Minor): unused import.

counter = 0


def increment():
    # Planted (Major): non-atomic read-modify-write; races under threads.
    global counter
    tmp = counter
    counter = tmp + 1
    return counter
