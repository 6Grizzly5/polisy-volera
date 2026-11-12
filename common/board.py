class Board:
    """Plateau traditionnel de Polisy sy Volera, 13 sommets."""

    CONNECTIONS = {
        0: [2, 4, 7, 10, 12, 3, 6, 9],
        1: [2, 3, 12],
        2: [1, 3, 12, 0],
        3: [1, 2, 5, 4, 0],
        4: [3, 5, 6, 0],
        5: [3, 4, 6],
        6: [5, 8, 7, 4, 0],
        7: [6, 8, 9, 0],
        8: [6, 9, 7],
        9: [8, 11, 10, 7, 0],
        10: [11, 9, 12, 0],
        11: [12, 10, 9],
        12: [1, 11, 2, 10, 0],
    }

    def __init__(self):
        self.connections = {k: list(v) for k, v in self.CONNECTIONS.items()}
        self.validate()

    def positions(self):
        return list(self.connections.keys())

    def get_neighbors(self, position):
        return self.connections.get(position, [])

    def are_connected(self, a, b):
        return b in self.get_neighbors(a)

    def validate(self):
        if set(self.connections) != set(range(13)):
            raise ValueError("Le plateau doit contenir les positions 0..12.")
        for a, neighbors in self.connections.items():
            for b in neighbors:
                if a not in self.connections.get(b, []):
                    raise ValueError(f"Connexion asymétrique: {a} -> {b}")
