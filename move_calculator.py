from dataclasses import dataclass, field
from board import Board
import random
from move_generator import MoveGenerator
from evaluator import Evaluator

@dataclass
class MoveCalculator:
    move_generator: MoveGenerator = field(default_factory=MoveGenerator)
    evaluator: Evaluator = field(default_factory=Evaluator)
    turn_objective: dict[str, str] = field(default_factory=lambda: {
        'white': 'maximize',
        'black': 'minimize'
    })

    def calculate_move(self, board: Board, iter: int = 0, color: str | None = None, MAX_DEPTH = 0) -> tuple[float, list]:
        turn_color = color if color is not None else board.active_color

        if iter >= MAX_DEPTH:
            return self.evaluator.get_punctuation(board_obj=board), []

        pieces = board.get_pieces(color=turn_color)

        best_score = float('-inf') if self.is_maximizing_turn(turn_color) else float('inf')
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

                score, child_path = self.calculate_move(board, iter + 1, self.get_other_color(turn_color), MAX_DEPTH)

                original_piece = piece if move_piece != piece else None
                board.undo_move(move_piece, original_pos, (target_row, target_col), captured_piece, old_castling_rights, original_piece, move_type)

                current_path = [move_tuple] + child_path

                if self.is_better_score(score, best_score, turn_color):
                    best_score = score
                    best_path = current_path
                    candidates = [(score, current_path)]
                elif score == best_score:
                    candidates.append((score, current_path))

        if not legal_moves_found:
            return self.evaluator.get_punctuation(board_obj=board), []

        if candidates:
            _, best_path = random.choice(candidates)

        return best_score, best_path

    def is_maximizing_turn(self, color: str) -> bool:
        objective = self.turn_objective.get(color)
        if objective is None:
            raise ValueError(f"Unknown turn color: {color}")
        return objective == 'maximize'

    def is_better_score(self, score: float, best_score: float, color: str) -> bool:
        if self.is_maximizing_turn(color):
            return score > best_score
        return score < best_score

    @staticmethod
    def get_other_color(color: str):
        return 'black' if color == 'white' else 'white'
