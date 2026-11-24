#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
import copy
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def is_game_over(self, state: GameState) -> bool:
        """
        The game is over if every square has been filled and if not both players are stuck.
        This does not tell us who won only that there is still moves to play because the game
        did not finish.
        """
        if SudokuBoard.empty not in state.board.squares:
            return True
        return not self.can_move(state, 1) and not self.can_move(state, 2)

    def legal_moves(self, state: GameState) -> list:
        """
        All moves the current player may play under the competitive sudoku rules:
        the square is empty and allowed for this player, the value does not already
        appear in the square's row, column or block, and the move is not taboo.
        """
        board = state.board
        # Get board total size, amount of rows and columns
        N, m, n = board.N, board.m, board.n

        # values already used in every row, column and block
        rows = [set() for _ in range(N)]
        cols = [set() for _ in range(N)]
        blocks = {}
        # Get each squares value
        for k, v in enumerate(board.squares):
            # If the value of the square is not empty than add to
            if v != SudokuBoard.empty:
                r, c = board.index2square(k)
                rows[r].add(v)  # Add the value to the corresponding row
                cols[c].add(v)  # Add the value to corresponding columns
                blocks.setdefault((r // m, c // n), set()).add(
                    v
                )  # Add the value to corresponding block

        squares = (
            state.player_squares()
        )  # empty allowed squares the player can play on based on the rules

        taboo = {(t.square, t.value) for t in state.taboo_moves}  # All taboo moves
        moves = []
        for r, c in squares:
            used = (
                rows[r] | cols[c] | blocks.get((r // m, c // n), set())
            )  # all values that cannot be played anymore in the square
            for value in range(1, N + 1):  # Check values between 1 - N + 1
                if (
                    value not in used and ((r, c), value) not in taboo
                ):  # If correct move add to moves
                    moves.append(Move((r, c), value))
        return moves

    def can_move(self, state: GameState, player: int) -> bool:
        """
        Returns if the player has moves that it can make.

        """
        saved = state.current_player
        state.current_player = player
        has_move = len(self.legal_moves(state)) > 0
        state.current_player = saved
        return has_move

    def is_loss(self, state: GameState, player: int) -> bool:
        """Checks if the player loses in a state, dynamic based on which player we are curious of"""
        if not self.is_game_over(state):
            return False
        return state.scores[player - 1] < state.scores[2 - player]

    def move_reward(self, board, square, value) -> int:
        """GameState does not have its own function to check what reward we could get if a
        moved is played. This function gives back the potential reward of a move.

        """
        N, m, n = board.N, board.m, board.n
        r, c = square
        board.put(square, value)  # place the value temporarily

        row_done = all(
            board.get((r, j)) != SudokuBoard.empty for j in range(N)
        )  # Does this move make any row finished?
        col_done = all(
            board.get((i, c)) != SudokuBoard.empty for i in range(N)
        )  # Does this row make any column finished?

        # E.g.: if board 9x9 and m = 3, n = 3. The square (4,7) will be in the block row 1
        # and block col 2. The first square of the block (1,2) is for this is (3,6)
        br, bc = (r // m) * m, (c // n) * n  #    top-left corner of the square's block
        block_done = all(
            board.get((br + i, bc + j)) != SudokuBoard.empty  # Each square in the block
            for i in range(m)
            for j in range(n)
        )  #    checks each positions of the block

        board.put(square, SudokuBoard.empty)  # undo so the board is unchanged
        return [0, 1, 3, 7][
            row_done + col_done + block_done
        ]  # return 0, 1, 3, 7 based on how many did the move complete

    def children(self, state):
        """
        Calculates the score for all the moves that in the current state a player can make.
        It gets a move and create a copy of it. Then calculates the score of the move and
        makes the move of the copied state. Changes the current layer to the next one.
        Important this does not just the true game state. Its used only to calculate future moves.
        Each state is copied so its not very memory efficient.

        """
        result = []
        for move in self.legal_moves(state):
            child = copy.deepcopy(state)
            p = child.current_player
            child.scores[p - 1] += self.move_reward(
                child.board, move.square, move.value
            )
            child.board.put(move.square, move.value)
            if child.occupied_squares1 is not None:
                child.occupied_squares().append(move.square)
            child.current_player = 3 - p
            result.append(child)

        if not result:  # this player is stuck: they're skipped, the opponent moves
            child = copy.deepcopy(state)
            child.current_player = 3 - state.current_player
            result.append(child)
        return result

    def evaluate_state(self, state: GameState, player: int):
        """
        A function that evaluates a state based on the differences in points of the players.
        Making loss moves the worst and winning moves the best.

        """
        opp = 3 - player
        score_diff = state.scores[player - 1] - state.scores[opp - 1]
        if self.is_loss(state, player):
            score_diff -= 1000  # if the player losses in that state
        elif self.is_loss(state, opp):
            score_diff += 1000  # if the opponent losses in that state
        return score_diff

    def ab_minimax(self, state, depth, alpha, beta, me):
        if depth == 0 or self.is_game_over(
            state
        ):  # check if we reached leaf nodes and if the game is over in that state
            return self.evaluate_state(state, me)

        children = self.children(state)  # Get all the children of the state

        if state.current_player == me:
            maxEval = float("-inf")
            for child in children:
                eval = self.ab_minimax(child, depth - 1, alpha, beta, me)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval
        else:
            minEval = float("inf")
            for child in children:  #
                eval = self.ab_minimax(child, depth - 1, alpha, beta, me)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval

    def compute_best_move(self, game_state: GameState) -> None:
        me = game_state.current_player
        # We want to propose a move so that we do not get insta loss
        moves = self.legal_moves(game_state)
        self.propose_move(random.choice(moves))
        for depth in range(
            1, 100
        ):  # iterative deepening: keep the best move found so far
            best_val, best_move = float("-inf"), None
            for move, child in zip(
                self.legal_moves(game_state), self.children(game_state)
            ):
                val = self.ab_minimax(child, depth - 1, float("-inf"), float("inf"), me)
                if val > best_val:
                    best_val, best_move = val, move
            if best_move:
                self.propose_move(best_move)
