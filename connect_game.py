import math
import os
import sys

import pygame
from typing import List
from random import choice

from config import black
from events import GameOver, MouseClickEvent, PieceDropEvent, bus
from game_data import GameData
from game_renderer import GameRenderer
from agents import Agent

import time

class ConnectGame:
    """
    Holds all of the game logic and game data.
    """

    game_data: GameData
    renderer: GameRenderer

    def __init__(self, game_data: GameData, renderer: GameRenderer):
        """
        Initializes the connect game.
        :param game_data: A reference to the game data object.
        :param renderer: A reference to the game renderer.
        """
        self.game_data = game_data
        self.renderer = renderer

    def quit(self):
        """
        Exits the game.
        """
        sys.exit()

    @bus.on("mouse:click")
    def mouse_click(self, event: MouseClickEvent):
        """
        Handles a mouse click event.
        :param event: Data about the mouse click
        """
        pygame.draw.rect(
            self.renderer.screen,
            black,
            (0, 0, self.game_data.width, self.game_data.sq_size),
        )

        col: int = int(math.floor(event.posx / self.game_data.sq_size))

        self.make_movement(col)

    @bus.on("game:undo")
    def undo(self):
        """
        Handles the Ctrl+Z keyboard sequence, which
        is used to roll back the last move.
        """
        if self.game_data.last_move_row:

            self.game_data.last_move_row.pop()
            self.game_data.last_move_col.pop()

            self.game_data.game_board.slots_filled -= 1
            self.game_data.turn += 1
            self.game_data.turn = self.game_data.turn % 2

    def make_movement(self, col: int, name=None):
        """
        Allows to make a movement without a mouse click.
        Inserts a new piece in the specified column and prints the new board.
        """
        assert(col is not None)
        if self.game_data.game_board.is_valid_location(col):
            row: int = self.game_data.game_board.get_next_open_row(col)

            self.game_data.last_move_row.append(row)
            self.game_data.last_move_col.append(col)
            self.game_data.game_board.drop_piece(row, col, self.game_data.turn + 1)

            self.draw()

            bus.emit(
                "piece:drop", PieceDropEvent(self.game_data.game_board.board[row][col])
            )

            self.print_board()

            if self.game_data.game_board.winning_move(self.game_data.turn + 1, row, col):
                print("Game over:", name)
                bus.emit(
                    "game:over", self.renderer, GameOver(False, self.game_data.turn + 1, name)
                )
                self.game_data.game_over = True

            pygame.display.update()

            self.game_data.turn += 1
            self.game_data.turn = self.game_data.turn % 2

    @staticmethod
    def play_game(player1: Agent, player2: Agent) -> int:
        """
        Agent1 plays first, agent2 plays second
        :param player1: an AI agent
        :param player2: an AI agent
        :returns: the winner; 1 = agent1, 2 = agent2, 0 = tie
        """
        data = GameData()
        board = data.game_board
        time_p1 = time_p2 = 0
        while True:
            start = time.process_time()
            col = player1.get_move(data)
            time_p1 += time.process_time() - start
            row = board.get_next_open_row(col)
            board.drop_piece(row, col, 1)
            if board.winning_move(1, row, col):
                return 1, time_p1, time_p2

            data.turn += 1
            data.turn = data.turn % 2

            start = time.process_time()
            col = player2.get_move(data)
            time_p2 += time.process_time() - start
            row = board.get_next_open_row(col)
            board.drop_piece(row, col, 2)

            if board.winning_move(2, row, col):
                return 2, time_p1, time_p2

            if board.tie_move():
                return 0, time_p1, time_p2

    @staticmethod
    def compare_agents(agent1: Agent, agent2: Agent, n=5, alternate=True, print_progress=True) -> List[int]:
        """
        The 2 given agents will play between them n times. The games are not showed.
        :param agent1: an AI agent
        :param agent2: an AI agent
        :param n: number of matches
        :param alternate: if True player1 and player2 will play first the same number of times
        :returns: number of [ties, player1 wins, player2 wins]
        """
        print(f"Compare {agent1.get_name()} to {agent2.get_name()} with {n} games")
        stats = [0, 0, 0]
        time_p1 = time_p2 = 0
        completed_games = 0
        if alternate:
            if n % 2 != 0:
                if choice([1, 2]) == 1:
                    winner, tp1, tp2 = ConnectGame.play_game(agent1, agent2)
                    time_p1 += tp1
                    time_p2 += tp2
                    stats[winner] += 1
                    completed_games += 1
                    if print_progress:
                        print(f"finished games 1: {completed_games}/{n}")
                        print("current stats [d, p1 wins, p2 wins]:", stats, ", t1=", time_p1, ", t2=", time_p2)
                else:
                    winner, tp2, tp1 = ConnectGame.play_game(agent2, agent1)
                    time_p1 += tp1
                    time_p2 += tp2
                    completed_games += 1
                    if winner == 1:
                        stats[2] += 1
                    elif winner == 2:
                        stats[1] += 1
                    else:
                        stats[0] += 1

                    if print_progress:
                        print(f"finished games 2: {completed_games}/{n}")
                        print("current stats [d, p1 wins, p2 wins]:", stats, ", t1=", time_p1, ", t2=", time_p2)

            for _ in range(n // 2):
                winner, tp1, tp2 = ConnectGame.play_game(agent1, agent2)
                time_p1 += tp1
                time_p2 += tp2
                stats[winner] += 1
                completed_games += 1
                if print_progress:
                    print(f"finished games 3: {completed_games}/{n}")
                    print("current stats [d, p1 wins, p2 wins]:", stats, ", t1=", time_p1, ", t2=", time_p2)

                winner, tp2, tp1 = ConnectGame.play_game(agent2, agent1)
                time_p1 += tp1
                time_p2 += tp2
                completed_games += 1
                if winner == 1:
                    stats[2] += 1
                elif winner == 2:
                    stats[1] += 1
                else:
                    stats[0] += 1

                if print_progress:
                    print(f"finished games 4: {completed_games}/{n}")
                    print("current stats [d, p1 wins, p2 wins]:", stats, ", t1=", time_p1, ", t2=", time_p2)
        else:
            for _ in range(n):
                winner, tp1, tp2 = ConnectGame.play_game(agent1, agent2)
                time_p1 += tp1
                time_p2 += tp2
                completed_games += 1
                stats[winner] += 1
                if print_progress:
                    print(f"finished games 5: {completed_games}/{n}")
                    print("current stats [d, p1 wins, p2 wins]:", stats)

        print(f"{agent1.get_name()} {stats[1]} to {agent2.get_name()} {stats[2]} with {stats[0]} ties in {n} games.  Time {agent1.get_name()}={time_p1}, time {agent2.get_name()}={time_p2}.")

        return stats

    def update(self):
        """
        Checks the game state, dispatching events as needed.
        """
        if self.game_data.game_board.tie_move():
            bus.emit("game:over", self.renderer, GameOver(was_tie=True))

            self.game_data.game_over = True

        if self.game_data.game_over:
            pygame.time.wait(1000)

    def draw(self):
        """
        Directs the game renderer to 'render' the game state to the audio and video devices.
        """
        self.renderer.draw(self.game_data)

    def print_board(self):
        """
        Prints the state of the board to the console.
        """
        self.game_data.game_board.print_board()
