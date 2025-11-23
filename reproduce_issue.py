from board import Board
from fen_parser import FenParser
from move_calculator import MoveCalculator
from main import get_move_name

def reproduce():
    fen = "r1b1k1nr/ppp2ppp/2n5/2bQP3/8/5N2/PPP2PPP/RNB1KB1R b KQkq - 0 6"
    print(f"FEN: {fen}")
    
    board = FenParser.from_fen(fen)
    print("Board state:")
    print(board)
    
    # Check pieces
    print("\nPieces on board:")
    for r in range(8):
        for c in range(8):
            p = board.board[r][c]
            if p:
                print(f"{p.get_name()} ({p.color}) at ({r}, {c})")
                if r == 4 and c == 1: # b4
                    print("!!! FOUND PIECE AT b4 !!!")

    print("\nCalculating move...")
    mc = MoveCalculator()
    # Depth 3 as requested
    score, move_path = mc.calculate_move(board=board, iter=0, color='black', MAX_DEPTH=3)
    
    if move_path:
        best_move = move_path[0]
        move_name = get_move_name(best_move)
        print(f"Best Move: {move_name}")
        print(f"Move details: {best_move}")
    else:
        print("No moves found")

if __name__ == "__main__":
    reproduce()
