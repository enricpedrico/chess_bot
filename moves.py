from enum import Enum, auto


class Moves(Enum):
    NORMAL = auto()
    CAPTURE = auto()
    CHECK = auto()
    CASTLING_SHORT = auto()
    CASTLING_LONG = auto()
    PROMOTION = auto()
