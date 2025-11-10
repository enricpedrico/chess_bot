from dataclasses import dataclass
from objects.board import Board
from copy import deepcopy
import random

@dataclass
class MoveCalculator:
    def calculate_move(self, board: Board, iter: int = 0, color: str = 'white', MAX_DEPTH = 0) -> tuple[float, tuple]:
        legal_moves = []
        for piece in board.get_pieces(color=color):
            for move_tuple in board.get_legal_moves(piece=piece):
                new_board = deepcopy(board)

                old_row, old_col = piece.position
                copied_piece = new_board.board[old_row][old_col]

                copied_move = (move_tuple[0], move_tuple[1], copied_piece, move_tuple[3])

                new_board.move(copied_move)

                legal_moves.append((new_board, copied_move))
        
        if iter >= MAX_DEPTH: # BASE CASE
            return self.choose_random(function=max, legal_moves=legal_moves, color=color)
        
        responses = []
        for move in legal_moves:
            punctuation, move_tuple = self.calculate_move(board=move[0],
                                                          iter=iter+1,
                                                          color=self.get_other_color(color),
                                                          MAX_DEPTH=MAX_DEPTH)
            responses.append((punctuation,
                              move_tuple))

        return self.choose_random(function=min, legal_moves=responses, color=self.get_other_color(color))


    @staticmethod
    def choose_random(function, legal_moves: list[tuple[Board, tuple]], color: str) -> tuple[Board, tuple]:
        if not legal_moves:
            print('NO LEGAL MOVES')
            return None

        scores = [(board.get_punctuation(color=color), board, move) for board, move in legal_moves]

        best_value = function(score for score, _, _ in scores)

        best_moves = [(board, move) for score, board, move in scores if score == best_value]

        chosen_move = random.choice(best_moves)

        return chosen_move

    
    @staticmethod
    def get_other_color(color: str):
        return 'black' if color == 'white' else 'white'