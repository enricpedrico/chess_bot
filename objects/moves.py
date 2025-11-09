from enum import Enum, auto


class Moves(Enum):
    NORMAL = auto()
    CAPTURE = auto()
    CHECK = auto()
    CASTLING = auto()
    PROMOTION = auto()