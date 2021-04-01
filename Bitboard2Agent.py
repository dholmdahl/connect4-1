from game_data import GameData
from agents import Agent
from random import choice

class Bitboard2Agent(Agent):
    """
    Adapted From: https://github.com/nwestbury/pyConnect4
    """
    def __init__(self):
        self.ai = AI("")
        self.other = Human("")
        self.board = None

    @staticmethod
    def get_name() -> str:
        return "BitBoard2"
        
    def get_move(self, game_data: GameData) -> int:
        """ returns a random valid col"""
        # print("--------------------------------- last col:", game_data.last_move_col, "turn:", game_data.turn)
        if game_data.game_board.slots_filled == 0:
            # first move of the game
            self.board = Board(self.ai, self.other)
            col = self.ai.play(self.board)
            self.board.placeToken(col)
            # print("--- first move:",col)
            return col
        if self.board == None:
            self.board = Board(self.other, self.ai)
        # print("board turn",self.board.TURN, "g turn", game_data.turn)

        #play for the opponent
        last_col = game_data.last_move_col[-1]
        result = self.board.placeToken(last_col)
        # print("Prev result:", result)
        col = self.ai.play(self.board)
        if col == None:
            print("No best move!")
            col = choice([c for c in range(7) if data.game_board.is_valid_location(c)])
        self.board.placeToken(col)
        # print("++++++++++++++++++++++++++++++++++++++++++++++++ AI move:",col)
        return col

class Board:
    def __init__(self, p1, p2, tokensize=80):

        width, height = 7, 6  # for now, the width and height will remain fixed

        # self.TOKENSIZE = tokensize
        # self.BOARDWIDTH = width*tokensize
        # self.BOARDHEIGHT = height*tokensize
        # self.WIDTH = width
        # self.HEIGHT = height
        # self.COLOR = (0, 0, 255)
        # self.XMARG = (WINDOW_DIMENSIONS[0] - self.BOARDWIDTH) // 2
        # self.YMARG = WINDOW_DIMENSIONS[1] // 6
        # self.RECT = pygame.Rect(self.XMARG, self.YMARG,
                                # self.BOARDWIDTH, self.BOARDHEIGHT)
        self.TURN = 0

        self.COUNT1 = 0  # player 1 moves
        self.COUNT2 = 0  # player 2 moves

        self.PLAYERS = (p1, p2)
        self.BITBOARDS = [0, 0]

        self.PIECES = []
        for piecex in range(width):
            colTokens = []
            for piecey in reversed(range(height)):
                # t = Piece(piecex, piecey, self)
                colTokens.append(0) #t)
            self.PIECES.append(colTokens)

    # def draw(self, screen):
    #     pygame.draw.rect(screen, self.COLOR, self.RECT)
    #     for col in self.PIECES:
    #         for piece in col:
    #             piece.draw(screen)

    # def play(self, mouseloc=(0, 0)):
    #         chosenCol = -1
    #         player = self.PLAYERS[self.TURN]
    #         if player.isAI:
    #             chosenCol = player.play(self)
    #         else:
    #             chosenCol = player.play(self, mouseloc)

    #         if chosenCol >= 0:
    #             return self.placeToken(chosenCol)

    #         return False

    def placeToken(self, col):
        """
        Argument:
        col : the column number by default an int between [0,6] where a token
        is requested to be placed.

        Return: 1 if the placed token wins the game 2 if draw, 0 otherwise

        """
        if col < 0:  # invalid column
            return False

        pieceCol = self.PIECES[col]
        # print(col,"piece col:",pieceCol)
        y = 0
        for idx, piece in enumerate(pieceCol):
            if not piece: #piece.STATUS:  # if the column has an empty space
                pieceCol[idx] = self.TURN + 1 # piece = piece.setColorToPlayer(self.TURN + 1)
                self.PLAYERS[self.TURN].flipBit(self, self.TURN, col, y)
                return self.endTurn()
            y += 1
        return False  # if the column is full, return False

    def hasWon(self, bitboard):
        # taken from http://stackoverflow.com/q/7033165/1524592
        y = bitboard & (bitboard >> 6)
        if (y & (y >> 2 * 6)):  # check \ diagonal
            return True
        y = bitboard & (bitboard >> 7)
        if (y & (y >> 2 * 7)):  # check horizontal
            return True
        y = bitboard & (bitboard >> 8)
        if (y & (y >> 2 * 8)):  # check / diagonal
            return True
        y = bitboard & (bitboard >> 1)
        if (y & (y >> 2)):  # check vertical
            return True
        return False

    def hasDrawn(self, overall_bitboard):
        """
        If the board has all of its valid slots filled, then it is a draw.
        We mask the board to a bitboard with all positions filled
        (0xFDFBF7EFDFBF) and if all the bits are active, it is a draw.

        """
        return (overall_bitboard & 0xFDFBF7EFDFBF) == 0xFDFBF7EFDFBF

    def endTurn(self):
        """
        This function is called at the end of every turn. It returns 1 on win
        2 on draw

        False otherwise

        """
        if self.hasWon(self.BITBOARDS[self.TURN]):
            return 1

        if self.hasDrawn(self.BITBOARDS[0] | self.BITBOARDS[1]):
            return 2

        self.TURN = not self.TURN

        # add to player move count
        if self.TURN:
            self.COUNT2 += 1
        else:
            self.COUNT1 += 1

        return False

    def isAITurn(self):
        """
        Return True if the AI's turn, this is needed to ignore user clicks made
        during the AI "thinking" phase.
        """

        return self.PLAYERS[self.TURN].isAI

class BasePlayer:
    def __init__(self, name, isAI):
        """
        BasePlayer is inherited by Player.py for Human and AI, it contains
        variables and functions useful to both classes.

        name is the name of the player (e.g. "CPU", "Human")
        isAI is a boolean where or not the player is an AI

        bitboard is a bitboard representation of the board for the given player
        The bitboard representation is like this:
        .  .  .  .  .  .  .  TOP
        5 12 19 26 33 40 47
        4 11 18 25 32 39 46
        3 10 17 24 31 38 45
        2  9 16 23 30 37 44
        1  8 15 22 29 36 43
        0  7 14 21 28 35 42  BOTTOM

        """
        self.name = name
        self.isAI = isAI

    def __repr__(self):
        return str(self.name)

    def flipBit(self, board, p, x, y):
        """
        Flip the bit at the x/y location.
        """
        board.BITBOARDS[p] |= (1 << (x*7 + y))

    def getNthBit(self, num, n):
        """
        Get the nth bit in the bitboard (0 or 1).
        """
        return (num >> n) & 1

    def setNthBit(self, num, n):
        """
        Set the nth bit in the bitboard to 1.
        """
        return num | (1 << n)

    def printBoard(self, board):
        """
        Print the bit board for a single player

        """
        print(">" * 14)
        for i in range(5, -1, -1):  # iterate backwards from 5 to 0.
            row = " ".join(str(self.getNthBit(board, i+x*7)) for x in range(7))
            print(row)
        print("<" * 14)

    def get_legal_locations(self, overall_bitboard):
        """
        Argument:
            overall_bitboard: the combined bitboard for both players (b1 | b2).
            One needs to combine the boards in order to find the top location
            (and check if its empty for a token).

        This function returns a list of tuples for every location that a piece
        could be placed (max of 7). The tuple has two items. The first is the
        column # (0-6) and the second is the bit index for the bitboard (0-42).
        It will returns an empty list when the board is full.

        .  .  .  .  .  .  .  TOP
        5 12 19 26 33 40 47
        4 11 18 25 32 39 46
        3 10 17 24 31 38 45
        2  9 16 23 30 37 44
        1  8 15 22 29 36 43
        0  7 14 21 28 35 42  BOTTOM

        """
        listOfCoords = []
        for i in range(7):  # for every column
            for x in range(i*7, i*7+6):  # for each cell in col, from bot to top
                if not self.getNthBit(overall_bitboard, x):  # get the 1st empty
                    listOfCoords.append((i, x))
                    break
        return listOfCoords

    def get_legal_board(self, overall_bitboard):
        """
        Takes as an argument a combined bitboard for the opponent and player
        and returns a bitboard with all the valid locations set to one.
        """
        board = 0
        for i in range(7):
            for x in range(i*7, i*7+6):
                if not self.getNthBit(overall_bitboard, x):
                    board |= (1 << x)
                    break
        return board

class Human (BasePlayer):
    def __init__(self, name="Human"):
        BasePlayer.__init__(self, name, False)

    # def detectColClick(self, board, mousepos):
    #     if board.RECT.collidepoint(mousepos):  # if click is inside the board
    #         colNumber = (mousepos[0]-board.XMARG)//board.TOKENSIZE
    #         return colNumber
    #     return -1

    def play(self, board, mouseloc):
        # return self.detectColClick(board, mouseloc)
        pass

class AI (BasePlayer):
    def __init__(self, name="CPU"):
        BasePlayer.__init__(self, name, True)

    def evaluate3(self, oppBoard, myBoard):
        """
        Returns the number of possible 3 in a rows in bitboard format.

        Running time: O(1)

        http://www.gamedev.net/topic/596955-trying-bit-boards-for-connect-4/

        """
        inverseBoard = ~(myBoard | oppBoard)
        rShift7MyBoard = myBoard >> 7
        lShift7MyBoard = myBoard << 7
        rShift14MyBoard = myBoard >> 14
        lShit14MyBoard = myBoard << 14
        rShift16MyBoard = myBoard >> 16
        lShift16MyBoard = myBoard << 16
        rShift8MyBoard = myBoard >> 8
        lShift8MyBoard = myBoard << 8
        rShift6MyBoard = myBoard >> 6
        lShift6MyBoard = myBoard << 6
        rShift12MyBoard = myBoard >> 12
        lShift12MyBoard = myBoard << 12

        # check _XXX and XXX_ horizontal
        result = inverseBoard & rShift7MyBoard & rShift14MyBoard\
            & (myBoard >> 21)

        result |= inverseBoard & rShift7MyBoard & rShift14MyBoard\
            & lShift7MyBoard

        result |= inverseBoard & rShift7MyBoard & lShift7MyBoard\
            & lShit14MyBoard

        result |= inverseBoard & lShift7MyBoard & lShit14MyBoard\
            & (myBoard << 21)

        # check XXX_ diagonal /
        result |= inverseBoard & rShift8MyBoard & rShift16MyBoard\
            & (myBoard >> 24)

        result |= inverseBoard & rShift8MyBoard & rShift16MyBoard\
            & lShift8MyBoard

        result |= inverseBoard & rShift8MyBoard & lShift8MyBoard\
            & lShift16MyBoard

        result |= inverseBoard & lShift8MyBoard & lShift16MyBoard\
            & (myBoard << 24)

        # check _XXX diagonal \
        result |= inverseBoard & rShift6MyBoard & rShift12MyBoard\
            & (myBoard >> 18)

        result |= inverseBoard & rShift6MyBoard & rShift12MyBoard\
            & lShift6MyBoard

        result |= inverseBoard & rShift6MyBoard & lShift6MyBoard\
            & lShift12MyBoard

        result |= inverseBoard & lShift6MyBoard & lShift12MyBoard\
            & (myBoard << 18)

        # check for _XXX vertical
        result |= inverseBoard & (myBoard << 1) & (myBoard << 2)\
            & (myBoard << 3)

        return result

    def evaluate2(self, oppBoard, myBoard):
        """
        Returns the number of possible 2 in a rows in bitboard format.

        Running time: O(1)

        """
        inverseBoard = ~(myBoard | oppBoard)
        rShift7MyBoard = myBoard >> 7
        rShift14MyBoard = myBoard >> 14
        lShift7MyBoard = myBoard << 7
        lShift14MyBoard = myBoard << 14
        rShift8MyBoard = myBoard >> 8
        lShift8MyBoard = myBoard << 8
        lShift16MyBoard = myBoard << 16
        rShift16MyBoard = myBoard >> 16
        rShift6MyBoard = myBoard >> 6
        lShift6MyBoard = myBoard << 6
        rShift12MyBoard = myBoard >> 12
        lShift12MyBoard = myBoard << 12

        # check for _XX
        result = inverseBoard & rShift7MyBoard & rShift14MyBoard
        result |= inverseBoard & rShift7MyBoard & rShift14MyBoard
        result |= inverseBoard & rShift7MyBoard & lShift7MyBoard

        # check for XX_
        result |= inverseBoard & lShift7MyBoard & lShift14MyBoard

        # check for XX / diagonal
        result |= inverseBoard & lShift8MyBoard & lShift16MyBoard

        result |= inverseBoard & rShift8MyBoard & rShift16MyBoard
        result |= inverseBoard & rShift8MyBoard & rShift16MyBoard
        result |= inverseBoard & rShift8MyBoard & lShift8MyBoard

        # check for XX \ diagonal
        result |= inverseBoard & rShift6MyBoard & rShift12MyBoard
        result |= inverseBoard & rShift6MyBoard & rShift12MyBoard
        result |= inverseBoard & rShift6MyBoard & lShift6MyBoard
        result |= inverseBoard & lShift6MyBoard & lShift12MyBoard

        # check for _XX vertical
        result |= inverseBoard & (myBoard << 1) & (myBoard << 2) \
            & (myBoard << 2)

        return result

    def evaluate1(self, oppBoard, myBoard):
        """
        Returns the number of possible 1 in a rows in bitboard format.

        Running time: O(1)

        Diagonals are skipped since they are worthless.

        """
        inverseBoard = ~(myBoard | oppBoard)
        # check for _X
        result = inverseBoard & (myBoard >> 7)

        # check for X_
        result |= inverseBoard & (myBoard << 7)

        # check for _X vertical
        result |= inverseBoard & (myBoard << 1)

        return result

    def bitboardBits(self, i):
        """"
        Returns the number of bits in a bitboard (7x6).

        Running time: O(1)

        Help from: http://stackoverflow.com/q/9829578/1524592

        """
        i = i & 0xFDFBF7EFDFBF  # magic number to mask to only legal bitboard
        # positions (bits 0-5, 7-12, 14-19, 21-26, 28-33, 35-40, 42-47)
        i = (i & 0x5555555555555555) + ((i & 0xAAAAAAAAAAAAAAAA) >> 1)
        i = (i & 0x3333333333333333) + ((i & 0xCCCCCCCCCCCCCCCC) >> 2)
        i = (i & 0x0F0F0F0F0F0F0F0F) + ((i & 0xF0F0F0F0F0F0F0F0) >> 4)
        i = (i & 0x00FF00FF00FF00FF) + ((i & 0xFF00FF00FF00FF00) >> 8)
        i = (i & 0x0000FFFF0000FFFF) + ((i & 0xFFFF0000FFFF0000) >> 16)
        i = (i & 0x00000000FFFFFFFF) + ((i & 0xFFFFFFFF00000000) >> 32)

        return i

    def evalCost(self, b, oppBoard, myBoard, bMyTurn):
        """
        Returns cost of each board configuration.

        winning is a winning move
        blocking is a blocking move

        Running time: O(7n)

        """
        winReward = 9999999
        OppCost3Row = 1000
        MyCost3Row = 3000
        OppCost2Row = 500
        MyCost2Row = 500
        OppCost1Row = 100
        MyCost1Row = 100

        if b.hasWon(oppBoard):
            return -winReward
        elif b.hasWon(myBoard):
            return winReward

        get3Win = self.evaluate3(oppBoard, myBoard)
        winning3 = self.bitboardBits(get3Win) * MyCost3Row

        get3Block = self.evaluate3(myBoard, oppBoard)
        blocking3 = self.bitboardBits(get3Block) * -OppCost3Row

        get2Win = self.evaluate2(oppBoard, myBoard)
        winning2 = self.bitboardBits(get2Win) * MyCost2Row

        get2Block = self.evaluate2(myBoard, oppBoard)
        blocking2 = self.bitboardBits(get2Block) * -OppCost2Row

        get1Win = self.evaluate1(oppBoard, myBoard)
        winning1 = self.bitboardBits(get1Win) * MyCost1Row

        get1Block = self.evaluate1(myBoard, oppBoard)
        blocking1 = self.bitboardBits(get1Block) * -OppCost1Row

        return winning3 + blocking3 + winning2 + blocking2\
            + winning1 + blocking1

    def search(self, board, use_alphabeta=True):
        """
        Construct the minimax tree, and get the best move based off the root.

        You have two options to build the tree:
            if use_alphabeta is True:
                alpha beta will be used to construct the tree
            otherwise:
                raw minimax will be used to construct the tree (it may be
            required to lower the maxDepth because it will be slower).
        """
        myBoard = board.BITBOARDS[board.TURN]
        oppBoard = board.BITBOARDS[(not board.TURN)]
        maxDepth = 7

        g = graph(myBoard, oppBoard, maxDepth)  # minimax graph

        if use_alphabeta:
            g.alphabeta(board, self, g.root, maxDepth,
                        float('-inf'), float('inf'))
        else:
            g.construct_tree(board, self, g.root, myBoard, oppBoard, 1)

        return g.getMove()

    def forced_moves(self, board):
        """
        If placing a token can win immediately, return that column.
        Otherwise, if you can block your opponent immediately, return
        one of those column(s).
        """

        myBoard = board.BITBOARDS[board.TURN]
        oppBoard = board.BITBOARDS[(not board.TURN)]
        possibleBits = self.get_legal_locations(myBoard | oppBoard)

        forcedCols = []  # cols needed to block your opponent if you cannot win
        for colbitTuple in possibleBits:
            tempMyBoard = self.setNthBit(myBoard, colbitTuple[1])
            tempOppBoard = self.setNthBit(oppBoard, colbitTuple[1])

            if board.hasWon(tempMyBoard):
                return colbitTuple[0]
            elif board.hasWon(tempOppBoard):
                forcedCols.append(colbitTuple[0])

        if forcedCols:
            return forcedCols[0]
        return -1

    def play(self, board):
        """
        Returns the column to place the piece in.
        """

        forcedColumn = self.forced_moves(board)  # if there is a forced move
        if forcedColumn > -1:
            return forcedColumn  # play it

        return self.search(board)  # otherwise, search the tree 

class graph:
    def __init__(self, myBoard, oppBoard, maxDepth):
        # initiate the first/root node to be at depth 0 and pointing to itself
        rootNode = Node(myBoard, oppBoard, 0, -1, -1)
        self.root = rootNode
        self.maxDepth = maxDepth  # the max depth to consider moves

    def getMove(self):
        """
        This function simply returns the column from the minimax graphs's top
        values. In the case there is more than one column equally-well rated,
        we will the one closest to the center.

        """

        bestvalue = self.root.value
        rootChildren = self.root.children

        # print("Best   value :", bestvalue)
        # print("Column values:", rootChildren)

        bestColumns = [c.col for c in rootChildren if c.value == bestvalue]

        # print("COLS", bestColumns)

        if bestColumns:
            if len(bestColumns) > 1:
                # return the column closest to the center, if they are all
                # equal
                return min(bestColumns, key=lambda x: 3-x)

            else:
                return bestColumns[0]

        return None
        # raise Exception("Failed to find best value")

    def construct_tree(self, b, ai, parentNode, myBoard, oppBoard, depth):
        """
        Likely the most complex function, this builds the tree of possibilities
        by brute forcing through all possible configurations up to a given depth
        (maxDepth). It works by getting the legal locations of where a place can
        be placed, and setting those bits (equivalent to placing a token). Once
        the board is either won or the max depth is reached, we evaluate the
        board. When the function pops out, it creates the value of the parent
        node based on its children values (maxmizing the values if we are
        playing or minimizing if the opponent is playing). On a high level, we
        are presuming both players will play the optimal moves and we want to
        maxmize our reward and minimize the opponent's rewards. We alternate
        back and forth from maximizing and minizming the reward after the
        lowest tree values have been filled.

        tl;dr This function fills a minimax tree.

        The function runs in O(7^d) (d=maxDepth), but the true expansion is
        considerably less than this after the move # + depth >= 4, because we
        stop branches where there is a win and all seven columns are not
        necessarily available.

        """
        bMyTurn = (depth % 2 == 1)

        possibleBits = ai.get_legal_locations(myBoard | oppBoard)
        childrenNodes = []

        for colbitTuple in possibleBits:
            won = False
            col = colbitTuple[0]

            if bMyTurn:  # it's my turn, so add to my board
                tmpMyBoard = ai.setNthBit(myBoard, colbitTuple[1])
                tmpOppBoard = oppBoard
                won = b.hasWon(tmpMyBoard)
            else:  # it's the oppnent's turn, so we simulate their move
                tmpMyBoard = myBoard
                tmpOppBoard = ai.setNthBit(oppBoard, colbitTuple[1])
                won = b.hasWon(tmpOppBoard)

            myNode = Node(tmpMyBoard, tmpOppBoard, depth, parentNode, col)

            # stop expanding the branch if the game is won | max depth = reached
            if won or depth == self.maxDepth:
                myNode.value = ai.evalCost(b, tmpOppBoard, tmpMyBoard, bMyTurn)
            else:
                self.construct_tree(b, ai, myNode,
                                    tmpMyBoard, tmpOppBoard, depth+1)
                myNode.setValueFromChildren()

            childrenNodes.append(myNode)

        parentNode.children = childrenNodes
        parentNode.setValueFromChildren()

    def createNodeChildren(self, ai, node):
        """
        This function will look at all the possible locations you can play
        pieces and create their respective nodes. After this list of nodes is
        created it is added to the inital's node class variable children.
        """
        bMyTurn = node.depth % 2
        possibleBits = ai.get_legal_locations(node.myBoard | node.oppBoard)
        childrenNodes = []
        for colbitTuple in possibleBits:
            col = colbitTuple[0]
            if bMyTurn:
                tmpMyBoard = ai.setNthBit(node.myBoard, colbitTuple[1])
                tmpOppBoard = node.oppBoard
            else:
                tmpMyBoard = node.myBoard
                tmpOppBoard = ai.setNthBit(node.oppBoard, colbitTuple[1])
            childNode = Node(tmpMyBoard, tmpOppBoard, node.depth+1, node, col)
            childrenNodes.append(childNode)
        node.children = childrenNodes

    def alphabeta(self, b, ai, node, depth, alpha, beta):
        """
        Constructs the tree using alphabeta, this is quite similar to the raw
        minimax used in the construct tree, however it is considerably faster
        because it removes branches that cannot be used. Simply put, it takes
        advantage of the minimax's attribute to maxmize and then minimize the
        nodes' values. For instance, if you have a bottom value of 5 and find
        a value of -100 at the bottom, you can ignore the entire branch because
        you know it will be minizmized before reaching the top.

        On my laptop, this equates to an increase from depth 5 to 7 for a max
        wait of ~2 seconds over non-optimized minimax.
        """
        isTurn = node.depth % 2 == 0  # if it's the AI's turn, we should maxmize
        if depth == 0 or node.depth == self.maxDepth:
            if node.value is None:
                node.value = ai.evalCost(b, node.myBoard, node.oppBoard, isTurn)
            return node.value

        self.createNodeChildren(ai, node)
        if isTurn:
            v = float('-inf')
            for child in node.children:
                v = max(v, self.alphabeta(b, ai, child, depth-1, alpha, beta))
                alpha = max(alpha, v)
                if node.value is None or alpha > node.value:
                    node.value = alpha
                if beta <= alpha:
                    node.value = None
                    break
            return v
        else:
            v = float('inf')
            for child in node.children:
                v = min(v, self.alphabeta(b, ai, child, depth-1, alpha, beta))
                beta = min(beta, v)
                if node.value is None or beta < node.value:
                    node.value = beta
                if beta <= alpha:
                    node.value = None
                    break
            return v


class Node:
    def __init__(self, myBoard, oppBoard, depth, parentNode, col, value=None):
        self.myBoard = myBoard
        self.oppBoard = oppBoard
        self.value = value
        self.depth = depth
        if depth == 0:  # if the node is the root
            self.parent = self  # set the parent node to itself
        else:
            self.parent = parentNode
        self.children = []
        self.col = col

    def setValueFromChildren(self):
        """
        Get the value of a node based on its children, minimizing if value if
        it's the opponent turn or maxmizing if it's before my turn.
        """
        if self.children and self.value is None:
            if self.depth % 2:
                self.value = min(c.value for c in self.children)
            else:
                self.value = max(c.value for c in self.children)
            return self.value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, node):
        return self.value == node.value

    def __lt___(self, node):
        return self.value < node.value

    def __gt__(self, node):
        return self.value > node.value
