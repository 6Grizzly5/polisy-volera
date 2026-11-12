from .constants import (
    THIEF,
    POLICE,
    CENTER,
    GAME_ONGOING,
    THIEF_WINS,
    POLICE_WINS,
)
from .rules import Rules


class MinimaxAI:

    def __init__(self, depth=3):
        self.depth = depth

    def choose_move(self, state, board, player):

        moves = Rules.valid_moves(
            state,
            board,
            player
        )

        if not moves:
            return None

        best_move = None

        if player == POLICE:
            best_score = float("-inf")

            for move in moves:

                new_state = Rules.apply_move(
                    state,
                    move,
                    board
                )

                score = self.minimax(
                    new_state,
                    board,
                    self.depth - 1,
                    POLICE
                )

                if score > best_score:
                    best_score = score
                    best_move = move

        else:
            best_score = float("inf")

            for move in moves:

                new_state = Rules.apply_move(
                    state,
                    move,
                    board
                )

                score = self.minimax(
                    new_state,
                    board,
                    self.depth - 1,
                    POLICE
                )

                if score < best_score:
                    best_score = score
                    best_move = move

        return best_move

    def minimax(
        self,
        state,
        board,
        depth,
        maximizing_player
    ):

        # ==========================================================
        # ÉTATS TERMINAUX
        # ==========================================================

        if state.status == POLICE_WINS:
            return 100000

        if state.status == THIEF_WINS:
            return -100000

        if depth == 0:
            return self.evaluate(
                state,
                board
            )

        current_player = state.current_player

        moves = Rules.valid_moves(
            state,
            board,
            current_player
        )

        if not moves:

            if current_player == THIEF:
                return 100000

            return -100000

        # ==========================================================
        # TOUR DU POLICIER
        # ==========================================================

        if current_player == POLICE:

            best_score = float("-inf")

            for move in moves:

                new_state = Rules.apply_move(
                    state,
                    move,
                    board
                )

                score = self.minimax(
                    new_state,
                    board,
                    depth - 1,
                    maximizing_player
                )

                best_score = max(
                    best_score,
                    score
                )

            return best_score

        # ==========================================================
        # TOUR DU VOLEUR
        # ==========================================================

        else:

            best_score = float("inf")

            for move in moves:

                new_state = Rules.apply_move(
                    state,
                    move,
                    board
                )

                score = self.minimax(
                    new_state,
                    board,
                    depth - 1,
                    maximizing_player
                )

                best_score = min(
                    best_score,
                    score
                )

            return best_score

    # ==============================================================
    # ÉVALUATION DE LA POSITION
    # ==============================================================

    def evaluate(self, state, board):

        if state.status == POLICE_WINS:
            return 100000

        if state.status == THIEF_WINS:
            return -100000

        score = 0

        thief_moves = len(
            Rules.valid_moves(
                state,
                board,
                THIEF
            )
        )

        police_moves = len(
            Rules.valid_moves(
                state,
                board,
                POLICE
            )
        )

        # ==========================================================
        # 1. OBJECTIF PRINCIPAL DU POLICIER :
        #    RÉDUIRE LES MOUVEMENTS DU VOLEUR
        # ==========================================================

        # Moins le voleur possède de mouvements,
        # meilleure est la situation du policier.
        score += (8 - thief_moves) * 150

        # Si le voleur n'a aucun mouvement,
        # on est pratiquement dans une victoire.
        if thief_moves == 0:
            score += 50000

        # ==========================================================
        # 2. CONTRÔLE DU CENTRE
        # ==========================================================

        # Le centre est la case stratégique la plus importante.

        if CENTER in state.police_positions:

            # Gros bonus :
            # le policier contrôle directement le centre.
            score += 5000

            # Le voleur ne peut pas revenir au centre.
            if state.thief_has_left_center:
                score += 3000

        else:

            # Si le voleur a quitté le centre et que personne
            # ne le contrôle, le policier doit essayer de revenir.
            if state.thief_has_left_center:

                score -= 2500

        # ==========================================================
        # 3. DISTANCE DU POLICIER AU CENTRE
        # ==========================================================

        # Les policiers proches du centre sont généralement
        # plus utiles pour empêcher le retour du voleur.

        for police_position in state.police_positions:

            distance = self.graph_distance(
                board,
                police_position,
                CENTER
            )

            score += max(
                0,
                10 - distance
            ) * 120

        # ==========================================================
        # 4. MOBILITÉ DU POLICIER
        # ==========================================================

        score += police_moves * 10

        # ==========================================================
        # 5. POSITION DU VOLEUR
        # ==========================================================

        thief_distance = self.graph_distance(
            board,
            state.thief_position,
            CENTER
        )

        # Si le voleur est loin du centre après l'avoir quitté,
        # ce n'est pas forcément mauvais pour le policier,
        # mais il faut surtout empêcher son retour.

        if state.thief_has_left_center:

            score += thief_distance * 20

        return score

    # ==============================================================
    # DISTANCE DANS LE GRAPHE
    # ==============================================================

    def graph_distance(
        self,
        board,
        start,
        target
    ):

        if start == target:
            return 0

        queue = [(start, 0)]
        visited = {start}

        while queue:

            current, distance = queue.pop(0)

            for neighbor in board.get_neighbors(current):

                if neighbor in visited:
                    continue

                if neighbor == target:
                    return distance + 1

                visited.add(neighbor)

                queue.append(
                    (
                        neighbor,
                        distance + 1
                    )
                )

        return 999