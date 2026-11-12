from dataclasses import dataclass, field
from .constants import INITIAL_THIEF_POSITION, INITIAL_POLICE_POSITIONS, GAME_ONGOING, THIEF

@dataclass
class GameState:
    thief_position: int = INITIAL_THIEF_POSITION
    police_positions: list[int] = field(default_factory=lambda: INITIAL_POLICE_POSITIONS.copy())
    current_player: str = THIEF
    status: str = GAME_ONGOING
    turn_number: int = 1
    thief_has_left_center: bool = False

    def copy(self):
        return GameState(
            self.thief_position,
            self.police_positions.copy(),
            self.current_player,
            self.status,
            self.turn_number,
            self.thief_has_left_center,
        )

    def to_dict(self):
        return {
            "thief": self.thief_position,
            "police": self.police_positions,
            "current_player": self.current_player,
            "status": self.status,
            "turn": self.turn_number,
            "thief_has_left_center": self.thief_has_left_center,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            int(data["thief"]),
            [int(x) for x in data["police"]],
            data["current_player"],
            data["status"],
            int(data["turn"]),
            bool(data.get("thief_has_left_center", False)),
        )
