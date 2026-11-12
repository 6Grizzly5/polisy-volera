from common import Board
from common import GameState
from common import Rules
from common import Player


BOARD = Board({
    0: [1, 3],
    1: [0, 2, 4],
    2: [1, 5],
    3: [0, 4, 6],
    4: [1, 3, 5, 7],
    5: [2, 4, 8],
    6: [3, 7],
    7: [4, 6, 8],
    8: [5, 7]
})


state = GameState()

print("=== ÉTAT INITIAL ===")
print(state)

print("\n=== COUPS DU VOLEUR ===")

moves = Rules.get_valid_moves(
    state,
    BOARD,
    Player.THIEF
)

for move in moves:
    print(move)

print("\n=== COUPS DE LA POLICE ===")

moves = Rules.get_valid_moves(
    state,
    BOARD,
    Player.POLICE
)

for move in moves:
    print(move)