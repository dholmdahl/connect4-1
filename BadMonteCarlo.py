import time
from random import choice
from math import log, sqrt
import numpy as np

from text_connect4 import Connect4
from agents import Agent

class BadMonteCarlo(Connect4, Agent):
    def __init__(self, max_time=1, max_moves=200, C=1.2):

        # get and set optional arguments
        self.max_time = max_time
        self.max_moves = max_moves
        self.C = C

        # define neccesary data structures for MCTS
        self.wins = {}
        self.plays = {}

    def get_name(self):
        return "MonteCarlo"

    def get_move(self, game_state):
        """
        Choose action based of state `state` using MCTS algorithm.
        """

        # conversion
        c4_rows = []
        for row in list(game_state.game_board):
            c4_rows.append(row[::-1])

        state = list(np.concatenate(c4_rows).flat)[::-1]

        actions = self.actions(state)

        # why calculate for just one action?
        if len(actions) == 1:
            return actions[0]

        # simulations = 0
        start_time = time.time()

        while time.time() - start_time < self.max_time:
            self.run_simulation(state)

            # if simulations % 1000 == 0:
            #     print(f"{simulations} simulations played.", end="\r")

            # print(f"{simulations} simulations played.", end="\r")

            # simulations += 1

        print()

        action_states = [(tuple(state), a) for a in actions]

        # print(f"action_states: {action_states}.")

        best_m = actions[0]
        best_p = 0
        for s, a in action_states:
            # log_total = log(sum([self.plays.get((s, a), 1) for s, a in action_states]))

            p = self.wins.get((s, a), 0) / self.plays.get((s, a), 1)
            # p = self.wins.get((s, a), 0) / self.plays.get((s, a), 1) + self.C * sqrt(log_total / self.plays.get((s, a), 1))

            print(f"Number of wins: {self.wins.get((s, a), 0)}")
            print(f"Number of plays: {self.plays.get((s, a), 1)}")
            print(f"Win probability for action {a} is {p}.\n")

            if p > best_p:
                best_p = p
                best_m = a

        return best_m

    def run_simulation(self, state):
        """
        Run MCTS simulation ...
        """

        # get ai player number
        ai = self.player(state)
        
        visited_states = set()

        local_state = state

        # expand node `state` to depth of max_moves
        for depth in range(self.max_moves + 1):
            # get actions for current state
            actions = self.actions(local_state)
            # get player for current state
            player = self.player(local_state)

            action_states = [(tuple(state), a) for a in actions]

            # current best move is unkown for now
            best_m = choice(actions)

            for action in actions:
                if self.terminal(self.result(local_state, action)):
                    best_m = action
                    break
            # check if all legal moves are in plays
            else:
                # if we have stats on all legal moves use them
                if all(self.plays.get((s, a)) for s, a in action_states):
                    # b must be raised to produce x, one input because b does not have to be specified
                    log_total = log(sum([self.plays[(s, a)] for s, a in action_states]))
                    
                    # find best move `best_m` for state `local_state` using UCB1
                    best_p = 0
                    for s, a in action_states:

                        p = self.wins[(s, a)] / self.plays[(s, a)] + self.C * sqrt(log_total / self.plays[(s, a)])
                        # p = self.wins.get((s, a), 0) / self.plays.get((s, a), 1)

                        # print(f"Result of UCB1 formula for action {a} is {p}.")
                        if p > best_p:
                            best_p = p
                            best_m = a

            if (tuple(local_state), best_m) not in self.plays:

                # setup state and player value in dictonaries
                self.plays[(tuple(local_state), best_m)] = 1
                self.wins[(tuple(local_state), best_m)] = 0

            visited_states.add((tuple(local_state), best_m))

            # set local board to be the result of the best move
            local_state = self.result(local_state, best_m)

            winner = player if self.terminal(local_state) else None

            if winner:
                break

        # update statistics
        for s, a in visited_states:
            # you can't update something that's not there
            if (s, a) not in self.plays:
                continue

            # add to plays for every state visited
            self.plays[(tuple(s), a)] += 1

            # add to wins if AI won
            if ai == winner:
                self.wins[(tuple(s), a)] += 1