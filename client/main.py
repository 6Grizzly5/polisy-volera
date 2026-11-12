import socket
import sys

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QHBoxLayout, QInputDialog, QLabel,
    QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget
)

from common.board import Board
from common.constants import GAME_ONGOING, POLICE, POLICE_WINS, PORT, THIEF, THIEF_WINS
from common.game_state import GameState
from common.move import Move
from client.board_widget import BoardWidget
from client.network import NetworkClient
from client.local_game import LocalGameController
from server.game_server import GameServer


class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.server = None
        self.setWindowTitle("Polisy sy Volera - V2")
        self.setMinimumSize(480, 430)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(45, 35, 45, 35)

        title = QLabel("POLISY SY VOLERA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)

        sub = QLabel("Jeu traditionnel malgache • Prototype V2")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)
        layout.addStretch()

        role = QComboBox()
        role.addItem("Police", POLICE)
        role.addItem("Voleur", THIEF)
        layout.addWidget(QLabel("Votre rôle :"))
        layout.addWidget(role)
        self.role_combo = role

        local = QPushButton("🤖 Jouer contre le bot")
        lan_create = QPushButton("🌐 Créer une partie LAN")
        lan_join = QPushButton("🔗 Rejoindre une partie LAN")
        quit_btn = QPushButton("Quitter")
        layout.addWidget(local)
        layout.addWidget(lan_create)
        layout.addWidget(lan_join)
        layout.addWidget(quit_btn)

        local.clicked.connect(self.start_local)
        lan_create.clicked.connect(self.create_game)
        lan_join.clicked.connect(self.join_game)
        quit_btn.clicked.connect(QApplication.quit)

        self.info = QLabel("")
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info.setWordWrap(True)
        layout.addWidget(self.info)

    def start_local(self):
        role = self.role_combo.currentData()
        self.game = GameWindow(role, None, self, None, local=True)
        self.game.show()
        self.hide()
        self.game.start_local(role)

    def create_game(self):
        role = self.role_combo.currentData()
        try:
            self.server = GameServer(role)
            self.server.start()
            self.game = GameWindow(role, "127.0.0.1", self, self.server)
            self.game.lan_info_label.setText(
                f"Partagez cette adresse avec l'autre joueur : "
                f"{self.local_ip()} • Port {PORT}"
            )
            self.game.show()
            self.hide()
            self.game.connect_to_server()
        except Exception as exc:
            if self.server:
                self.server.stop()
                self.server = None
            QMessageBox.critical(self, "Erreur", str(exc))

    def join_game(self):
        ip, ok = QInputDialog.getText(self, "Rejoindre", "IP du PC serveur :")
        if not ok or not ip.strip():
            return
        role = self.role_combo.currentData()
        self.game = GameWindow(role, ip.strip(), self, None)
        self.game.show()
        self.hide()
        self.game.connect_to_server()

    @staticmethod
    def local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
        finally:
            s.close()


class GameWindow(QMainWindow):
    def __init__(self, role, host, menu, server=None, local=False):
        super().__init__()
        self.role = role
        self.host = host
        self.menu = menu
        self.server = server
        self.local = local
        self.selected = None
        self.state = GameState()
        self.network = NetworkClient() if not local else None
        self.setWindowTitle(f"Polisy sy Volera - {('Police' if role == POLICE else 'Voleur')}")
        self.resize(850, 760)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top = QHBoxLayout()
        title = QLabel(f"POLISY SY VOLERA  •  {('POLICE' if role == POLICE else 'VOLEUR')}")
        title.setStyleSheet("font-size: 19px; font-weight: 700;")
        self.connection_label = QLabel("Local" if local else "Connexion...")
        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.connection_label)
        layout.addLayout(top)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(self.info_label)

        self.lan_info_label = QLabel("")
        self.lan_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lan_info_label.setWordWrap(True)
        layout.addWidget(self.lan_info_label)

        self.board_widget = BoardWidget(Board(), self.state)
        self.board_widget.positionClicked.connect(self.click_position)
        layout.addWidget(self.board_widget, 1)

        bottom = QHBoxLayout()
        self.restart_button = QPushButton("Nouvelle partie")
        self.restart_button.clicked.connect(self.restart)
        back = QPushButton("Retour au menu")
        back.clicked.connect(self.back_to_menu)
        bottom.addWidget(self.restart_button)
        bottom.addStretch()
        bottom.addWidget(back)
        layout.addLayout(bottom)

        if self.network:
            self.network.messageReceived.connect(self.process_message)
            self.network.disconnectedSignal.connect(self.disconnected)

    def start_local(self, role):
        self.local_controller = LocalGameController(self, role)

    def connect_to_server(self):
        try:
            self.network.connect(self.host, PORT, self.role)
        except Exception as exc:
            QMessageBox.critical(self, "Connexion impossible", str(exc))
            self.back_to_menu()

    def process_message(self, message):
        typ = message.get("type")
        if typ == "WAITING":
            self.connection_label.setText("En attente du 2e joueur")
            self.info_label.setText(
                "En attente de l'autre joueur. Il doit choisir le rôle opposé."
            )
        elif typ in ("START", "STATE"):
            self.state = GameState.from_dict(message["state"])
            self.board_widget.set_state(self.state)
            self.connection_label.setText("Connecté")
            self.update_turn()
            self.show_end_if_needed()
        elif typ == "ERROR":
            self.info_label.setText("⚠ " + message.get("message", "Erreur"))
            self.connection_label.setText("Connexion refusée")
        elif typ == "DISCONNECTED":
            self.selected = None
            self.board_widget.selected = None
            self.board_widget.update()
            self.connection_label.setText("Adversaire déconnecté")
            self.info_label.setText(message.get("message", "L'autre joueur s'est déconnecté."))

    def update_turn(self):
        if self.state.status != GAME_ONGOING:
            self.info_label.setText("PARTIE TERMINÉE")
        elif self.state.current_player == self.role:
            self.info_label.setText(f"À VOUS DE JOUER • Tour {self.state.turn_number}")
        else:
            name = "VOLEUR" if self.state.current_player == THIEF else "POLICE"
            self.info_label.setText(f"Tour de l'adversaire • {name}")

    def show_end_if_needed(self):
        if self.state.status == THIEF_WINS:
            QMessageBox.information(self, "Fin", "🟤 Le voleur a réussi à revenir au centre !")
        elif self.state.status == POLICE_WINS:
            QMessageBox.information(self, "Fin", "🔵 La police a bloqué le voleur !")

    def click_position(self, pos):
        if self.local:
            self.local_controller.click_position(pos)
            return
        if self.state.status != GAME_ONGOING or self.state.current_player != self.role:
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
            self.info_label.setText("Position sélectionnée. Cliquez sur la destination.")
            return
        if pos == self.selected:
            self.selected = None
            self.board_widget.selected = None
            self.update_turn()
            self.board_widget.update()
            return
        move = Move(self.role, self.selected, pos)
        self.selected = None
        self.board_widget.selected = None
        self.board_widget.update()
        try:
            self.network.send_move(move)
        except OSError as exc:
            self.info_label.setText(f"⚠ Envoi du coup impossible : {exc}")

    def restart(self):
        if self.local:
            self.start_local(self.role)
            return
        self.info_label.setText("Redémarrage : créez une nouvelle partie pour réinitialiser le serveur.")

    def disconnected(self):
        if self.connection_label.text() != "Connexion refusée":
            QTimer.singleShot(0, lambda: self.info_label.setText("Connexion perdue."))

    def back_to_menu(self):
        if self.network:
            self.network.close()
        if self.server:
            self.server.stop()
        self.close()
        self.menu.show()

    def closeEvent(self, event):
        if self.network:
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
