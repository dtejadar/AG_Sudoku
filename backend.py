from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import random
import math

app = FastAPI()

class SudokuRequest(BaseModel):
    size: int
    fill_percent: float = 0.4

class SudokuSolutionRequest(BaseModel):
    board: list

def is_valid(board, row, col, num):
    size = len(board)
    block_size = int(math.sqrt(size))

    if num in board[row]:
        return False
    if num in board[:, col]:
        return False
    block_row_start = (row // block_size) * block_size
    block_col_start = (col // block_size) * block_size
    block = board[block_row_start:block_row_start + block_size, block_col_start:block_col_start + block_size]
    if num in block:
        return False

    return True

def generate_valid_board(size, fill_percent=0.3):
    board = np.zeros((size, size), dtype=int)

    def backtrack():
        for i in range(size):
            for j in range(size):
                if board[i][j] == 0:
                    nums = list(range(1, size + 1))
                    random.shuffle(nums)
                    for num in nums:
                        if is_valid(board, i, j, num):
                            board[i][j] = num
                            if backtrack():
                                return True
                            board[i][j] = 0
                    return False
        return True

    backtrack()  # Generar un tablero completamente válido
    num_cells_to_fill = int(size * size * fill_percent)
    filled_cells = 0

    # Elimina algunas celdas para crear un Sudoku inicial
    while filled_cells < size * size - num_cells_to_fill:
        row = random.randint(0, size - 1)
        col = random.randint(0, size - 1)
        if board[row][col] != 0:
            board[row][col] = 0
            filled_cells += 1

    return board

def generate_chromosome(board):
    size = len(board)
    chromosome = board.copy()
    for row in range(size):
        empty_cells = np.where(chromosome[row] == 0)[0]
        missing_values = list(set(range(1, size + 1)) - set(chromosome[row]))
        random.shuffle(missing_values)
        for i, cell in enumerate(empty_cells):
            chromosome[row][cell] = missing_values[i]
    return chromosome

def fitness(chromosome):
    size = len(chromosome)
    block_size = int(math.sqrt(size))
    score = 0
    
    for row in chromosome:
        score += size - len(set(row))
    for col in range(size):
        col_values = chromosome[:, col]
        score += size - len(set(col_values))
    for i in range(block_size):
        for j in range(block_size):
            block = chromosome[i * block_size:(i + 1) * block_size, j * block_size:(j + 1) * block_size].flatten()
            score += size - len(set(block))

    if score > 0:
        return score + 1000  # Penalización severa

    return score

def crossover(parent1, parent2):
    child = parent1.copy()
    size = len(parent1)
    for row in range(size):
        if random.random() > 0.5:
            child[row] = parent2[row].copy()
    return child

def mutate(chromosome, initial_board):
    size = len(chromosome)
    row = random.randint(0, size - 1)
    empty_cells = np.where(initial_board[row] == 0)[0]
    if len(empty_cells) > 1:
        i, j = random.sample(list(empty_cells), 2)
        chromosome[row][i], chromosome[row][j] = chromosome[row][j], chromosome[row][i]
    
    # Validar después de la mutación
    for cell in empty_cells:
        num = chromosome[row][cell]
        if not is_valid(chromosome, row, cell, num):
            chromosome[row][cell] = 0  # Revertir si es inválido

def genetic_algorithm(board, population_size=100, generations=1100):
    initial_board = board.copy()  
    population = [generate_chromosome(initial_board) for _ in range(population_size)]
    history = []
    count = 0

    for generation in range(generations):
        population.sort(key=lambda chromo: fitness(chromo))
        history.append(population[0].tolist())

        if fitness(population[0]) == 0 and all(is_valid(population[0], r, c, population[0][r][c]) for r in range(len(board)) for c in range(len(board))):
            return history, population[0]

        next_generation = population[:population_size // 2]
        count += 1

        while len(next_generation) < population_size:
            parent1, parent2 = random.sample(next_generation, 2)
            child = crossover(parent1, parent2)
            if random.random() < 0.1:
                mutate(child, initial_board)
            next_generation.append(child)

        population = next_generation

    return history, population[0], count

@app.post("/generate_board")
async def generate_board(request: SudokuRequest):
    size = request.size
    fill_percent = request.fill_percent
    board = generate_valid_board(size, fill_percent)
    return {"board": board.tolist()}

@app.post("/solve_sudoku")
async def solve_sudoku(request: SudokuSolutionRequest):
    board = request.board
    board_np = np.array(board)
    history, solution, count = genetic_algorithm(board_np)
    return {"history": history, "solution": solution.tolist(), "generations": str(count)}
