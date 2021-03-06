from sys import argv
import numpy as np
from random import shuffle
from os import path


def read(filename):
    with open(filename, 'r') as f:
        lines = [[int(x) for x in line.split()] for line in f]
        n = lines[0][0]
        C = set(lines[1])
        A = np.array(lines[2:n+2])
        return A, C


def output(i, cycles, objval, gap):
    filename = './out/%d.out' % i
    if path.isfile(filename):
        with open(filename, 'r') as f:
            objval2 = float(f.readline())
            if objval2 >= objval:
                return
    with open(filename, 'w') as f:
        f.write(str(objval) + '\n')
        f.write(str(gap) + '\n')
        f.write(format_cycles(cycles) + '\n')


def format_cycles(cycles):
    if len(cycles) == 0:
        return 'None'
    cycles = [' '.join(map(str, cycle)) for cycle in cycles]
    return '; '.join(cycles)

def run(i, k):
    """
    Run our greedy algorithm on the ith instance with k max cycle length.
    """
    filename = 'phase1-processed/%d.in' % i
    A, C = read(filename)
    n = A.shape[0]
    solutions = []
    solutions.append(solve_greedy(np.copy(A), C, n, k, range(n)))
    print(solutions[0][0])
    for i in range(3):  # run the randomized version 3 times
        A_copy = np.copy(A)
        perm = list(range(n))
        shuffle(perm)
        sol = solve_greedy(A_copy, C, n, k, perm)
        if sol[1] is not None:
            solutions.append(sol)
        print(sol[0])
    return max(solutions)

def solve_greedy(A, C, n, k, perm):
    """
    A - adjancency matrix
    C - children
    n - size of our adjancy matrix
    k - max cycle length
    perm - a permutation of 1 to n
    """
    A_copy = np.copy(A)
    matched = set()
    total_weight = 0
    cycles = []
    while True:
        best_weight = 0
        best_cycle = None
        for i in perm:
            if i in matched:
                continue
            weight, cycle = dfs_from(i, A, C, k, 5)
            if cycle is None:
                continue
            if weight > best_weight:
                best_weight = weight
                best_cycle = cycle
        if best_cycle is None:
            break
        total_weight += best_weight
        for vertex in best_cycle:
            if vertex in matched:
                print("ERR: %d already matched" % vertex)
            matched.add(vertex)
            for j in range(n):
                A[vertex][j] = 0
                A[j][vertex] = 0
        cycles.append(best_cycle)
    if check_cycles(A_copy, C, k, cycles, total_weight):
        return total_weight, cycles
    else:
        print("Returning false")
        return 0, None


def dfs_from(i, A, C, k, L):
    n = A.shape[0]
    queue = [(j, [j]) for j in range(n) if A[i][j] == 1]
    found = []
    while len(queue) > 0:
        pos, path = queue.pop()
        for j in range(n):
            if A[pos][j] == 1:
                new_path = list(path)
                if j == i:
                    new_path.append(j)
                    found.append(new_path)
                    if len(found) == L:
                        return best_cycle(found, A, C)
                else:
                    new_path = list(path)
                    if j not in path:
                        new_path.append(j)
                        if len(new_path) < k:
                            queue.append((j, new_path))
    # base case
    return best_cycle(found, A, C)


def best_cycle(cycles, A, C):
    if len(cycles) == 0:
        return 0, None
    weights = []
    for cycle in cycles:
        weight = 0
        for vertex in cycle:
            if vertex in C:
                weight += 2
            else:
                weight += 1
        weights.append((weight, cycle))
    return max(weights)


def check_cycles(A, C, k, cycles, objval):
    n = A.shape[0]
    used = [False for i in range(n)]
    r_objval = 0.0
    for cycle in cycles:
        len_cycle = len(cycle)
        if len_cycle <= 1:
            print('ERROR: cycle of length <= 1 :', cycle)
            return False
        if len_cycle > k + 1:
            print('ERROR: cycle of length >=', k, ':', cycle)
            return False
        if len(set(cycle)) != len_cycle:
            print('ERROR: duplicate vertex in cycle :', cycle)
            return False

        for v in cycle:
            if used[v]:
                print('ERROR: cycle contains already-used vertex :', cycle, '(', v, ')')
                return False
            if v < 0 or v >= n:
                print('ERROR: vertex out of range:', v)
                return False
            used[v] = True
            r_objval += 2 if v in C else 1

        for i in range(1, len_cycle + 1):
            if A[cycle[i - 1], cycle[i % len_cycle]] != 1:
                print('ERROR: cycle contains nonexistent edge :', cycle, '(', cycle[i - 1], ',', cycle[i % len_cycle], ')')
                return False

    if r_objval != objval:
        print('ERROR: reported objective value != real objective value : r_objval =', r_objval, ', objval =', objval)
        return False
    return True

def run_inst(i):
        solution = run(i, 5)
        objval, cycles = solution
        objval = float(objval)
        print(solution)
        output(i, cycles, objval, 0.0)

if __name__ == '__main__':
    if len(argv) == 2 and int(argv[1]) in range(1, 493):
        i = int(argv[1])
        run_inst(i)
    elif len(argv) == 3 and int(argv[1]) < int(argv[2]):
        l = int(argv[1])
        r = int(argv[2])
        for i in range(l, r):
            run_inst(i)
