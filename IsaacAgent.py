from random import choice
from copy import deepcopy
from game_data import GameData
from agents import Agent
import numpy as np
import random
import pickle
import pandas as pd

class IsaacAgent(Agent):

    def __init__(self, max_time=2, max_depth=300):

        self.max_time = max_time
        self.max_depth = max_depth

        # self.heuristic = [
        #     [0], [0], [0], [0], [0], [0], [0],
        #     [0], [0], [0], [0], [0], [0], [0],
        #     [0], [0], [0], [0], [0], [0], [0],
        #     [0], [0], [0], [0], [0], [0], [0], # ...
        #     [0], [0], [-1], [-1], [-1], [0], [0], # odd player
        #     [0], [1, -1], [0], [0], [0], [1, -1], [0] # even player
        # ]

        self.heuristic = [
            [0], [0], [0], [0], [0], [0], [0],
            [0], [0], [1, -1], [2, -2], [1, -1], [0], [0],
            [0], [0], [1, -2], [2, -2], [1, -2], [0], [0],
            [0], [0], [3, -2], [3, -2], [3, -2], [0], [0],
            [0], [0], [4, -3], [4, -3], [3, -3], [0], [0],
            [0], [1, -1], [4, -4], [4, -4], [4, -4], [1, -1], [0]
        ]

        self.game_data = None

        self.model = pickle.load(open("./c4model.sav", 'rb'))

    def get_name(self) -> str:
        return "IsaacAgent"

    def get_move(self, game_data) -> int:
        self.game_data = game_data

        rows_reversed_connect4_board = []
        for row in list(game_data.game_board):
            rows_reversed_connect4_board.append(row[::-1])

        connect4_board = list(np.concatenate(rows_reversed_connect4_board).flat)[::-1]

        for sn, sv in enumerate(connect4_board):
            if sv == 0:
                connect4_board[sn] = ' '
            elif sv == 1:
                connect4_board[sn] = 'R'
            else:
                connect4_board[sn] = 'B'

        # self.print_board(connect4_board)

        turn = self.player(connect4_board)

        actions = self.actions(connect4_board)

        best_action = random.choice(actions)

        if turn == 'R':
            # max player

            local_best_min_v = -float('inf')

            for action in actions:
                self.current_depth = 0
                min_v = self.min_value(self.result(connect4_board, action))

                # print(f"Action: {action + 1}, Min Value: {min_v}")

                if min_v > local_best_min_v:
                    local_best_min_v = min_v
                    best_action = action

        else:
            # min player

            local_best_max_v = float('inf')

            for action in actions:
                self.current_depth = 0
                max_v = self.max_value(self.result(connect4_board, action))

                # print(f"Action: {action + 1}, Max Value: {max_v}")

                if max_v < local_best_max_v:
                    local_best_max_v = max_v
                    best_action = action
            
        return best_action

    def print_board(self, board):
        for l in range(0, 42, 7):
            row = ''.join([board[l + i] + '|' for i in range(7)])
            print(row[:13])
            print('-+-+-+-+-+-+-')

    def player(self, board):
        return 'B' if board.count('R') > board.count('B') else 'R'

    def is_tie(self, board):
        return len([sq for sq in board if sq == ' ']) == 0

    def utility(self, board):
        return 0 if self.is_tie(board) else -1000 if self.player(board) == "R" else 1000

    def terminal(self, board):
        # use modulo 7 to detect new row
        row = 0
        for sq in range(42):
            if sq % 7 == 0:
                row += 1

            distance_to_new_row = 7 * row - (sq + 1)
            distance_to_column_end = [i for i in range(6) if (sq + 1) + i * 7 > 35][0]

            if board[sq] == ' ':
                continue

            # 4 horizontally
            if distance_to_new_row >= 3 and board[sq] == board[sq + 1] and board[sq] == board[sq + 2] and board[sq] == board[sq + 3]:
                return True
            # 4 vertically
            elif distance_to_column_end > 2 and board[sq] == board[sq + 7] and board[sq] == board[sq + 14] and board[sq] == board[sq + 21]:
                return True
            # 4 diagonally
            elif distance_to_new_row >= 3 and distance_to_column_end >= 2 and sq + 24 < len(board) and board[sq] == board[sq + 8] and board[sq] == board[sq + 16] and board[sq] == board[sq + 24]:
                return True
            elif distance_to_new_row >= 3 and distance_to_column_end <= 2 and 0 <= sq - 18 < len(board) and board[sq] == board[sq - 6] and board[sq] == board[sq - 12] and board[sq] == board[sq - 18]:
                return True

        return self.is_tie(board)

    def actions(self, board):
        return [sn for sn in range(7) if board[sn] == ' ']

    def result(self, board, action):
        result = board[:]
        for r in range(6):
            current_sq = board[action + 35 - r * 7]
            if current_sq == ' ':
                result[action + 35 - r * 7] = self.player(board)
                break
        return result

    def count_two_in_row(self, board, player):
        two_in_row = 0

        row = 0
        for sq in range(42):
            if sq % 7 == 0:
                row += 1

            distance_to_new_row = 7 * row - (sq + 1)
            distance_to_column_end = [i for i in range(6) if (sq + 1) + i * 7 > 35][0]

            if board[sq] != player or board[sq].isdigit() or board[sq] == ' ':
                continue

            # 4 horizontally
            if distance_to_new_row >= 3 and board[sq] == board[sq + 1]:
                two_in_row += 1
            # 4 vertically
            elif distance_to_column_end > 2 and board[sq] == board[sq + 7]:
                two_in_row += 1
            # 4 diagonally
            elif distance_to_new_row >= 3 and distance_to_column_end >= 2 and sq + 8 < len(board) and board[sq] == board[sq + 8]:
                two_in_row += 1
            elif distance_to_new_row >= 3 and distance_to_column_end <= 2 and 0 <= sq - 6 < len(board) and board[sq] == board[sq - 6]:
                two_in_row += 1

        return two_in_row

    def count_three_in_row(self, board, player):
        three_in_row = 0

        row = 0
        for sq in range(42):
            if sq % 7 == 0:
                row += 1

            distance_to_new_row = 7 * row - (sq + 1)
            distance_to_column_end = [i for i in range(6) if (sq + 1) + i * 7 > 35][0]

            if board[sq] != player or board[sq].isdigit() or board[sq] == ' ':
                continue

            # 4 horizontally
            if distance_to_new_row >= 3 and board[sq] == board[sq + 1] and board[sq] == board[sq + 2]:
                three_in_row += 1
            # 4 vertically
            elif distance_to_column_end > 2 and board[sq] == board[sq + 7] and board[sq] == board[sq + 14]:
                three_in_row += 1
            # 4 diagonally
            elif distance_to_new_row >= 3 and distance_to_column_end >= 2 and sq + 16 < len(board) and board[sq] == board[sq + 8] and board[sq] == board[sq + 16]:
                three_in_row += 1
            elif distance_to_new_row >= 3 and distance_to_column_end <= 2 and 0 <= sq - 12 < len(board) and board[sq] == board[sq - 6] and board[sq] == board[sq - 12]:
                three_in_row += 1

        return three_in_row

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
        for vn, values in enumerate(self.heuristic):
            for value in values:
                if value < 0 and board[vn] == 'B':
                    total_score += value
                elif value > 0 and board[vn] == 'R':
                    total_score += value

        # three_in_row_modifier = 10
        # total_score += self.count_three_in_row(board, 'R') * three_in_row_modifier
        # total_score -= self.count_three_in_row(board, 'B') * three_in_row_modifier
        # total_score += self.count_two_in_row(board, 'R') * three_in_row_modifier
        # total_score -= self.count_two_in_row(board, 'B') * three_in_row_modifier

        
        # divisor = 5
        # for i in range(7):
        #     action_result = self.result(board, i)
        #     if self.terminal(action_result):
        #         total_score += self.utility(action_result) / divisor

        #     print(total_score)

        # multiplier = 2
        # r_win_states = 0
        # b_win_states = 0
        # for i in range(7):
        #     action_result = self.result(board, i)
        #     if self.terminal(action_result):
        #         if self.utility(action_result) == 1000:
        #             r_win_states += 1
        #         else:
        #             b_win_states += 1

        # total_score += r_win_states * multiplier
        # total_score -= b_win_states * multiplier

        # if r_win_states >= 2:
        #     total_score += 400
        # elif b_win_states >= 2:
        #     total_score -= 400

        # print(f"Red Win States: {r_win_states}, Blue Win States: {b_win_states}")

        multiplier = 30

        conv_data = []

        for sq in board:
            if sq.isdigit() or sq == ' ':
                conv_data.append(0)
            elif sq == 'R':
                conv_data.append(1)
            else:
                conv_data.append(-1)  

        c4_board = pd.Series(conv_data, index=[f"pos_{sn + 1}" for sn, sv in enumerate(board)])

        total_score += self.model.predict([c4_board])[0][0]

        return total_score

    def min_value(self, board):
        if self.terminal(board):
            return self.utility(board)

        if self.current_depth > self.max_depth:
            return self.evaluate(board)

        self.current_depth += 1
        v = float('inf')

        for action in self.actions(board):
            max_v = self.max_value(self.result(board, action))
            v = min(v, max_v)

        return v

    def max_value(self, board):
        if self.terminal(board):
            return self.utility(board)

        if self.current_depth > self.max_depth:
            return self.evaluate(board)

        self.current_depth += 1
        v = -float('inf')

        for action in self.actions(board):
            min_v = self.min_value(self.result(board, action))
            v = max(v, min_v)

        return v
        