class Evaluator:
    
    def get_punctuation(self, board_obj) -> float:
        # Positive values favor white, negative values favor black.
        total = 0

        for row in board_obj.board:
            for piece in row:
                if piece is not None:
                    i, j = piece.position
                    adder = piece.get_value_adder_matrix()[i][j]
                    value = piece.value + adder
                    total += value if piece.color == 'white' else -value

        return total
