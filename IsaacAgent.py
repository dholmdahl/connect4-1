from random import choice
from copy import deepcopy
from game_data import GameData
from agents import Agent
import numpy as np

class IsaacAgent(Agent):

    def __init__(self, max_time=2, max_depth=12):
        self.best_min_v = -float('inf')
        self.best_max_v = float('inf')

        self.max_time = max_time
        self.max_depth = max_depth

        self.heuristic = [
            0, 0, -1, -1, -1, 0, 0,
            0, 0, 2, 2, 2, 0, 0,
            0, 0, -2, -2, -2, 0, 0,
            0, 0, 3, 3, 3, 0, 0,
            0, 0, -3, -3, -3, 0, 0,
            0, 0, 1, 1, 1, 0, 0
        ]

        self.game_data = None
        self.connect4_board = None

    def get_name(self) -> str:
        return "IsaacAgent"

    def get_move(self, game_data) -> int:
        self.game_data = game_data
        # self.connect4_board = np.concatenate( game_data.game_board, axis=0 )

        print(type(game_data.game_board))
        print(list(game_data.game_board))
        return 2

    def player(self, board):
        return self.game_data.turn

    def is_tie(self, board):
        return game_data.game_board.tie_move()

    def utility(self, board):
        return 0 if self.is_tie(board) else -100 if self.player(board) == 0 else 100
        
    def evaluate(self, board):
        """
        Heuristic:
        - Squares value:
            [0, 0, -1, -1, -1, 0, 0,
             0, 0, 2, 2, 2, 0, 0,
             0, 0, -2, -2, -2, 0, 0,
             0, 0, 3, 3, 3, 0, 0,
             0, 0, -3, -3, -3, 0, 0,
             0, 0, 1, 1, 1, 0, 0]

        - Include win squares of each player and where they are located.
        Heuristic based off Odd-Even strategy: https://www.youtube.com/watch?v=YqqcNjQMX18
        """

        total_score = 0
        for sn, sv in enumerate(self.heuristic):
            if sv < 0 and board[sn] == 2:
                total_score += sv
            elif board[sn] == 1:
                total_score += sv

        return total_score

    def terminal(self, board):
        if game_data.game_board.horizontal_win() or game_data.game_board.vertical_win() or game_data.game_board.diagonal_win():
            return True

        return self.is_tie(board)

    def actions(self, board):
        return [sn for sn in range(7) if board[sn].isdigit()]

    def result(self, board, action):
        result = board[:]
        for r in range(6):
            current_sq = board[action + 35 - r * 7]
            if current_sq.isdigit() or current_sq == ' ':
                result[action + 35 - r * 7] = self.player(board)
                break
        return result

    def min_value(self, board):
        if self.terminal(board):
            return self.utility(board)
        # print(f"Current Depth: {self.current_depth}, Max Depth: {self.max_depth}, Is At Max Depth: {self.current_depth > self.max_depth}")
        if self.current_depth > self.max_depth:
            return self.evaluate(board)

        self.current_depth += 1
        v = float('inf')

        for action in self.actions(board):
            max_v = self.max_value(self.result(board, action))
            v = min(v, max_v)
            self.best_max_v = min(v, max_v)
            if v < self.best_min_v:
                break
        return v

    def max_value(self, board):
        if self.terminal(board):
            # print(self.utility(board))
            return self.utility(board)
        if self.current_depth > self.max_depth:
            return self.evaluate(board)

        self.current_depth += 1
        v = -float('inf')

        for action in self.actions(board):
            min_v = self.min_value(self.result(board, action))
            v = max(v, min_v)
            self.best_min_v = max(v, min_v)
            if v > self.best_max_v:
                break
        return v
