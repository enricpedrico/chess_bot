from dataclasses import dataclass, field
from .piece import Rook, Knight, Bishop, Queen, King, Pawn, Piece
from .moves import Moves

@dataclass
class Board:
    board: list[list] | None = None
    active_color: str = 'white'
    castling_rights: str = '-'
    en_passant: tuple | None = None
    halfmove_clock: int = 0
    fullmove_number: int = 1

    

    
    # PRE: move is legal
    def move(self, move: tuple[int, int, Piece, Moves]):
        new_row, new_col, piece, _ = move
        old_row, old_col = piece.position

        self.board[old_row][old_col] = None
        self.board[new_row][new_col] = piece

        piece.position = (new_row, new_col)

        return self.board
    
    def get_pieces(self, color: str):
        return [piece for row in self.board for piece in row if piece is not None and piece.color == color]
    

    def get_punctuation(self, color: str) -> float:
        total = 0

        for row in self.board:
            for piece in row:
                if piece is not None:
                    i, j = piece.position
                    adder = piece.get_value_adder_matrix()[i][j]
                    value = piece.value + adder
                    total += value if color == piece.color else -value

        return total

    
    
    """NO ENROQUE; NO EN_PASSANT; NO PROMOTE; LEGAL MOVES?"""
    def get_legal_moves(self, piece) -> list[tuple[int, int, Piece, Moves]]:
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

            if on_board(row + direction, col) and self.board[row + direction][col] is None:
                add_move(row + direction, col, piece, Moves.NORMAL)

                if row == start_row and self.board[row + 2 * direction][col] is None:
                    add_move(row + 2 * direction, col, piece, Moves.NORMAL)

            for dc in (-1, 1):
                r, c = row + direction, col + dc
                if on_board(r, c) and self.board[r][c] and self.board[r][c].color != piece.color:
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
                target = self.board[r][c]
                if target is None:
                    add_move(r, c, piece, Moves.NORMAL)
                elif target.color != piece.color:
                    add_move(r, c, piece, Moves.CAPTURE)

        elif isinstance(piece, Bishop):
            moves += self._sliding_moves(piece, row, col, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

        elif isinstance(piece, Rook):
            moves += self._sliding_moves(piece, row, col, [(-1, 0), (1, 0), (0, -1), (0, 1)])

        elif isinstance(piece, Queen):
            moves += self._sliding_moves(piece, row, col, [
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
                    target = self.board[r][c]
                    if target is None:
                        add_move(r, c, piece, Moves.NORMAL)
                    elif target.color != piece.color:
                        add_move(r, c, piece, Moves.CAPTURE)

        return moves

    def _sliding_moves(self, piece, row, col, directions):
        """Devuelve los movimientos para piezas deslizantes (torre, alfil, reina)."""
        result = []
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
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
    
    ##############################################################################################################################
    # INIT BOARD #################################################################################################################
    ##############################################################################################################################

    def __post_init__(self):
        if self.board is None:
            self.board = self.create_starting_board()
        else:
            self.fix_piece_positions()

    @classmethod
    def from_fen(cls, fen: str):
        parts = fen.split()
        placement, active_color, castling, en_passant, halfmove, fullmove = parts

        board = cls.parse_fen_placement(placement)

        obj = cls(board=board)
        obj.active_color = 'white' if active_color == 'w' else 'black'
        obj.castling_rights = castling if castling != '-' else ''
        obj.en_passant = cls.convert_en_passant(en_passant)
        obj.halfmove_clock = int(halfmove)
        obj.fullmove_number = int(fullmove)

        return obj
    
    @staticmethod
    def parse_fen_placement(placement: str) -> list[list]:
        rows = placement.split('/')
        board = [[None for _ in range(8)] for _ in range(8)]

        piece_from_char = {
            'p': Pawn, 'r': Rook, 'n': Knight, 'b': Bishop,
            'q': Queen, 'k': King,
        }

        for row_idx, fen_row in enumerate(rows):
            col = 0
            for char in fen_row:
                if char.isdigit():
                    col += int(char)
                else:
                    color = 'white' if char.isupper() else 'black'
                    piece_class = piece_from_char[char.lower()]
                    board[row_idx][col] = piece_class(color)
                    col += 1

        # Assign positions
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece:
                    piece.position = (r, c)

        return board
    
    @staticmethod
    def convert_en_passant(ep: str):
        if ep == '-':
            return None
        file = ord(ep[0]) - ord('a')
        rank = 8 - int(ep[1])
        return (rank, file)
    
    @staticmethod
    def create_starting_board():
        board = [[None for _ in range(8)] for _ in range(8)]

        board[0] = [
            Rook('black'), Knight('black'), Bishop('black'), Queen('black'),
            King('black'), Bishop('black'), Knight('black'), Rook('black')
        ]
        board[1] = [Pawn('black') for _ in range(8)]

        for row in range(2, 6):
            board[row] = [None for _ in range(8)]

        board[6] = [Pawn('white') for _ in range(8)]
        board[7] = [
            Rook('white'), Knight('white'), Bishop('white'), Queen('white'),
            King('white'), Bishop('white'), Knight('white'), Rook('white')
        ]

        for r in range(8):
            for c in range(8):
                if board[r][c] is not None:
                    board[r][c].position = (r, c)

        return board
    
    def fix_piece_positions(self):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None:
                    piece.position = (r, c)