from random import randint

class Connect4():

    def __init__(self):
        """
        Initialize game board.
        Each game board has
            - `board`: the current state of the game.
        """
        self.board = [0 for sq in range(42)]

    def player(self, state):
        return 2 if state.count(1) > state.count(2) else 1

    def actions(self, state):
        """
        Takes a `state` list as input
        and returns all of the available actions [`i`, `i`, `i`, ...] in that state.

        Action `i` represents placing a chip in `i` column.
        """
        return [sn for sn in range(7) if state[sn] == 0]

    def is_tie(self, state):
        """
        Check if the current state of `board` is tie.
        """
        return len([sq for sq in state if sq == 0]) == 0

    def terminal(self, state):
        """
        Check if the current state of `board` is terminal.
        """
        row = 0
        for sq in range(42):
            if sq % 7 == 0:
                row += 1

            distance_to_new_row = 7 * row - (sq + 1)
            distance_to_column_end = [i for i in range(6) if (sq + 1) + i * 7 > 35][0]

            if state[sq] == 0:
                continue

            # 4 horizontally
            if distance_to_new_row >= 3 and state[sq] == state[sq + 1] and state[sq] == state[sq + 2] and state[sq] == state[sq + 3]:
                return True
            # 4 vertically
            elif distance_to_column_end > 2 and state[sq] == state[sq + 7] and state[sq] == state[sq + 14] and state[sq] == state[sq + 21]:
                return True
            # 4 diagonally
            elif distance_to_new_row >= 3 and distance_to_column_end >= 2 and sq + 24 < len(state) and state[sq] == state[sq + 8] and state[sq] == state[sq + 16] and state[sq] == state[sq + 24]:
                return True
            elif distance_to_new_row >= 3 and distance_to_column_end <= 2 and 0 <= sq - 18 < len(state) and state[sq] == state[sq - 6] and state[sq] == state[sq - 12] and state[sq] == state[sq - 18]:
                return True

        return self.is_tie(state)

    def result(self, state, action):
        """
        Return the result of `action` for the current player.
        `action` must be an int `i`.
        """

        result = state[:]

        for r in range(6):
            current_sq = action + 35 - r * 7
            if result[current_sq] == 0:
                result[action + 35 - r * 7] = self.player(state)
                break

        return result

    def print_state(self, state):
        """
        Print the current `state` of the board.
        """

        for l in range(0, 42, 7):
            row = ''.join([f"{state[l + i]}|" for i in range(7)])
            print(row[:13])
            print('-+-+-+-+-+-+-')

    def play(self, opponent=None, human=randint(1, 2), agent_battle=False):
        """
        Play against another human or AI `opponent`, human starts with turn `human`.
        """

        opponent_name = opponent.get_name() if opponent else None

        while True:

            self.print_state(self.board)

            player = self.player(self.board)
            actions = self.actions(self.board)

            if not agent_battle and (not opponent or player == human):
                print(f"Player {player}'s Move.")

                while True:
                    column = int(input().strip()) - 1
                    
                    if not column in actions:
                        print('That place is already filled or invalid. Still your move.')
                    else:
                        break

            elif opponent:
                print(f"{opponent_name}'s Move.")

                column = opponent.choose_action(self.board)

                print(f"{opponent_name} put a chip in column {column + 1}.")

            # update board
            self.board = self.result(self.board, column)

            # check if game over
            winner = player if self.terminal(self.board) else None 
            if winner:
                self.print_state(self.board)

                print("\nGAME OVER\n")
                print(f"Winner is player {player}")

                break
                
        if input("Play again?\n").lower() == "y":
            self.board = [0 for sq in range(42)]
            self.play(opponent=opponent, human=human, agent_battle=agent_battle)

if __name__ == "__main__":
    connect4 = Connect4()

    connect4.play()