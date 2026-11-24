#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def ab_minimax(self,position,depth,alpha,beta,maximizingPlayer):
        if depth == 0 or position.game_over: # position.game_over is placeholder
            return position.value

        if maximizingPlayer:
            maxEval = float("-inf")
            for child in position.children:# position.children is placeholder
                eval = self.ab_minimax(child, depth-1, alpha, beta, False)
                maxEval = max(maxEval,eval)
                alpha = max(alpha,eval)
                if beta <= alpha:
                    break
            return maxEval
        else:
            minEval = float("inf")
            for child in position.children:# position.children is placeholder
                eval = self.ab_minimax(child,depth-1,alpha,beta,True)
                minEval = min(minEval,eval)
                beta = min(beta,eval)
                if beta <= alpha:
                    break
            return minEval

    def cell_block(self,row,col,m,n):
        return (row // m , col // n)

    def what_is_used(self,board):
        N = board.m*board.n #Number of rows and cols
        row_used = [set() for _ in range(N)]
        col_used = [set() for _ in range(N)]
        block_used = {}

        for row in range(N):
            for col in range(N):
                    v = board.get((row,col))
                    if v: #value and not empty state
                        row_used[row].add(v)
                        col_used[col].add(v)
                        block_used.setdefault(self.cell_block(row, col, board.m, board.n), set()).add(v)
                        
        return row_used, col_used, block_used

    def playable_cells(self,board):
        pass

    def legal_moves(self,board):
        #would combine all of the other helper functions into one function that shows legal moves
        pass
    
    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

        # Check whether a cell is empty, a value in that cell is not taboo, and that cell is allowed
        def possible(i, j, value):
            return game_state.board.get((i, j)) == SudokuBoard.empty \
                   and not TabooMove((i, j), value) in game_state.taboo_moves \
                       and (i, j) in game_state.player_squares()

        all_moves = [Move((i, j), value) for i in range(N) for j in range(N)
                     for value in range(1, N+1) if possible(i, j, value)]
        move = random.choice(all_moves)
        self.propose_move(move)
        while True: 
            time.sleep(0.2)
            self.propose_move(random.choice(all_moves))

