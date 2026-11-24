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

    def evaluate_state():
        """
        A function that evaluates a state based on the differences in points of the players

        """
        pass

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

        # Check whether a cell is empty, a value in that cell is not taboo, and that cell is allowed
        def possible(i, j, value):
            return (
                game_state.board.get((i, j)) == SudokuBoard.empty
                and not TabooMove((i, j), value) in game_state.taboo_moves
                and (i, j) in game_state.player_squares()
            )

        # So we can just reuse the possible move, and reuse all moves
        all_moves = [
            Move((i, j), value)
            for i in range(N)
            for j in range(N)
            for value in range(1, N + 1)
            if possible(i, j, value)
        ]
        # The move here should not be random but be determined based on its score
        # Calculated as e.g. difference in scores.
        # We can make player 1 us as max player and player 2 as min
        # Each node will include the value which is either positive or negative
        # If positive thats good for the max player
        # If negative than good for the min player
        move = random.choice(all_moves)
        self.propose_move(move)
        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(all_moves))
