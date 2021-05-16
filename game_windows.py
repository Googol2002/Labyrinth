import tkinter
from tkinter import font
from tkinter import Canvas
from tkinter import Tk
from tkinter import Button
from tkinter import Frame
from tkinter import PhotoImage
from enum import Enum

from game import LabyrinthGame
from game import LabyrinthGameCore
from robot import RobotThread


class LabyrinthGameGui(LabyrinthGameCore):
    RATE = 0.6

    class State(Enum):
        GAME = 1
        WIN = 2

    def __init__(self, width, height):
        # super(LabyrinthGameGui, self).__init__(width, height, initialize=initialize)
        self.game = None
        self.width = width
        self.height = height
        self.state = None

        self.root = Tk()
        self.root.title("迷宫 By Hy. Shi")
        self.pho = PhotoImage(file=r"D:\Workspace\Final Project\Cha.png")
        # 创建一个Canvas，设置其背景色为白色
        self.cv = Canvas(self.root, bg='white', width=800, height=600)
        self.cv.bind("<w>", self.upward_event)
        self.cv.bind("<a>", self.leftward_event)
        self.cv.bind("<s>", self.downward_event)
        self.cv.bind("<d>", self.rightward_event)
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

    def button1(self, event):
        self.state = LabyrinthGameGui.State.GAME
        self.game = LabyrinthGame(self.width, self.height, initialize=LabyrinthGameGui.INITIALIZES[self.mode.get()],
                                  has_mist=(self.is_mist.get() == 1))
        self.game.add_win_observer(self.win)
        self.game.add_update_observer(self.update_async)
        self.game.notify_update()

    def button2(self, event):
        self.state = LabyrinthGameGui.State.GAME
        self.game = LabyrinthGame(self.width, self.height, initialize=LabyrinthGameGui.INITIALIZES[self.mode.get()],
                                  has_mist=(self.is_mist.get() == 1))
        self.game.add_win_observer(self.paint_win)
        self.game.add_update_observer(self.update_async)
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

        per_width = 30

        for i, row in enumerate(self.game.labyrinth_data):
            for j, num in enumerate(row):
                self.cv.create_rectangle(j * per_width, i * per_width, (j + 1) * per_width, (i + 1) * per_width,
                                         fill=("white" if self.game.is_mist((i, j))
                                               else ("#F2F2F2" if num == 2 else "#635A47")), outline='white')
        self.cv.create_text(self.game.start[0] * per_width + per_width / 2, self.game.start[1] * per_width + per_width / 2,
                            text="S", fill="#5C1015")
        self.cv.create_text(self.game.end[0] * per_width + per_width / 2, self.game.end[1] * per_width + per_width / 2,
                            text="E", fill="#5C1015")

        self.cv.create_image(self.game.position[0] * per_width + per_width / 2, self.game.position[1] * per_width + per_width / 2,
                             image=self.pho)

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