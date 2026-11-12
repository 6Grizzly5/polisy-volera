from dataclasses import dataclass


@dataclass(frozen=True)
class Move:
    player: str
    from_position: int
    to_position: int

    def to_dict(self):
        return {
            "player": self.player,
            "from": self.from_position,
            "to": self.to_position,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["player"],
            int(data["from"]),
            int(data["to"]),
        )

    def __str__(self):
        return (
            f"{self.player}: "
            f"{self.from_position} -> "
            f"{self.to_position}"
        )