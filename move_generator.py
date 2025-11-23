from pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from moves import Moves

class MoveGenerator:
    
    def get_legal_moves(self, board_obj, piece) -> list[tuple[int, int, Piece, Moves]]:
        pseudo_moves = self.get_pseudo_legal_moves(board_obj, piece)
        legal_moves = []

        original_pos = piece.position
        my_color = piece.color
        
        for move in pseudo_moves:
            target_row, target_col, move_piece, move_type = move
            
            captured_piece = board_obj.move(move, start_pos=original_pos)
            
            king_pos = board_obj.white_king_pos if my_color == 'white' else board_obj.black_king_pos
            
            # If king_pos is None (e.g. in tests without kings), assume safe or handle error. 
            # Ideally kings should always exist.
            if king_pos:
                if not self.is_square_attacked(board_obj, king_pos, 'black' if my_color == 'white' else 'white'):
                    legal_moves.append(move)
            
            original_piece = piece if move_piece != piece else None
            board_obj.undo_move(move_piece, original_pos, (target_row, target_col), captured_piece, original_piece)

        return legal_moves

    def is_square_attacked(self, board_obj, square: tuple[int, int], attacker_color: str) -> bool:
        row, col = square
        
        # Check for Knight attacks
        knight_deltas = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_deltas:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board_obj.board[r][c]
                if piece and piece.color == attacker_color and isinstance(piece, Knight):
                    return True

        # Check for sliding pieces (Rook, Queen)
        ortho_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in ortho_dirs:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board_obj.board[r][c]
                if piece:
                    if piece.color == attacker_color and (isinstance(piece, Rook) or isinstance(piece, Queen)):
                        return True
                    break
                r += dr
                c += dc

        # Check for sliding pieces (Bishop, Queen)
        diag_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in diag_dirs:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board_obj.board[r][c]
                if piece:
                    if piece.color == attacker_color and (isinstance(piece, Bishop) or isinstance(piece, Queen)):
                        return True
                    break
                r += dr
                c += dc

        # Check for King attacks
        king_deltas = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dr, dc in king_deltas:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board_obj.board[r][c]
                if piece and piece.color == attacker_color and isinstance(piece, King):
                    return True

        # Check for Pawn attacks
        # Pawns attack diagonally. If attacker is white, they attack from row-1. If black, from row+1.
        pawn_direction = -1 if attacker_color == 'black' else 1 # Direction FROM attacker TO square? 
        # No, let's think: White pawn at (r, c) attacks (r-1, c-1) and (r-1, c+1).
        # So if we are at 'square' and want to see if a White pawn attacks us, we look at (row+1, col-1) and (row+1, col+1).
        
        check_direction = 1 if attacker_color == 'white' else -1
        
        for dc in (-1, 1):
            r, c = row + check_direction, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board_obj.board[r][c]
                if piece and piece.color == attacker_color and isinstance(piece, Pawn):
                    return True
        
        return False

    def get_pseudo_legal_moves(self, board_obj, piece) -> list[tuple[int, int, Piece, Moves]]:
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
