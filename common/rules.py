from .constants import (
    THIEF,
    POLICE,
    CENTER,
    GAME_ONGOING,
    THIEF_WINS,
    POLICE_WINS,
)
from .game_state import GameState
from .move import Move


class Rules:

    @staticmethod
    def occupied(state, position):
        """Retourne True si la position est occupée."""
        return (
            position == state.thief_position
            or position in state.police_positions
        )

    @staticmethod
    def valid_moves(state, board, player):
        """Retourne tous les déplacements légaux du joueur."""

        if state.status != GAME_ONGOING:
            return []

        result = []

        # ==========================================================
        # VOLEUR
        # ==========================================================
        if player == THIEF:

            src = state.thief_position

            for dst in board.get_neighbors(src):

                # Un policier bloque totalement la case.
                if dst in state.police_positions:
                    continue

                # Protection explicite du centre :
                # si un policier occupe le centre, le voleur
                # ne peut absolument pas y entrer.
                if dst == CENTER and CENTER in state.police_positions:
                    continue

                result.append(
                    Move(
                        THIEF,
                        src,
                        dst
                    )
                )

        # ==========================================================
        # POLICE
        # ==========================================================
        elif player == POLICE:

            for src in state.police_positions:

                for dst in board.get_neighbors(src):

                    # Le policier ne peut pas aller sur une case
                    # occupée par un autre policier ou par le voleur.
                    if Rules.occupied(state, dst):
                        continue

                    result.append(
                        Move(
                            POLICE,
                            src,
                            dst
                        )
                    )

        return result

    @staticmethod
    def apply_move(state, move, board):

        if state.status != GAME_ONGOING:
            raise ValueError("La partie est terminée.")

        if move.player != state.current_player:
            raise ValueError("Ce n'est pas le tour de ce joueur.")

        # Vérification stricte du déplacement.
        legal = any(
            m.from_position == move.from_position
            and m.to_position == move.to_position
            for m in Rules.valid_moves(
                state,
                board,
                move.player
            )
        )

        if not legal:
            raise ValueError("Déplacement illégal.")

        new = state.copy()

        # ==========================================================
        # VOLEUR
        # ==========================================================
        if move.player == THIEF:

            new.thief_position = move.to_position

            # Le voleur vient de quitter le centre.
            if move.from_position == CENTER:
                new.thief_has_left_center = True

            # Le voleur a quitté le centre puis y revient.
            # Il gagne uniquement si le centre n'est évidemment
            # pas occupé par un policier, ce qui est déjà garanti
            # par valid_moves().
            if (
                new.thief_has_left_center
                and new.thief_position == CENTER
            ):
                new.status = THIEF_WINS

            else:
                new.current_player = POLICE

        # ==========================================================
        # POLICE
        # ==========================================================
        elif move.player == POLICE:

            index = new.police_positions.index(
                move.from_position
            )

            new.police_positions[index] = move.to_position

            new.current_player = THIEF

        new.turn_number += 1

        # ==========================================================
        # VÉRIFICATION DE LA VICTOIRE DU POLICIER
        # ==========================================================

        if (
            new.status == GAME_ONGOING
            and not Rules.valid_moves(
                new,
                board,
                THIEF
            )
        ):
            new.status = POLICE_WINS

        return new