import time
from functools import partial
from random import choices, randint, randrange, random

from algorithms.maze.dfs_solve import find_exit_bfs
from algorithms.maze.helpers import get_coords_for_field, get_next_move_coords, is_dead_end, distance, clear_folder, map_coords_to_moves
from algorithms.maze.types import *
from algorithms.maze.variables import MUTATIONS, MAZE, SOLUTION_FOUND_FITNESS_VALUE, DEAD_END_FITNESS_VALUE, STEPS_MULTIPLIER, NEGATIVE_FINISH_MULTIPLIER, POPULATION_SIZE, MAX_MOVES, GENERATIONS
from algorithms.maze.visualize import visualize_maze


def generate_genome(length: int) -> Genome:
    return choices([Move.BOTTOM, Move.TOP, Move.RIGHT, Move.LEFT], k=length)


def generate_population(size: int, genome_length: int) -> Population:
    return [generate_genome(genome_length) for _ in range(size)]


# SELECTION FUNCTION
# Selects a pair of 2 solutions that will be the parents of 2 new solution of next generation
def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return choices(
        k=2,  # returns a list of 2 items
        population=population,  # from population
        weights=[fitness_func(gnome) for gnome in population],  # solutions with higher fitness should have higher probability of being chosen
    )


# CROSSOVER FUNCTION
# Sample input [1, 1], [0, 0]
# Sample output [1, 0], [0, 1]
# or
# Sample input [1, 1, 1, 1, 1], [0, 0 ,0 ,0, 0]
# Sample output [1, 1, 1, 1, 0], [0, 0, 0, 0, 1]
def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b must be of same length")

    length = len(a)

    if length < 2:
        return a, b

    # randomly chose an index to cut a genome in half
    p = randint(1, length - 1)

    return a[0:p] + b[p:], b[0:p] + a[p:]


# # Sample Input [1,1,1,1,1]
# # Sample Output [1,0,1,1,1] (only element at index 1 was mutated)
# if mutation is too big, it will never reach the end
# if mutation is too small, he will never grow
def mutation(genome: Genome, number_of_mutations: int = MUTATIONS, mutation_probability: float = 0.1) -> Genome:
    genome_len = len(genome)
    for _ in range(number_of_mutations):
        randomGenomeIndex = randrange(genome_len)
        # leaves genome the same
        # OR turns 1 into 0 or 0 into 1
        # based on the mutation probability
        if random() < mutation_probability:
            genome[randomGenomeIndex] = generate_genome(1)[0]

    return genome


# generation_limit - maximum number of generation our evolution runs for, if it is not reaching the fitness limit before that
def run_evolution(populate_func: PopulateFunc,
                  fitness_func: FitnessFunc,
                  fitness_limit: int,
                  selection_func: SelectionFunc = selection_pair,
                  crossover_func: CrossoverFunc = single_point_crossover,
                  mutation_func: MutationFunc = mutation,
                  generation_limit: int = 100) -> Tuple[Population, int]:
    # random genomes:
    # for population size = 2 and genome_length of 10, it can be: [[0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    population = populate_func()

    for i in range(generation_limit):
        #  sort populations based on their fitness
        population = sorted(population, key=lambda genome: fitness_func(genome), reverse=True)

        visualize_maze(maze=MAZE, moves=population[0], start=get_coords_for_field(MAZE, START),
                       maze_name="generation_" + str(i))

        #  if the genome already meets our requirements
        if fitness_func(population[0]) >= fitness_limit:
            print('SUCCESS')
            break

        # Pick two best genomes from population
        # Elitism involves copying a small proportion of the fittest candidates, unchanged, into the next generation.
        next_generation = population[0:2]

        #  Loop as long as its needed to create a new generation with size equal to previous one
        for j in range(int(len(population) / 2) - 1):
            # Randomly pick parents, but genomes with higher fitness have bigger change of being picked
            parents = selection_func(population, fitness_func)
            # Create offsprings by crossing over genomes of parents
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            # Mutate offspring genomes
            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            # Add to the new generation
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    return population, i


def fitness(genome: Genome, maze: Maze, start: Coords, finish: Coords) -> int:
    position: Coords = start
    steps = 0
    visits = {}

    for index, move in enumerate(genome):
        next_move: Coords = get_next_move_coords(position, move)

        x: int = next_move[0]
        y: int = next_move[1]
        cell = maze[x][y]
        visit_key = 'x' + str(x) + 'y' + str(y)

        # prevent circles
        if visit_key in visits:
            break
        else:
            visits[visit_key] = 1

        if cell == END:
            return SOLUTION_FOUND_FITNESS_VALUE
        elif cell == PATH:
            if is_dead_end(maze, position, next_move):
                maze[x][y] = DEAD_END
                return DEAD_END_FITNESS_VALUE
            else:
                steps = steps + 1
                position = next_move
        else:
            break

    distance_to_finish = distance(position, finish)

    return STEPS_MULTIPLIER * steps - NEGATIVE_FINISH_MULTIPLIER * distance_to_finish


def main():
    def use_fitness(genome: Genome):
        return fitness(genome, maze=MAZE, start=get_coords_for_field(MAZE, START), finish=get_coords_for_field(MAZE, END))

    clear_folder()

    start = get_coords_for_field(MAZE, START)

    bfs_exit_path = find_exit_bfs(maze=MAZE, position=start)
    # print(MAZE)
    bfs_exit_moves = map_coords_to_moves(bfs_exit_path)
    visualize_maze(maze=MAZE, moves=bfs_exit_moves, start=start, maze_name="bfs")

    start = time.time()
    population, generations = run_evolution(
        fitness_func=use_fitness,
        populate_func=partial(generate_population, size=POPULATION_SIZE, genome_length=MAX_MOVES),
        fitness_limit=SOLUTION_FOUND_FITNESS_VALUE,  # value limit that makes us satisfied with the solution
        generation_limit=GENERATIONS  # so that we don't loop forever when fitness limit is never reached
    )
    end = time.time()


main()
