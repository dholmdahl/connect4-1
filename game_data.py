from typing import Tuple
import enum

from game_board import GameBoard

#const
#TODO - make enum
PLAYER1 = 0
PLAYER2 = 1

class GameData:
    """
    The game data class contains all of the data for the game.
    """

    radius: int
    height: int
    width: int
    sq_size: int
    size: Tuple[int, int]

    game_over: bool
    turn: int #0 = player1, 1 = player2
    last_move_row: [int]
    last_move_col: [int]
    game_board: GameBoard
    winner: int # 0 = Nobody yet, 1 = player1, 2 = player2

    def __init__(self):
        self.game_over = False
        self.winner = 0
        self.turn = 0
        self.last_move_row = []
        self.last_move_col = []
        self.game_board = GameBoard()
        self.action = None

        self.sq_size: int = 100
        self.width: int = 7 * self.sq_size
        self.height: int = 7 * self.sq_size
        self.size: Tuple[int, int] = (self.width, self.height)
        self.radius: int = int(self.sq_size / 2 - 5)

class PLAYER(enum.Enum):
    Player1 = 0
    Player2 = 1

class WINNER(enum.Enum):
    Nobody = 0
    Player1 = 1
    Player2 = 2