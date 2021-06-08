import tkinter
from tkinter import font
from tkinter import Canvas
from tkinter import Tk
from tkinter import Button
from tkinter import Frame
from tkinter import PhotoImage
from enum import Enum
import math
import numpy as np

from game import LabyrinthGame
from game import LabyrinthGameCore
from robot import RobotThread


class LabyrinthGameGui(LabyrinthGameCore):
    RATE = 0.6
    PER_WIDTH = 32

    class State(Enum):
        GAME = 1
        WIN = 2

    def __init__(self, width=None, height=None):
        # super(LabyrinthGameGui, self).__init__(width, height, initialize=initialize)
        self.root = Tk()

        self.game = None
        self.random_map = None
        self.width = width
        self.height = height
        # self.width = width if width else (math.floor(self.root.winfo_screenwidth()
        #                                             / LabyrinthGameGui.PER_WIDTH) + 1) // 2 * 2 - 1
        # self.height = height if height else (math.floor(self.root.winfo_screenheight()
        #                                             / LabyrinthGameGui.PER_WIDTH) + 1) // 2 * 2 - 1
        self.state = None

        self.root.title("迷宫 By Hy. Shi")
        self.pho = PhotoImage(file=r".\texture\Cha.png")
        self.resource = self.__resource()
        # 创建一个Canvas，设置其背景色为白色
        self.cv = Canvas(self.root, bg='white', width=800, height=600)
        self.cv.bind("<w>", self.upward_event)
        self.cv.bind("<a>", self.leftward_event)
        self.cv.bind("<s>", self.downward_event)
        self.cv.bind("<d>", self.rightward_event)
        self.cv.bind("<W>", self.upward_event)
        self.cv.bind("<A>", self.leftward_event)
        self.cv.bind("<S>", self.downward_event)
        self.cv.bind("<D>", self.rightward_event)
        # canvas随窗口大小改变

        top = Frame(self.root, takefocus=False)
        bt1 = Button(top, takefocus=False)
        bt1.configure(text="Play by Yourself")
        bt1.bind("<Button-1>", self.button1)
        bt1.grid(row=0, column=0)

        bt2 = Button(top, takefocus=False)
        bt2.configure(text="Play by Robot")
        bt2.bind("<Button-1>", self.button2)
        bt2.grid(row=0, column=1)

        self.mode = tkinter.IntVar()
        self.mode.set(1)
        mode1 = tkinter.Radiobutton(top, text="Prim无环", value=1, variable=self.mode)
        mode2 = tkinter.Radiobutton(top, text="Prim有环", value=2, variable=self.mode)
        mode1.grid(row=0, column=2)
        mode2.grid(row=0, column=3)

        self.is_mist = tkinter.IntVar()
        self.is_mist.set(0)
        mist_box = tkinter.Checkbutton(top, text="战争迷雾", variable=self.is_mist, onvalue=1, offvalue=0)
        mist_box.grid(row=0, column=4)

        top.pack()
        self.cv.pack(fill='both', expand='yes')

    def display(self):
        self.root.mainloop()

    INITIALIZES = {1: LabyrinthGame.prim, 2: LabyrinthGame.prim_with_circle_generator(RATE)}

    def __width(self):
        return self.width if self.width else (math.floor(self.cv.winfo_width()
                                                     / LabyrinthGameGui.PER_WIDTH) + 1) // 2 * 2 - 1

    def __height(self):
        return self.height if self.height else (math.floor(self.cv.winfo_height()
                                     / LabyrinthGameGui.PER_WIDTH) + 1) // 2 * 2 - 1

    def button1(self, event):
        self.state = LabyrinthGameGui.State.GAME
        self.game = LabyrinthGame(self.__width(), self.__height(), initialize=LabyrinthGameGui.INITIALIZES[self.mode.get()],
                                  has_mist=(self.is_mist.get() == 1))
        self.game.add_win_observer(self.win)
        self.game.add_update_observer(self.update_async)
        self.random_map = np.random.rand(self.__height(), self.__width())
        self.game.notify_update()

    def button2(self, event):
        self.state = LabyrinthGameGui.State.GAME
        self.game = LabyrinthGame(self.__width(), self.__height(), initialize=LabyrinthGameGui.INITIALIZES[self.mode.get()],
                                  has_mist=(self.is_mist.get() == 1))
        self.game.add_win_observer(self.paint_win)
        self.game.add_update_observer(self.update_async)
        self.random_map = np.random.rand(self.__height(), self.__width())
        self.game.notify_update()

        bt = RobotThread(self.game)
        bt.start()

    # 这样Robot多线程不会阻塞
    def update_async(self):
        self.root.after_idle(self.repaint)

    def repaint(self):
        """
        Shouldn't be called directly
        :return:
        """
        if self.state == self.State.WIN:
            return

        self.cv.delete("all")

        per_width = LabyrinthGameGui.PER_WIDTH

        for i, row in enumerate(self.game.labyrinth_data):
            for j, num in enumerate(row):
                # self.cv.create_rectangle(j * per_width, i * per_width, (j + 1) * per_width, (i + 1) * per_width,
                #                         fill=("white" if self.game.is_mist((i, j))
                #                               else ("#F2F2F2" if num == 2 else "#635A47")), outline='white')
                if self.game.is_mist((i, j)):
                    self.cv.create_rectangle(j * per_width, i * per_width, (j + 1) * per_width, (i + 1) * per_width,
                                             fill="white", outline="white")
                else:
                    self.cv.create_image(j * per_width + per_width / 2, i * per_width + per_width / 2,
                                         image=self.resource(num, self.random_map[i][j]))
        # self.cv.create_text(self.game.start[0] * per_width + per_width / 2,
        #       self.game.start[1] * per_width + per_width / 2, text="S", fill="#5C1015")
        # self.cv.create_text(self.game.end[0] * per_width + per_width / 2,
        #       self.game.end[1] * per_width + per_width / 2, text="E", fill="#5C1015")
        self.cv.create_image(self.game.start[0] * per_width + per_width / 2,
                             self.game.start[1] * per_width + per_width / 2, image=self.resource(4))

        self.cv.create_image(self.game.end[0] * per_width + per_width / 2,
                             self.game.end[1] * per_width + per_width / 2, image=self.resource(5))

        self.cv.create_image(self.game.position[0] * per_width + per_width / 2,
                             self.game.position[1] * per_width + per_width / 2, image=self.pho)

        self.cv.focus_set()
#       self.cv.update_idletasks()

    def win(self):
        self.root.after_idle(self.paint_win)

    def paint_win(self):
        """
        Shouldn't be called directly
        :return:
        """
        my_font = font.Font(size=40, weight='bold')
        self.cv.create_text(self.cv.winfo_width() / 2, 200, text="Congratulations", font=my_font, fill="#506AD4")
        self.state = self.State.WIN
#       self.cv.update_idletasks()

    def upward_event(self, event):
        if self.state == self.State.WIN:
            return
        try:
            self.game.upward()
        except IndexError:
            pass

    def downward_event(self, event):
        if self.state == self.State.WIN:
            return
        try:
            self.game.downward()
        except IndexError:
            pass

    def leftward_event(self, event):
        if self.state == self.State.WIN:
            return
        try:
            self.game.leftward()
        except IndexError:
            pass

    def rightward_event(self, event):
        if self.state == self.State.WIN:
            return
        try:
            self.game.rightward()
        except IndexError:
            pass

    MOSSY_RATE = 0.3

    @staticmethod
    def __resource():

        blocks = []
        roads = []

        blocks.append(PhotoImage(file=r".\texture\stone_bricks.png"))
        blocks.append(PhotoImage(file=r".\texture\mossy_stone_bricks.png"))

        roads.append(PhotoImage(file=r".\texture\sand.png"))
        end = PhotoImage(file=r".\texture\water_bucket.png")
        begin = PhotoImage(file=r".\texture\crafting_table_front.png")

        def resource(id, rand_num=None):
            if id == 2:
                return roads[0]
            elif id == 0 or id == 3:
                r = 0 if rand_num > LabyrinthGameGui.RATE else 1
                return blocks[r]
            elif id == 4:
                return begin
            elif id == 5:
                return end

            raise IndexError()

        return resource
