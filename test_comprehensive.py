from board import Board
from fen_parser import FenParser
from move_generator import MoveGenerator
from moves import Moves
from pieces import Queen, Rook, Bishop, Knight, Pawn, King

def run_test(name, fen, description, assertions):
    print(f"\n--- Test: {name} ---")
    print(f"Description: {description}")
    print(f"FEN: {fen}")
    
    board = FenParser.from_fen(fen)
    mg = MoveGenerator()
    
    # Run assertions
    try:
        assertions(board, mg)
        print("RESULT: PASSED")
    except AssertionError as e:
        print(f"RESULT: FAILED - {e}")
    except Exception as e:
        print(f"RESULT: ERROR - {e}")

def test_pawn_moves(board, mg):
    # White pawn at e2. Should have 2 moves: e3, e4.
    pawn = board.board[6][4]
    moves = mg.get_legal_moves(board, pawn)
    assert len(moves) == 2, f"Expected 2 moves for pawn at e2, got {len(moves)}"
    
    targets = [(m[0], m[1]) for m in moves]
    assert (5, 4) in targets, "Missing move e3"
    assert (4, 4) in targets, "Missing move e4"

def test_knight_moves(board, mg):
    # White knight at b1. Should have 2 moves: a3, c3.
    knight = board.board[7][1]
    moves = mg.get_legal_moves(board, knight)
    assert len(moves) == 2, f"Expected 2 moves for knight at b1, got {len(moves)}"
    
    targets = [(m[0], m[1]) for m in moves]
    assert (5, 0) in targets, "Missing move a3" # (5, 0)
    assert (5, 2) in targets, "Missing move c3" # (5, 2)

def test_pin_absolute(board, mg):
    # White King e1, White Rook e2, Black Rook e8. Rook pinned.
    # Rook can only move on e-file.
    rook = board.board[6][4]
    moves = mg.get_legal_moves(board, rook)
    
    for r, c, _, _ in moves:
        assert c == 4, f"Pinned rook moved off-file to ({r}, {c})"

def test_check_resolution(board, mg):
    # White King e1, Black Rook e8. Check.
    # King must move or piece block.
    king = board.board[7][4]
    moves = mg.get_legal_moves(board, king)
    
    # e2 is attacked. d1, f1, d2, f2 are safe (assuming empty board).
    # e2 is (6, 4).
    targets = [(m[0], m[1]) for m in moves]
    assert (6, 4) not in targets, "King cannot move to e2 (attacked)"

def test_double_check(board, mg):
    # White King e1. Black Rook e8, Black Bishop h4.
    # Only King moves allowed.
    # Add a white rook at a1 to verify it has no moves.
    white_rook = board.board[7][0]
    moves = mg.get_legal_moves(board, white_rook)
    assert len(moves) == 0, f"Piece other than King moved in double check: {len(moves)}"

def test_castling_short(board, mg):
    # White King e1, Rook h1. Clear path.
    king = board.board[7][4]
    moves = mg.get_legal_moves(board, king)
    
    has_short = any(m[3] == Moves.CASTLING_SHORT for m in moves)
    assert has_short, "Short castling should be available"

def test_castling_long_obstructed(board, mg):
    # White King e1, Rook a1. Knight at b1.
    king = board.board[7][4]
    moves = mg.get_legal_moves(board, king)
    
    has_long = any(m[3] == Moves.CASTLING_LONG for m in moves)
    assert not has_long, "Long castling should be obstructed"

def test_promotion(board, mg):
    # White Pawn at a7. Move to a8.
    pawn = board.board[1][0]
    moves = mg.get_legal_moves(board, pawn)
    
    has_promotion = any(m[3] == Moves.PROMOTION for m in moves)
    assert has_promotion, "Promotion move missing"

def test_stalemate(board, mg):
    # White King at a1. Black Queen at c2. Black King at c3.
    # White King has no moves. Not in check.
    # FEN: 8/8/8/8/8/2k5/2q5/K7 w - - 0 1
    king = board.board[7][0]
    moves = mg.get_legal_moves(board, king)
    assert len(moves) == 0, f"Stalemate should have 0 moves, got {len(moves)}"
    
    # Verify not in check
    assert not mg.is_square_attacked(board, king.position, 'black'), "King should not be in check for stalemate"

def test_checkmate(board, mg):
    # Fool's Mate pattern or similar.
    # White King e1. Black Queen e2. Black King e3. (Support mate)
    # FEN: 8/8/8/8/8/4k3/4q3/4K3 w - - 0 1
    king = board.board[7][4]
    moves = mg.get_legal_moves(board, king)
    assert len(moves) == 0, f"Checkmate should have 0 moves, got {len(moves)}"
    
    # Verify in check
    assert mg.is_square_attacked(board, king.position, 'black'), "King should be in check for checkmate"


if __name__ == "__main__":
    # 1. Pawn Moves
    run_test("Pawn Moves", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 
             "Start position, white pawn at e2", test_pawn_moves)
    
    # 2. Knight Moves
    run_test("Knight Moves", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 
             "Start position, white knight at b1", test_knight_moves)
    
    # 3. Pin Absolute
    run_test("Pin Absolute", "4r3/8/8/8/8/8/4R3/4K3 w - - 0 1", 
             "White Rook pinned by Black Rook", test_pin_absolute)
    
    # 4. Check Resolution
    run_test("Check Resolution", "4r3/8/8/8/8/8/8/4K3 w - - 0 1", 
             "White King in check by Black Rook", test_check_resolution)
    
    # 5. Double Check
    run_test("Double Check", "4r3/8/8/8/7b/8/8/R3K3 w - - 0 1", 
             "White King in double check (Rook + Bishop)", test_double_check)
    
    # 6. Castling Short
    run_test("Castling Short", "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1", 
             "White King e1, Rook h1, clear path", test_castling_short)
    
    # 7. Castling Long Obstructed
    run_test("Castling Long Obstructed", "r3k2r/8/8/8/8/8/8/RN2K2R w KQkq - 0 1", 
             "White King e1, Rook a1, Knight b1", test_castling_long_obstructed)
    
    # 8. Promotion
    run_test("Promotion", "8/P7/8/8/8/8/8/8 w - - 0 1", 
             "White Pawn at a7", test_promotion)
    
    # 9. Stalemate
    run_test("Stalemate", "8/8/8/8/8/2k5/2q5/K7 w - - 0 1", 
             "White King a1, Black Queen c2, Black King c3", test_stalemate)
    
    # 10. Checkmate
    run_test("Checkmate", "8/8/8/8/8/4k3/4q3/4K3 w - - 0 1", 
             "White King e1, Black Queen e2 (supported)", test_checkmate)
