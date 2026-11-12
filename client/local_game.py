from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

from common.ai import MinimaxAI
from common.board import Board
from common.constants import GAME_ONGOING, POLICE, THIEF, THIEF_WINS, POLICE_WINS
from common.game_state import GameState
from common.move import Move
from common.rules import Rules


class LocalGameController:
    def __init__(self, window, human_role):
        self.window = window
        self.human_role = human_role
        self.bot_role = POLICE if human_role == THIEF else THIEF
        self.board = Board()
        self.state = GameState()
        self.ai = MinimaxAI(depth=3)
        self.window.board_widget.set_state(self.state)
        self.update()
        if self.state.current_player == self.bot_role:
            QTimer.singleShot(500, self.bot_turn)

    def update(self):
        self.window.board_widget.set_state(self.state)
        if self.state.status == GAME_ONGOING:
            if self.state.current_player == self.human_role:
                self.window.info_label.setText(f"À VOUS DE JOUER • Tour {self.state.turn_number}")
            else:
                self.window.info_label.setText("🤖 Le bot réfléchit...")
        elif self.state.status == THIEF_WINS:
            QMessageBox.information(self.window, "Fin de partie", "🟤 Le voleur a réussi à revenir au centre !")
        elif self.state.status == POLICE_WINS:
            QMessageBox.information(self.window, "Fin de partie", "🔵 La police a bloqué le voleur !")

    def click_position(self, pos):
        if self.state.status != GAME_ONGOING or self.state.current_player != self.human_role:
            return

        if self.window.selected is None:
            if self.human_role == THIEF and pos == self.state.thief_position:
                self.window.selected = pos
            elif self.human_role == POLICE and pos in self.state.police_positions:
                self.window.selected = pos
            else:
                return
            self.window.board_widget.selected = pos
            self.window.board_widget.update()
            self.window.info_label.setText("Position sélectionnée. Cliquez sur la destination.")
            return

        if pos == self.window.selected:
            self.window.selected = None
            self.window.board_widget.selected = None
            self.update()
            return

        move = Move(self.human_role, self.window.selected, pos)
        self.window.selected = None
        self.window.board_widget.selected = None
        try:
            self.state = Rules.apply_move(self.state, move, self.board)
        except ValueError as exc:
            self.window.info_label.setText(f"⚠ {exc}")
            self.window.board_widget.update()
            return

        self.update()
        if self.state.status == GAME_ONGOING and self.state.current_player == self.bot_role:
            QTimer.singleShot(350, self.bot_turn)

    def bot_turn(self):
        if self.state.status != GAME_ONGOING or self.state.current_player != self.bot_role:
            return
        move = self.ai.choose_move(self.state, self.board, self.bot_role)
        if move is None:
            return
        try:
            self.state = Rules.apply_move(self.state, move, self.board)
        except ValueError:
            return
        self.update()
        if self.state.status == GAME_ONGOING and self.state.current_player == self.bot_role:
            QTimer.singleShot(250, self.bot_turn)
