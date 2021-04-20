from random import choice
from game_data import GameData
from agents import Agent

import subprocess
import re

class CppAgent(Agent):

    __cpp_board: str

    """
    See: https://connect4.gamesolver.org/
    And: http://blog.gamesolver.org/solving-connect-four/01-introduction/
    c4solver.exe: buit for win from source at: https://github.com/PascalPons/connect4/
    7x6.book is from: https://github.com/PascalPons/connect4/releases
    """
    def __init__(self):
        """
        Setup the c4solver
        """
        self.__cpp_board = ""
        self.__solver = subprocess.Popen(['c4solver.exe', '-b', '7x6.book'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT
                        )
        # clear out the book load line
        out = self.__solver.stdout.readline()
        self.__re_score = re.compile("[1-7]+ ([-0-9]+)")

    @staticmethod
    def get_name() -> str:
        return "CppAgent"
        
    def get_move(self, game_data: GameData) -> int:
        """ returns a move from c4agent.exe """
        # print("Slots filled=",game_data.game_board.slots_filled, ", cpp board=", self.__cpp_board)
        if game_data.game_board.slots_filled == 0:
            # first move of the game
            self.__cpp_board = "4"
            return 3
        elif game_data.game_board.slots_filled == 1:
            # opponent went first
            self.__cpp_board = ""
        
        self.set_cpp_board(game_data)
        
        #possible_moves is a list of columns that aren't full
        possible_moves = [col for col in range(7) if game_data.game_board.is_valid_location(col)]
        move_values = [self._get_score(move) for move in possible_moves]
        best_moves = [i for i in possible_moves if move_values[possible_moves.index(i)] == min(move_values)]
        col = choice(best_moves)
        # print("t=",game_data.turn,"p_m=",possible_moves,"m_vals=",move_values,"b_m=",best_moves,"col=",col)
        self.__cpp_board += str(col + 1)
        return col

    def set_cpp_board(self, game_data: GameData):
        # print("lmc: ", game_data.last_move_col)
        self.__cpp_board += str(game_data.last_move_col[-1] + 1)

    def _get_score(self, col: int) -> int:
        """
        :return: The value of a given movement.
        """
        cpp_board = self.__cpp_board + str(col+1)
        self.__solver.stdin.write(str.encode(cpp_board + "\n"))
        self.__solver.stdin.flush()
        out = self.__solver.stdout.readline().decode("utf-8").rstrip()

        # print("get_score:",cpp_board,"=",out)
        if re.match(".*Invalid move.*",out):
            # print("get_score:  winner!")
            return -1000
        score = self.__re_score.match(out).group(1)
        # print("get_score:",cpp_board,"=",score)
        return int(score)
