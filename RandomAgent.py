from random import choice
from copy import deepcopy
from game_data import GameData
from agents import Agent

class RandomAgent(Agent):
    """
    An agent which makes random moves.
    """

    @staticmethod
    def get_name(self) -> str:
        return "RandomAgent"
        
    @staticmethod
    def get_move(data) -> int:
        """ returns a random valid col"""
        return choice([c for c in range(7) if data.game_board.is_valid_location(c)])