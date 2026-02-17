from fen_parser import FenParser
from move_calculator import MoveCalculator
from moves import Moves


def test_white_maximizes():
    # White rook on a7 can capture black queen on a8.
    fen = "q6k/R7/8/8/8/8/8/7K w - - 0 1"
    board = FenParser.from_fen(fen)

    score, path = MoveCalculator().calculate_move(board=board, iter=0, MAX_DEPTH=1)

    assert path, "Expected at least one legal move for white."
    best_move = path[0]
    assert (best_move[0], best_move[1]) == (0, 0), "White should choose Rxa8 to maximize score."
    assert best_move[3] == Moves.CAPTURE, "White best move should be a capture."
    assert score > 0, f"Expected positive evaluation for white advantage, got {score}."


def test_black_minimizes():
    # Black rook on a2 can capture white queen on a1.
    fen = "k7/8/8/8/8/8/r7/Q6K b - - 0 1"
    board = FenParser.from_fen(fen)

    score, path = MoveCalculator().calculate_move(board=board, iter=0, MAX_DEPTH=1)

    assert path, "Expected at least one legal move for black."
    best_move = path[0]
    assert (best_move[0], best_move[1]) == (7, 0), "Black should choose Rxa1 to minimize score."
    assert best_move[3] == Moves.CAPTURE, "Black best move should be a capture."
    assert score < 0, f"Expected negative evaluation for black advantage, got {score}."


if __name__ == "__main__":
    test_white_maximizes()
    test_black_minimizes()
    print("MoveCalculator tests passed.")
