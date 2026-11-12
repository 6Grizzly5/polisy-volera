class Board:
    """Plateau officiel à 13 positions, modélisé comme un graphe non orienté."""

    CONNECTIONS = {
        0: [2, 4, 7, 10, 12, 3, 6, 9],
        1: [12, 3, 2],
        2: [1, 3, 0, 12],
        3: [1, 2, 5, 4, 0],
        4: [3, 5, 0],
        5: [3, 4, 6],
        6: [5, 8, 7, 0],
        7: [6, 8, 0],
        8: [9, 6, 7],
        9: [11, 8, 10, 0],
        10: [9, 11, 0],
        11: [12, 9, 10],
        12: [1, 11, 2, 0],
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
