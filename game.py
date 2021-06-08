import numpy as np
import random


class LabyrinthGameCore:

    def __init__(self):
        self.start = None
        self.end = None

    def display(self):
        raise NotImplemented()

    def upward(self):
        raise NotImplemented()

    def downward(self):
        raise NotImplemented()

    def leftward(self):
        raise NotImplemented()

    def rightward(self):
        raise NotImplemented()

    def add_win_observer(self, ob):
        raise NotImplemented()

    def add_update_observer(self, ob):
        raise NotImplemented()


class LabyrinthGame(LabyrinthGameCore):

    def __init__(self, width, height, initialize=None, has_mist=False):
        """
        :param width: 要求奇数
        :param height: 要求奇数
        :param initialize:
        """
        initialize = initialize if initialize else LabyrinthGame.prim

        self.width = width
        self.height = height
        self.labyrinth_data = np.zeros((height, width), dtype=int)
        self.start, self.end = initialize(self.labyrinth_data)
        self.win_observers = []
        self.update_observers = []
        self.position = self.start

        self.mist = np.ones((width, height)) if has_mist else None
        self.__dispell(self.end[0], self.end[1], 2)

    def display(self):
        raise NotImplemented()

    def upward(self):
        t = self.position[0], self.position[1] - 1
        if self.labyrinth_data[t[1], t[0]] == 2:
            self.position = t
            self.notify_update()
            self.check_win()
        else:
            raise IndexError()

    def downward(self):
        t = self.position[0], self.position[1] + 1
        if self.labyrinth_data[t[1], t[0]] == 2:
            self.position = t
            self.notify_update()
            self.check_win()
        else:
            raise IndexError()

    def leftward(self):
        t = self.position[0] - 1, self.position[1]
        if self.labyrinth_data[t[1], t[0]] == 2:
            self.position = t
            self.notify_update()
            self.check_win()
        else:
            raise IndexError()

    def rightward(self):
        t = self.position[0] + 1, self.position[1]
        if self.labyrinth_data[t[1], t[0]] == 2:
            self.position = t
            self.notify_update()
            self.check_win()
        else:
            raise IndexError()

    # 观察者模式
    def add_win_observer(self, ob):
        """
        :param ob:为一个方法
        :return:
        """
        self.win_observers.append(ob)

    # 观察者模式
    def add_update_observer(self, ob):
        """
        :param ob:为一个方法
        :return:
        """
        self.update_observers.append(ob)

    R = 4

    def __dispell(self, x, y, R):
        if self.mist is not None:
            self.mist[(x-R if x-R >= 0 else 0): (x+R+1 if x+R+1 <= self.width else x+R+1),
                (y-R if y-R >= 0 else 0): (y+R+1 if y+R+1 <= self.width else y+R+1)] = 0

    def notify_update(self):
        R = LabyrinthGame.R
        x = self.position[0]
        y = self.position[1]

        self.__dispell(x, y, R)

        for ob in self.update_observers:
            ob()

    def check_win(self):
        if (self.position == self.end).all():
            self.win()

    def win(self):
        for ob in self.win_observers:
            ob()

    @staticmethod
    def prim(data, start=None):

        def index(pos):
            return data[pos[1]][pos[0]]

        def way_to(pos_now, pos1):
            return pos_now[0] - pos1[0] + pos_now[0], \
                   pos_now[1] - pos1[1] + pos_now[1]

        def expand(pos_now):
            pos = pos_now
            pos_now = np.asarray(pos_now)
            directions = [np.asarray([0, 1]), np.asarray([0, -1]),
                          np.asarray([-1, 0]), np.asarray([1, 0])]
            for d in directions:
                if index((pos_now + d)) == 0:
                    road_set.add((tuple((pos_now + d)), pos))
                elif index((pos_now + d)) == 3:
                    nonlocal end
                    end = pos_now

        height, width = data.shape

        start = (1, random.randint(1, (height - 1) / 2) * 2 - 1) if start is None else start

        for i in range(1, height - 1, 2):
            data[i][1::2] = 1
        data[0, :] = 3
        data[-1, :] = 3
        data[:, 0] = 3
        data[:, -1] = 3

        data[start[1], start[0]] = 2
        road_set = set()
        expand(start)
        end = start
        while len(road_set) > 0:
            t = tuple(road_set)
            target = random.choice(t)
            road_set.remove(target)
            if index(target[0]) == 2:
                continue

            to = way_to(target[0], target[1])
            if index(to) == 1:
                data[target[0][1]][target[0][0]] = 2
                data[to[1]][to[0]] = 2
                expand(to)

            elif index(to) == 2:
                data[target[0][1]][target[0][0]] = 0

        return start, end

    @staticmethod
    def prim_with_circle_generator(rate):

        def prim_with_circle(data, start=None):
            start, end = LabyrinthGame.prim(data, start)
            roads = np.random.rand(*data.shape)
            roads[:, 0] = 1
            roads[:, -1] = 1
            roads[0, :] = 1
            roads[-1, :] = 1

            # TODO: 修改
            roads = np.where(roads < rate, 2, data)
            np.copyto(data, roads)

            return start, end

        return prim_with_circle

    def __getitem__(self, item):
        return self.labyrinth_data[item[1], item[0]]

    def __setitem__(self, key, value):
        self.labyrinth_data[key[1], key[0]] = value

    def is_mist(self, item):
        if self.mist is not None:
            return self.mist[item[1], item[0]] == 1
        else:
            return 0

class LabyrinthGameCmd(LabyrinthGame):
    TEXTS = ['█', 'N', ' ', '█']

    def display(self):

        for row in self.labyrinth_data:
            for num in row:
                print(LabyrinthGameCmd.TEXTS[num], end="")
            print()
