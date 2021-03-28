from random import choice
from copy import deepcopy
from game_data import GameData
from agents import Agent

import random
import math
import copy
import time

from numpy import flip, zeros

class MonteCarloAgent(Agent):
    """
    Adapted From: https://github.com/Alfo5123/Connect4
    """
    def __init__(self, depth=5):
        board = [] 
        for i in range(6):
            row = []
            for j in range(7):
                row.append(0)
            board.append(row)

        self.mc_board = Board( board )

    @staticmethod
    def get_name() -> str:
        return "MonteCarlo"
        
    def get_move(self, game_data) -> int:
        """ returns a random valid col"""
        gd_board = game_data.game_board.board
        mc_board = self.mc_board.board
        conv_board(gd_board, mc_board)
        # print("GD Board:")
        # print_board(gd_board)
        # print("MC Board:")
        # print_board(mc_board)
        column = self.findBestMove(2.0)
        # print("column",column)
        return column

    def findBestMove(self , factor )-> int:
    # Returns the best move using MonteCarlo Tree Search
        orig_mc_arr = copy.deepcopy (self.mc_board.board)
        o = Node(self.mc_board)
        bestMove = MTCS( 3000, o, factor )
        self.mc_board = copy.deepcopy( bestMove.state )

        # print_board(self.mc_board.board)

        #find col
        column = -1
        for row in range(6):
            for col in range(7):
                if orig_mc_arr[row][col] != self.mc_board.board[row][col]:
                    column=col
        return column

def conv_board(gd_board: list, mc_board: list):
    """
    Convert from game data style board to MC style board
    The MC analysis was from a program that uses a different board style
    """
    # convert in place
    #-1 is player 1, 1 is player 2, 0 is empty
    #out 1 is player 1, 2 is player 2, 0 is empty
    for i in range(6):
        for j in range(7):
            gd_val = gd_board[i][j]
            if gd_val == 0:
                mc_board[5-i][j] = 0
            elif gd_val == 1:
                mc_board[5-i][j] = -1
            else:
                mc_board[5-i][j] = 1

def print_board(board: list):
    """
    Prints the state of the board to the console.
    """
    print(flip(board, 0))
    print(" ---------------------")
    print(" " + str([1, 2, 3, 4, 5, 6, 7]))

## Game basic dynamics
class Board(object):
    
    def __init__(self, board , last_move = [ None , None ] ):
        self.board = board 
        self.last_move = last_move
        self.dx = [ 1, 1,  1,  0 ]
        self.dy = [ 1, 0,  -1,  1  ]

    def tryMove(self, move):
        # Takes the current board and a possible move specified 
        # by the column. Returns the appropiate row where the 
        # piece and be located. If it's not found it returns -1.

        if ( move < 0 or move > 7 or self.board[0][move] != 0 ):
            return -1

        for i in range(len(self.board)):
            if ( self.board[i][move] != 0 ):
                return i-1
        return len(self.board)-1

    def terminal(self):
       # Returns true when the game is finished, otherwise false.
        for i in range(len(self.board[0])):
            if ( self.board[0][i] == 0 ):
                return False
        return True

    def legal_moves(self):
        # Returns the full list of legal moves that for next player.
        legal = []
        for i in range(len(self.board[0])):
            if( self.board[0][i] == 0 ):
                legal.append(i)

        return legal

    def next_state(self, turn):
        # Retuns next state
        aux = copy.deepcopy(self)
        moves = aux.legal_moves()
        if len(moves) > 0 :
            ind = random.randint(0,len(moves)-1)
            row = aux.tryMove(moves[ind])
            aux.board[row][moves[ind]] = turn
            aux.last_move = [ row, moves[ind] ]
        return aux 

    def winner(self):
        # Takes the board as input and determines if there is a winner.
        # If the game has a winner, it returns the player number (Computer = 1, Human = -1).
        # If the game is still ongoing, it returns zero.  

        x = self.last_move[0]
        y = self.last_move[1]

        if x == None:
            return 0 

        for d in range(4):

            h_counter = 0
            c_counter = 0

            for k in range(-3,4):

                u = x + k * self.dx[d]
                v = y + k * self.dy[d]

                if u < 0 or u >= 6:
                    continue

                if v < 0 or v >= 7:
                    continue

                if self.board[u][v] == -1:
                    c_counter = 0
                    h_counter += 1
                elif self.board[u][v] == 1:
                    h_counter = 0
                    c_counter += 1
                else:
                    h_counter = 0
                    c_counter = 0

                if h_counter == 4:
                    return -1 

                if c_counter == 4:  
                    return 1

        return 0


class Node():
# Data structure to keep track of our search
    def __init__(self, state, parent = None):
        self.visits = 1 
        self.reward = 0.0
        self.state = state
        self.children = []
        self.children_move = []
        self.parent = parent 

    def addChild( self , child_state , move ):
        child = Node(child_state,self)
        self.children.append(child)
        self.children_move.append(move)

    def update( self,reward ):
        self.reward += reward 
        self.visits += 1

    def fully_explored(self):
        if len(self.children) == len(self.state.legal_moves()):
            return True
        return False

def MTCS( maxIter , root , factor ):
    for _ in range(maxIter):
        front, turn = treePolicy( root , 1 , factor )
        reward = defaultPolicy(front.state, turn)
        backup(front,reward,turn)

    ans = bestChild(root,0)
    # print([(c.reward/c.visits) for c in ans.parent.children ])
    return ans


def treePolicy( node, turn , factor ):
    while node.state.terminal() == False and node.state.winner() == 0:
        if ( node.fully_explored() == False ):
            return expand(node, turn), -turn
        else:
            node = bestChild ( node , factor )
            turn *= -1
    return node, turn

def expand( node, turn ):
    tried_children_move = [m for m in node.children_move]
    possible_moves = node.state.legal_moves()

    for move in possible_moves:
        if move not in tried_children_move:
            row = node.state.tryMove(move)
            new_state = copy.deepcopy(node.state)
            new_state.board[row][move] = turn 
            new_state.last_move = [ row , move ]
            break

    node.addChild(new_state,move)
    return node.children[-1]

def bestChild(node,factor):
    bestscore = -10000000.0
    bestChildren = []
    for c in node.children:
        exploit = c.reward / c.visits
        explore = math.sqrt(math.log(2.0*node.visits)/float(c.visits))
        score = exploit + factor*explore
        if score == bestscore:
            bestChildren.append(c)
        if score > bestscore:
            bestChildren = [c]
            bestscore = score 
    return random.choice(bestChildren)

def defaultPolicy( state, turn  ):
    while state.terminal()==False and state.winner() == 0 :
        state = state.next_state( turn )
        turn *= -1
    return  state.winner() 

def backup( node , reward, turn ):
    while node != None:
        node.visits += 1 
        node.reward -= turn*reward
        node = node.parent
        turn *= -1
    return
