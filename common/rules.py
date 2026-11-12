from .constants import THIEF, POLICE, CENTER, GAME_ONGOING, THIEF_WINS, POLICE_WINS
from .game_state import GameState
from .move import Move

class Rules:
    @staticmethod
    def occupied(state, position):
        return position == state.thief_position or position in state.police_positions

    @staticmethod
    def valid_moves(state, board, player):
        if state.status != GAME_ONGOING:
            return []

        result = []
        if player == THIEF:
            src = state.thief_position
            for dst in board.get_neighbors(src):
                if dst not in state.police_positions:
                    result.append(Move(THIEF, src, dst))
        elif player == POLICE:
            for src in state.police_positions:
                for dst in board.get_neighbors(src):
                    if not Rules.occupied(state, dst):
                        result.append(Move(POLICE, src, dst))
        return result

    @staticmethod
    def apply_move(state, move, board):
        if state.status != GAME_ONGOING:
            raise ValueError("La partie est terminée.")
        if move.player != state.current_player:
            raise ValueError("Ce n'est pas le tour de ce joueur.")

        legal = any(
            m.from_position == move.from_position and m.to_position == move.to_position
            for m in Rules.valid_moves(state, board, move.player)
        )
        if not legal:
            raise ValueError("Déplacement illégal.")

        new = state.copy()

        if move.player == THIEF:
            new.thief_position = move.to_position
            if move.from_position == CENTER:
                new.thief_has_left_center = True

            if new.thief_has_left_center and new.thief_position == CENTER:
                new.status = THIEF_WINS
            else:
                new.current_player = POLICE

        elif move.player == POLICE:
            index = new.police_positions.index(move.from_position)
            new.police_positions[index] = move.to_position
            new.current_player = THIEF

        new.turn_number += 1

        if new.status == GAME_ONGOING and not Rules.valid_moves(new, board, THIEF):
            new.status = POLICE_WINS

        return new
