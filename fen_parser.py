from pieces import Pawn, Rook, Knight, Bishop, Queen, King
from board import Board

class FenParser:
    
    @classmethod
    def from_fen(cls, fen: str) -> Board:
        parts = fen.split()
        placement, active_color, castling, en_passant, halfmove, fullmove = parts

        board_matrix = cls.parse_fen_placement(placement)

        obj = Board(board=board_matrix)
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
    def create_starting_board() -> list[list]:
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
