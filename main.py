from objects.moves import Moves
from objects.piece import Piece


def get_move_name(move: tuple[int, int, Piece, Moves]):
    dict_pos = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}

    row, col, piece, _ = move

    return piece.get_name() + ' ' + dict_pos[col] + str(8-row)


def execute():
    pass



if __name__ == "__main__":
    execute()