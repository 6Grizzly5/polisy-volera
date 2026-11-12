import socket
import sys

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QHBoxLayout, QInputDialog, QLabel,
    QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget
)

from common.board import Board
from common.constants import (
    GAME_ONGOING, POLICE, POLICE_WINS, PORT, THIEF, THIEF_WINS
)
from common.game_state import GameState
from common.move import Move
from client.board_widget import BoardWidget
from client.network import NetworkClient
from server.game_server import GameServer

class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.server = None
        self.setWindowTitle("Polisy sy Volera - V1")
        self.setMinimumSize(460, 380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(45, 35, 45, 35)

        title = QLabel("POLISY SY VOLERA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: 700;")
        layout.addWidget(title)

        sub = QLabel("Jeu traditionnel malgache • Prototype réseau V1")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        layout.addStretch()

        self.host_role = QComboBox()
        self.host_role.addItem("Police", POLICE)
        self.host_role.addItem("Voleur", THIEF)

        create = QPushButton("Créer une partie")
        join = QPushButton("Rejoindre une partie")
        quit_btn = QPushButton("Quitter")

        create.clicked.connect(self.create_game)
        join.clicked.connect(self.join_game)
        quit_btn.clicked.connect(QApplication.quit)

        layout.addWidget(QLabel("Pour créer : choisissez votre rôle"))
        layout.addWidget(self.host_role)
        layout.addWidget(create)
        layout.addWidget(join)
        layout.addWidget(quit_btn)

        self.info = QLabel("")
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info.setWordWrap(True)
        layout.addWidget(self.info)

    def create_game(self):
        role = self.host_role.currentData()
        try:
            self.server = GameServer(role, log=self.info.setText)
            self.server.start()
            self.info.setText(
                f"Serveur prêt. IP LAN : {self.local_ip()} | Port : {PORT}"
            )
            self.game = GameWindow(role, "127.0.0.1", self, self.server)
            self.game.show()
            self.hide()
            self.game.connect_to_server()
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", str(exc))

    def join_game(self):
        ip, ok = QInputDialog.getText(
            self, "Rejoindre", "IP du PC qui héberge :", text="192.168.1.10"
        )
        if not ok or not ip.strip():
            return

        role_text, ok = QInputDialog.getItem(
            self, "Rôle", "Votre rôle :", ["Police", "Voleur"], 0, False
        )
        if not ok:
            return

        role = POLICE if role_text == "Police" else THIEF
        self.game = GameWindow(role, ip.strip(), self, None)
        self.game.show()
        self.hide()
        self.game.connect_to_server()

    def local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()

class GameWindow(QMainWindow):
    def __init__(self, role, host, menu, server):
        super().__init__()
        self.role = role
        self.host = host
        self.menu = menu
        self.server = server
        self.board = Board()
        self.state = GameState()
        self.network = NetworkClient()
        self.network.messageReceived.connect(self.process_message)
        self.network.disconnectedSignal.connect(self.disconnected)
        self.selected = None

        role_name = "POLICE" if role == POLICE else "VOLEUR"
        self.setWindowTitle(f"Polisy sy Volera - {role_name}")
        self.resize(900, 800)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top = QHBoxLayout()
        self.role_label = QLabel(f"Vous êtes : {role_name}")
        self.connection_label = QLabel("Connexion...")
        self.connection_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        top.addWidget(self.role_label)
        top.addStretch()
        top.addWidget(self.connection_label)
        layout.addLayout(top)

        self.board_widget = BoardWidget(self.board, self.state)
        self.board_widget.positionClicked.connect(self.click_position)
        layout.addWidget(self.board_widget, 1)

        self.info_label = QLabel("Connexion...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(self.info_label)

        bottom = QHBoxLayout()
        bottom.addStretch()
        back = QPushButton("Quitter la partie")
        back.clicked.connect(self.back_to_menu)
        bottom.addWidget(back)
        layout.addLayout(bottom)

    def connect_to_server(self):
        try:
            self.network.connect(self.host, PORT, self.role)
        except Exception as exc:
            QMessageBox.critical(self, "Connexion impossible", str(exc))
            self.back_to_menu()

    def process_message(self, message):
        typ = message.get("type")

        if typ == "WAITING":
            self.connection_label.setText("En attente...")
            self.info_label.setText("En attente du deuxième joueur...")

        elif typ == "START":
            self.state = GameState.from_dict(message["state"])
            self.board_widget.set_state(self.state)
            self.connection_label.setText("Connecté")
            self.update_turn()

        elif typ == "STATE":
            self.state = GameState.from_dict(message["state"])
            self.board_widget.set_state(self.state)
            self.update_turn()

            if self.state.status == THIEF_WINS:
                QMessageBox.information(self, "Fin", "Le voleur a réussi à revenir au centre !")
            elif self.state.status == POLICE_WINS:
                QMessageBox.information(self, "Fin", "La police a encerclé le voleur !")

        elif typ == "ERROR":
            self.info_label.setText("⚠ " + message.get("message", "Erreur"))

    def update_turn(self):
        if self.state.status != GAME_ONGOING:
            self.info_label.setText("PARTIE TERMINÉE")
            return

        if self.state.current_player == self.role:
            self.info_label.setText(f"À VOUS DE JOUER • Tour {self.state.turn_number}")
        else:
            name = "VOLEUR" if self.state.current_player == THIEF else "POLICE"
            self.info_label.setText(f"Tour de l'adversaire • {name}")

    def click_position(self, pos):
        if self.state.status != GAME_ONGOING:
            return
        if self.state.current_player != self.role:
            return

        if self.selected is None:
            if self.role == THIEF and pos == self.state.thief_position:
                self.selected = pos
            elif self.role == POLICE and pos in self.state.police_positions:
                self.selected = pos
            else:
                return

            self.board_widget.selected = pos
            self.board_widget.update()
            self.info_label.setText(f"Position {pos} sélectionnée. Cliquez sur la destination.")
            return

        if pos == self.selected:
            self.selected = None
            self.board_widget.selected = None
            self.board_widget.update()
            self.update_turn()
            return

        move = Move(self.role, self.selected, pos)
        self.network.send_move(move)
        self.selected = None
        self.board_widget.selected = None
        self.board_widget.update()

    def disconnected(self):
        QTimer.singleShot(0, lambda: self.info_label.setText("Connexion perdue."))

    def back_to_menu(self):
        self.network.close()
        if self.server:
            self.server.stop()
        self.close()
        self.menu.show()

    def closeEvent(self, event):
        self.network.close()
        if self.server:
            self.server.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget { font-family: Arial; font-size: 14px; }
        QPushButton { padding: 9px; }
        QComboBox { padding: 7px; }
    """)
    menu = MenuWindow()
    menu.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
