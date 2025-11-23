from moves import Moves
from pieces import Piece
from move_calculator import MoveCalculator
from board import Board
from fen_parser import FenParser


def get_move_name(move: tuple[int, int, Piece, Moves]):
    dict_pos = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}

    row, col, piece, _ = move

    return piece.get_name() + ' ' + dict_pos[col] + str(8-row)


def execute():
    fen_input: str = str(input("FEN position (or empty): "))
    if fen_input == "":
        board_matrix = FenParser.create_starting_board()
        board = Board(board=board_matrix)
    else:
        board = FenParser.from_fen(fen_input)
    
    MAX_DEPTH = 4
    COLOR = 'black'
    score, move_path = MoveCalculator().calculate_move(board=board, iter=0, color=COLOR, MAX_DEPTH=MAX_DEPTH)

    print('             ')
    if move_path:
        print(f'BEST MOVE: {get_move_name(move_path[0])}')
        
        """if len(move_path) > 1:
            print('NEXT MOVES: ', end='')
            for move in move_path[1:]:
                print(get_move_name(move), end=' ')
            print()"""
    else:
        print("No moves found")

if __name__ == "__main__":
    execute()