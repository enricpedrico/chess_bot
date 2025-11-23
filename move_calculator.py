from dataclasses import dataclass, field
from board import Board
import random
from move_generator import MoveGenerator
from evaluator import Evaluator

@dataclass
class MoveCalculator:
    move_generator: MoveGenerator = field(default_factory=MoveGenerator)
    evaluator: Evaluator = field(default_factory=Evaluator)

    def calculate_move(self, board: Board, iter: int = 0, color: str = 'white', MAX_DEPTH = 0) -> tuple[float, list]:
        if iter >= MAX_DEPTH:
            return self.evaluator.get_punctuation(board_obj=board, color='white'), []

        pieces = board.get_pieces(color=color)
        
        best_score = float('-inf') if color == 'white' else float('inf')
        best_path = []
        
        legal_moves_found = False
        
        candidates = []

        for piece in pieces:
            original_pos = piece.position
            moves = self.move_generator.get_legal_moves(board_obj=board, piece=piece)
            
            for move_tuple in moves:
                legal_moves_found = True
                target_row, target_col, move_piece, move_type = move_tuple
                
                captured_piece, old_castling_rights = board.move(move_tuple, start_pos=original_pos)
                
                score, child_path = self.calculate_move(board, iter + 1, self.get_other_color(color), MAX_DEPTH)

                original_piece = piece if move_piece != piece else None
                board.undo_move(move_piece, original_pos, (target_row, target_col), captured_piece, old_castling_rights, original_piece, move_type)

                current_path = [move_tuple] + child_path

                if color == 'white':
                    if score > best_score:
                        best_score = score
                        best_path = current_path
                        candidates = [(score, current_path)]
                    elif score == best_score:
                        candidates.append((score, current_path))
                else:
                    if score < best_score:
                        best_score = score
                        best_path = current_path
                        candidates = [(score, current_path)]
                    elif score == best_score:
                        candidates.append((score, current_path))

        if not legal_moves_found:
            return self.evaluator.get_punctuation(board_obj=board, color='white'), []

        if candidates:
            _, best_path = random.choice(candidates)

        return best_score, best_path

    @staticmethod
    def get_other_color(color: str):
        return 'black' if color == 'white' else 'white'