class Evaluator:
    
    def get_punctuation(self, board_obj, color: str) -> float:
        total = 0

        for row in board_obj.board:
            for piece in row:
                if piece is not None:
                    i, j = piece.position
                    adder = piece.get_value_adder_matrix()[i][j]
                    value = piece.value + adder
                    total += value if color == piece.color else -value

        return total
