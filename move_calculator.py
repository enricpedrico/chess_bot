from dataclasses import dataclass
from objects.board import Board

@dataclass
class MoveCalculator:
    def calculate_move(self, board: Board, iter: int = 0, color: bool = bool(iter % 2), MAX_DEPTH = 0):
        legal_moves = []
        for piece in board.get_pieces(color=color):
            for move_tuple in board.get_legal_moves(piece=piece):
                legal_moves.append((board.move(move=move_tuple), 
                                    move_tuple))
        
        if iter >= MAX_DEPTH: # BASE CASE
            return max([(board.get_punctuation(color=color), move_tuple) 
                        for board, move_tuple in legal_moves])
        
        responses = []
        for move in legal_moves:
            punctuation, move_tuple = self.calculate_move(board=move[0], iter=iter+1, color=color, MAX_DEPTH=MAX_DEPTH)
            responses.append((punctuation,
                              move_tuple))

        return min(responses)
