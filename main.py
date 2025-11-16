from objects.moves import Moves
from objects.piece import Piece
from move_calculator import MoveCalculator
from objects.board import Board


def get_move_name(move: tuple[int, int, Piece, Moves]):
    dict_pos = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}

    row, col, piece, _ = move

    return piece.get_name() + ' ' + dict_pos[col] + str(8-row)


def execute():
    fen_input: str = str(input("FEN position (or empty): "))
    if fen_input == "":
        board = Board()
    else:
        board = Board.from_fen(fen_input)
    MAX_DEPTH = 2
    board, move = MoveCalculator().calculate_move(board=board, iter=0, color='white', MAX_DEPTH=MAX_DEPTH)

    print('             ')
    print(get_move_name(move))
    #print(board)


if __name__ == "__main__":
    execute()