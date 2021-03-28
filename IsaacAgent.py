from random import choice
from copy import deepcopy
from game_data import GameData
from agents import Agent

class IsaacAgent(Agent):
    """
    Isaac's agent
    """
    def __init__(self, max_time, max_depth):
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


    @staticmethod
    def get_name() -> str:
        return "Random"
        
    def get_move(self, data) -> int:
        """ returns a random valid col"""
        return choice([c for c in range(7) if data.game_board.is_valid_location(c)])


    def create_board(self):
        new_connect4_board = []
        for i in range(1, 43):
            if i <= 7:
                new_connect4_board.append(str(i))
            else:
                new_connect4_board.append(' ')
        return new_connect4_board

    def print_board(self, board):
        for l in range(0, 42, 7):
            row = ''.join([board[l + i] + '|' for i in range(7)])
            print(row[:13])
            print('-+-+-+-+-+-+-')

    def player(self, board):
        return 'B' if board.count('R') > board.count('B') else 'R'

    def is_tie(self, board):
        return len([sq for sq in board if sq.isdigit() or sq == ' ']) == 0

    def utility(self, board):
        return 0 if self.is_tie(board) else 100 if self.player(board) == "R" else -100 

    def terminal(self, board):
        # use modulo 7 to detect new row
        row = 0
        for sq in range(42):
            if sq % 7 == 0:
                row += 1

            distance_to_new_row = 7 * row - (sq + 1)
            distance_to_column_end = [i for i in range(6) if (sq + 1) + i * 7 > 35][0]

            if board[sq].isdigit() or board[sq] == ' ':
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
        return [sn for sn in range(7) if board[sn].isdigit()]

    def result(self, board, action):
        result = board[:]
        for r in range(6):
            current_sq = board[action + 35 - r * 7]
            if current_sq.isdigit() or current_sq == ' ':
                result[action + 35 - r * 7] = self.player(board)
                break
        return result

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
            if sv < 0 and board[sn] == 'B':
                total_score += sv
            elif board[sn] == 'R':
                total_score += sv

        return total_score

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

    def connect4(self):
            connect4_board = self.create_board()

            turn = None
            winner = None

            print("Do you want to play as 'R' or 'B'?")
            human = 'R' if input().lower().strip() == 'r' else 'B'

            while not winner:
                turn = self.player(connect4_board)

                print(f"Your move {turn}.")
                self.print_board(connect4_board)
                print(f"Evaluation: {self.evaluate(connect4_board)}")

                if turn == human:
                    move = None

                    while move == None:
                        column = int(input().strip()) - 1
                        
                        for r in range(6):
                            current_sq = connect4_board[column + 35 - r * 7]
                            if current_sq.isdigit() or current_sq == ' ':
                                move = column + 35 - r * 7
                                break

                        # +35
                        # -7
                        # -14

                        if move is not None:
                            connect4_board[move] = turn
                        else:
                            move = None
                            print('That place is already filled. Still your move.')
                else:
                    best_action = None
                    self.start = time.time()

                    if turn == 'R':
                        # max player

                        local_best_min_v = -float('inf')

                        for action in self.actions(connect4_board):
                            self.current_depth = 0
                            min_v = self.min_value(self.result(connect4_board, action))
                            print(min_v)

                            if min_v > local_best_min_v:
                                local_best_min_v = min_v
                                best_action = action

                        connect4_board = self.result( connect4_board, best_action )

                    else:
                        # min player

                        local_best_max_v = float('inf')

                        for action in self.actions(connect4_board):
                            self.current_depth = 0
                            max_v = self.max_value(self.result(connect4_board, action))

                            if max_v < local_best_max_v:
                                local_best_max_v = max_v
                                best_action = action

                        connect4_board = self.result(connect4_board, best_action)
                        
                    print(f'Calculation time: {time.time() - self.start}')

                if self.terminal(connect4_board):
                    winner = self.utility(connect4_board)

                    self.print_board(connect4_board)
                    print('\nGame Over.\n')

                    if winner == 0:
                        print('Tie game.')
                    else:
                        print(f'**** {turn} won ****')

                    break
            
            # play again?
            restart = input("Do want to play Again? (y/n) > ")
            if restart.lower().strip() == 'y':
                self.connect4()

minimax_connect4 = MinimaxConnect4(max_time=2.2, max_depth=12)
minimax_connect4.connect4()