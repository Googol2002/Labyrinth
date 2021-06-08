from game import LabyrinthGame
from game_windows import LabyrinthGameGui
from robot import Robot
from threading import Thread

if __name__ == "__main__":
    labyrinth = LabyrinthGameGui()
    labyrinth.display()