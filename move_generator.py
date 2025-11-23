from pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from moves import Moves

class MoveGenerator:
    
    def get_legal_moves(self, board_obj, piece) -> list[tuple[int, int, Piece, Moves]]:
        """Devuelve una lista de tuplas (fila, columna, pieza, tipo_de_movimiento)."""
        if not piece or not hasattr(piece, "position"):
            return []

        row, col = piece.position
        moves = []

        def on_board(r, c):
            return 0 <= r < 8 and 0 <= c < 8

        def add_move(r, c, piece, move_type):
            if on_board(r, c):
                moves.append((r, c, piece, move_type))

        if isinstance(piece, Pawn):
            direction = -1 if piece.color == "white" else 1
            start_row = 6 if piece.color == "white" else 1

            if on_board(row + direction, col) and board_obj.board[row + direction][col] is None:
                add_move(row + direction, col, piece, Moves.NORMAL)

                if row == start_row and board_obj.board[row + 2 * direction][col] is None:
                    add_move(row + 2 * direction, col, piece, Moves.NORMAL)

            for dc in (-1, 1):
                r, c = row + direction, col + dc
                if on_board(r, c) and board_obj.board[r][c] and board_obj.board[r][c].color != piece.color:
                    add_move(r, c, piece, Moves.CAPTURE)

            final_row = 0 if piece.color == "white" else 7
            for (r, c, piece, mtype) in moves.copy():
                if r == final_row:
                    moves.remove((r, c, piece, mtype))
                    moves.append((r, c, Queen(color=piece.color, position=(r, c)), Moves.PROMOTION))

        elif isinstance(piece, Knight):
            deltas = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for dr, dc in deltas:
                r, c = row + dr, col + dc
                if not on_board(r, c):
                    continue
                target = board_obj.board[r][c]
                if target is None:
                    add_move(r, c, piece, Moves.NORMAL)
                elif target.color != piece.color:
                    add_move(r, c, piece, Moves.CAPTURE)

        elif isinstance(piece, Bishop):
            moves += self._sliding_moves(board_obj, piece, row, col, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

        elif isinstance(piece, Rook):
            moves += self._sliding_moves(board_obj, piece, row, col, [(-1, 0), (1, 0), (0, -1), (0, 1)])

        elif isinstance(piece, Queen):
            moves += self._sliding_moves(board_obj, piece, row, col, [
                (-1, -1), (-1, 1), (1, -1), (1, 1),
                (-1, 0), (1, 0), (0, -1), (0, 1)
            ])

        elif isinstance(piece, King):
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == dc == 0:
                        continue
                    r, c = row + dr, col + dc
                    if not on_board(r, c):
                        continue
                    target = board_obj.board[r][c]
                    if target is None:
                        add_move(r, c, piece, Moves.NORMAL)
                    elif target.color != piece.color:
                        add_move(r, c, piece, Moves.CAPTURE)

        return moves

    def _sliding_moves(self, board_obj, piece, row, col, directions):
        """Devuelve los movimientos para piezas deslizantes (torre, alfil, reina)."""
        result = []
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board_obj.board[r][c]
                if target is None:
                    result.append((r, c, piece, Moves.NORMAL))
                elif target.color != piece.color:
                    result.append((r, c, piece, Moves.CAPTURE))
                    break
                else:
                    break
                r += dr
                c += dc
        return result
