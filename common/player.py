from enum import Enum

class Player(Enum):
    THIEF = "THIEF"
    POLICE = "POLICE"

    @property
    def opponent(self):
        return Player.POLICE if self is Player.THIEF else Player.THIEF
