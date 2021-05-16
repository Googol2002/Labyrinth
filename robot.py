import numpy as np
from game import LabyrinthGame
from threading import Thread
import queue
import time


# A* 启发式寻路算法
class Robot:
    DIRECTIONS = [np.asarray([0, 1]), np.asarray([0, -1]),
                  np.asarray([-1, 0]), np.asarray([1, 0])]

    PARAMETER1 = PARAMETER2 = 2

    def __init__(self, labyrinth: LabyrinthGame):
        self.cost = -1
        self.labyrinth = labyrinth
        # distance of G
        self.distances_g = dict()
        # from where
        self.parents = dict()
        # distance of F = G + H
        self.distances_f = dict()
        self.heap = queue.PriorityQueue()

    def a_star(self):
        def expand(vec):
            pos = np.asarray(vec)
            for direction in Robot.DIRECTIONS:
                to = tuple(direction + pos)
                if self.labyrinth[to] == 2:
                    if (to == self.labyrinth.end).all():
                        self.add_vector(vec, to)
                        raise Exception("FOUND THE END{}".format(to))

                    if to not in self.distances_g:
                        self.add_vector(vec, to)
                    elif (self.func_g(vec) + 1 + self.func_h(to)) < self.func_f(to):
                        self.add_vector(vec, to)

        # 初始化start
        start = self.labyrinth.start
        self.distances_g[start] = 0
        self.distances_f[start] = self.func_h(start) + 0
        self.parents[start] = None
        self.heap.put((self.distances_f[start], start))

        cost = 0
        try:
            while not self.heap.empty():
                u = self.heap.get()

                # 落后数据，更新掉
                if u[0] > self.func_f(u[1]):
                    continue

                cost += 1
                expand(u[1])
        except Exception as e:
            self.cost = cost
            # print(e)

    def simulate(self):
        path = []

        parents = tuple(self.labyrinth.end)
        while parents != self.labyrinth.start:
            path.append(parents)
            parents = self.parents[parents]

        print("=====TASK=====")
        print("Cost:", self.cost)
        print("Path length:", len(path))
        print("Hamilton Distance", np.abs(self.labyrinth.end - np.asarray(self.labyrinth.start)).sum())

        while len(path) > 0:
            p = path.pop()
            self.labyrinth.position = p
            self.labyrinth.notify_update()
            time.sleep(0.5)
        self.labyrinth.check_win()

    def information(self):
        result = {"cost": self.cost}

        path = []
        parents = tuple(self.labyrinth.end)
        while parents != self.labyrinth.start:
            path.append(parents)
            parents = self.parents[parents]

        result["path"] = len(path)
        result["distance"] = np.abs(self.labyrinth.end - np.asarray(self.labyrinth.start)).sum()

        return result

    def func_g(self, pos):
        return self.distances_g[pos]

    def func_h(self, pos):
        end = self.labyrinth.end

        return self.PARAMETER1 * abs(end[0] - pos[0]) +\
               self.PARAMETER2 * abs(end[1] - pos[1])

    def add_vector(self, parent, to):
        # parent的g是正常的
        g = self.func_g(parent) + 1
        self.distances_g[to] = g
        f = g + self.func_h(to)
        self.distances_f[to] = f
        self.parents[to] = parent
        self.heap.put((f, to))

    def func_f(self, pos):
        return self.distances_f[pos]


class RobotThread(Thread):

    def __init__(self, l_g):
        super(RobotThread, self).__init__()
        self.robot = Robot(l_g)

    def run(self):
        self.robot.a_star()
        self.robot.simulate()
