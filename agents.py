from random import choice
from copy import deepcopy
from game_data import GameData
import abc


class Agent(abc.ABC):
    """
    It is an abstract class. All the agents must inherit from this class.
    Modified From: https://github.com/Pabloo22/connect4
    """

    def get_name(self) -> str:
        return "default"
        
    def get_move(self, game_data: GameData) -> int:
        pass

