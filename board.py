from dataclasses import dataclass
from pieces import Piece
from moves import Moves

@dataclass
class Board:
    board: list[list] | None = None
    active_color: str = 'white'
    castling_rights: str = '-'
    en_passant: tuple | None = None
    halfmove_clock: int = 0
    fullmove_number: int = 1
    punctuation: float = 0.0
    white_king_pos: tuple[int, int] | None = None
    black_king_pos: tuple[int, int] | None = None

    def __post_init__(self):
        if self.punctuation == 0.0:
            self.punctuation = self.calculate_score()

    def calculate_score(self) -> float:
        total = 0
        if self.board is None: return 0
        for row in self.board:
            for piece in row:
                if piece is not None:
                    i, j = piece.position
                    adder = piece.get_value_adder_matrix()[i][j]
                    value = piece.value + adder
                    total += value if piece.color == 'white' else -value
        return total

    # PRE: move is legal
    def move(self, move: tuple[int, int, Piece, Moves], start_pos: tuple[int, int] | None = None):
        new_row, new_col, piece, move_type = move
        
        if start_pos:
            old_row, old_col = start_pos
        else:
            old_row, old_col = piece.position

        piece_on_board = self.board[old_row][old_col]
        
        adder_old = piece_on_board.get_value_adder_matrix()[old_row][old_col]
        val_old = piece_on_board.value + adder_old
        self.punctuation -= val_old if piece_on_board.color == 'white' else -val_old

        adder_new = piece.get_value_adder_matrix()[new_row][new_col]
        val_new = piece.value + adder_new
        self.punctuation += val_new if piece.color == 'white' else -val_new

        target = self.board[new_row][new_col]
        if target is not None:
            adder_target = target.get_value_adder_matrix()[new_row][new_col]
            val_target = target.value + adder_target
            self.punctuation -= val_target if target.color == 'white' else -val_target

        self.board[old_row][old_col] = None
        self.board[new_row][new_col] = piece

        piece.position = (new_row, new_col)

        if piece.get_name() == 'King':
            if piece.color == 'white':
                self.white_king_pos = (new_row, new_col)
            else:
                self.black_king_pos = (new_row, new_col)

        # Handle Castling
        old_castling_rights = self.castling_rights
        if move_type == Moves.CASTLING_SHORT:
            rook_col = 7
            rook_target_col = 5
            rook = self.board[new_row][rook_col]
            self.board[new_row][rook_col] = None
            self.board[new_row][rook_target_col] = rook
            rook.position = (new_row, rook_target_col)
            
            # Update score for rook move (simplified, assuming rook value doesn't change much by position or we accept small drift, 
            # but ideally we should update it. Let's do it properly.)
            adder_rook_old = rook.get_value_adder_matrix()[new_row][rook_col]
            val_rook_old = rook.value + adder_rook_old
            self.punctuation -= val_rook_old if rook.color == 'white' else -val_rook_old
            
            adder_rook_new = rook.get_value_adder_matrix()[new_row][rook_target_col]
            val_rook_new = rook.value + adder_rook_new
            self.punctuation += val_rook_new if rook.color == 'white' else -val_rook_new

        elif move_type == Moves.CASTLING_LONG:
            rook_col = 0
            rook_target_col = 3
            rook = self.board[new_row][rook_col]
            self.board[new_row][rook_col] = None
            self.board[new_row][rook_target_col] = rook
            rook.position = (new_row, rook_target_col)

            adder_rook_old = rook.get_value_adder_matrix()[new_row][rook_col]
            val_rook_old = rook.value + adder_rook_old
            self.punctuation -= val_rook_old if rook.color == 'white' else -val_rook_old
            
            adder_rook_new = rook.get_value_adder_matrix()[new_row][rook_target_col]
            val_rook_new = rook.value + adder_rook_new
            self.punctuation += val_rook_new if rook.color == 'white' else -val_rook_new

        # Update Castling Rights
        if self.castling_rights:
            if piece.get_name() == 'King':
                if piece.color == 'white':
                    self.castling_rights = self.castling_rights.replace('K', '').replace('Q', '')
                else:
                    self.castling_rights = self.castling_rights.replace('k', '').replace('q', '')
            elif piece.get_name() == 'Rook':
                if piece.color == 'white':
                    if old_col == 0: self.castling_rights = self.castling_rights.replace('Q', '')
                    elif old_col == 7: self.castling_rights = self.castling_rights.replace('K', '')
                else:
                    if old_col == 0: self.castling_rights = self.castling_rights.replace('q', '')
                    elif old_col == 7: self.castling_rights = self.castling_rights.replace('k', '')
            
            if target and target.get_name() == 'Rook':
                 if target.color == 'white':
                    if new_col == 0: self.castling_rights = self.castling_rights.replace('Q', '')
                    elif new_col == 7: self.castling_rights = self.castling_rights.replace('K', '')
                 else:
                    if new_col == 0: self.castling_rights = self.castling_rights.replace('q', '')
                    elif new_col == 7: self.castling_rights = self.castling_rights.replace('k', '')

        return target, old_castling_rights

    def undo_move(self, piece: Piece, original_pos: tuple[int, int], target_pos: tuple[int, int], captured_piece: Piece | None, old_castling_rights: str, original_piece: Piece | None = None, move_type: Moves = Moves.NORMAL):
        old_row, old_col = original_pos
        new_row, new_col = target_pos

        piece_to_restore = original_piece if original_piece else piece

        adder_new = piece.get_value_adder_matrix()[new_row][new_col]
        val_new = piece.value + adder_new
        self.punctuation -= val_new if piece.color == 'white' else -val_new

        adder_old = piece_to_restore.get_value_adder_matrix()[old_row][old_col]
        val_old = piece_to_restore.value + adder_old
        self.punctuation += val_old if piece_to_restore.color == 'white' else -val_old

        if captured_piece is not None:
            adder_target = captured_piece.get_value_adder_matrix()[new_row][new_col]
            val_target = captured_piece.value + adder_target
            self.punctuation += val_target if captured_piece.color == 'white' else -val_target

        self.board[new_row][new_col] = captured_piece
        self.board[old_row][old_col] = piece_to_restore
        piece_to_restore.position = original_pos

        if piece_to_restore.get_name() == 'King':
            if piece_to_restore.color == 'white':
                self.white_king_pos = original_pos
            else:
                self.black_king_pos = original_pos
        
        # Restore Castling Rights
        self.castling_rights = old_castling_rights

        # Undo Castling Rook Move
        if move_type == Moves.CASTLING_SHORT:
            rook_col = 7
            rook_current_col = 5
            rook = self.board[new_row][rook_current_col]
            self.board[new_row][rook_current_col] = None
            self.board[new_row][rook_col] = rook
            rook.position = (new_row, rook_col)

            adder_rook_curr = rook.get_value_adder_matrix()[new_row][rook_current_col]
            val_rook_curr = rook.value + adder_rook_curr
            self.punctuation -= val_rook_curr if rook.color == 'white' else -val_rook_curr
            
            adder_rook_old = rook.get_value_adder_matrix()[new_row][rook_col]
            val_rook_old = rook.value + adder_rook_old
            self.punctuation += val_rook_old if rook.color == 'white' else -val_rook_old

        elif move_type == Moves.CASTLING_LONG:
            rook_col = 0
            rook_current_col = 3
            rook = self.board[new_row][rook_current_col]
            self.board[new_row][rook_current_col] = None
            self.board[new_row][rook_col] = rook
            rook.position = (new_row, rook_col)

            adder_rook_curr = rook.get_value_adder_matrix()[new_row][rook_current_col]
            val_rook_curr = rook.value + adder_rook_curr
            self.punctuation -= val_rook_curr if rook.color == 'white' else -val_rook_curr
            
            adder_rook_old = rook.get_value_adder_matrix()[new_row][rook_col]
            val_rook_old = rook.value + adder_rook_old
            self.punctuation += val_rook_old if rook.color == 'white' else -val_rook_old
    
    def get_pieces(self, color: str):
        return [piece for row in self.board for piece in row if piece is not None and piece.color == color]
    
    def __str__(self):
        piece_symbols = {
            'Pawn': 'P',
            'Rook': 'R',
            'Knight': 'N',
            'Bishop': 'B',
            'Queen': 'Q',
            'King': 'K'
        }

        lines = []
        for row in self.board:
            row_str = ""
            for piece in row:
                if piece is None:
                    row_str += ". "
                else:
                    symbol = piece_symbols.get(piece.__class__.__name__, "?")
                    if piece.color == 'black':
                        symbol = symbol.lower()
                    row_str += symbol + " "
            lines.append(row_str.rstrip())
        return "\n".join(lines)
