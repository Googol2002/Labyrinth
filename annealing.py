from game import LabyrinthGame
from robot import Robot
import math
from random import random


def robot_cost_gene(labyrinths):
    def robot_cost(parameter):
        sum_cost = 0
        for lab in labyrinths:
            r = Robot(lab)
            r.PARAMETER1 = r.PARAMETER2 = parameter
            r.a_star()
            sum_cost += r.information()["cost"]

        return sum_cost
    return robot_cost


def judge(dE, t):
    if dE < 0:
        return True
    else:
        d = math.exp(-(dE / t))
        if d > random():
            return True
        else:
            return False


def annealing(a, b, func):
    tmp = 1e5
    tmp_max = 1e5
    tmp_min = 1e-3

    alpha = 1
    beta = 0.99

    p_old = (b - a) * random() * a
    p_new = p_old
    f_old = func(p_old)
    f_new = f_old

    k_max = 100
    counter = 0

    f_min_history = f_old
    p_min_history = p_old

    while counter < k_max and tmp > tmp_min:
        delta = (random() - 0.5) * (b - a) * alpha
        p_new = p_old + delta
        if p_new < a or p_new > b:
            p_new = p_new - 2 * delta

        f_new = func(p_new)

        dE = f_new - f_old

        if f_new < f_min_history:
            f_min_history = f_new
            p_min_history = p_new

        if judge(dE, tmp):
            p_old = p_new
            f_old = f_new

        if dE < 0:
            tmp *= beta

        counter += 1
        print(counter)

    return p_min_history


if __name__ == "__main__":
    labs = [LabyrinthGame(51, 25, LabyrinthGame.prim) for _ in range(100)]
    f = robot_cost_gene(labs)

    p = annealing(0, 2, f)

    print(p)