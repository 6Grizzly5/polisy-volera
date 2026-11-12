import json
import socket
import threading

from common.board import Board
from common.game_state import GameState
from common.move import Move
from common.rules import Rules
from common.constants import THIEF, POLICE, PORT, PROTOCOL_VERSION

class GameServer:
    """Serveur TCP arbitre une seule partie LAN."""

    def __init__(self, host_role, host="0.0.0.0", port=PORT, log=None):
        if host_role not in (THIEF, POLICE):
            raise ValueError("Le rôle de l'hôte doit être Police ou Voleur.")
        self.host_role = host_role
        self.host = host
        self.port = port
        self.log = log or (lambda _: None)
        self.board = Board()
        self.state = GameState()
        self.server_socket = None
        self.clients = {}
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(2)
        except OSError:
            self.server_socket.close()
            self.server_socket = None
            raise
        self.running = True
        self.log(f"Serveur prêt : port {self.port}")
        threading.Thread(target=self.accept_loop, daemon=True).start()

    def accept_loop(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
            except OSError:
                break
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        role = None
        try:
            hello = self.recv_one(conn)
            if hello.get("type") != "HELLO" or hello.get("version") != PROTOCOL_VERSION:
                self.send(conn, {"type": "ERROR", "message": "Protocole incompatible."})
                return

            requested = hello.get("role")
            if requested not in (THIEF, POLICE):
                self.send(conn, {"type": "ERROR", "message": "Rôle invalide."})
                return

            with self.lock:
                if requested in self.clients:
                    available_role = THIEF if self.host_role == POLICE else POLICE
                    role_name = "Voleur" if available_role == THIEF else "Police"
                    self.send(conn, {
                        "type": "ERROR",
                        "message": f"Ce rôle est déjà pris. Choisissez le rôle {role_name} sur l'écran d'accueil.",
                    })
                    return
                role = requested
                self.clients[role] = conn

            self.log(f"{addr[0]} connecté comme {role}")

            if len(self.clients) < 2:
                self.send(conn, {"type": "WAITING", "role": role, "state": self.state.to_dict()})
            else:
                self.broadcast({
                    "type": "START",
                    "state": self.state.to_dict(),
                })
                self.log("Deux joueurs connectés : partie démarrée.")

            buffer = b""
            while self.running:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if line.strip():
                        self.process_message(role, json.loads(line.decode("utf-8")))

        except Exception as exc:
            self.log(f"Client {addr[0]} : {exc}")
        finally:
            with self.lock:
                if role:
                    self.clients.pop(role, None)
            if role and self.running:
                self.broadcast({
                    "type": "DISCONNECTED",
                    "message": "L'autre joueur s'est déconnecté. Recréez une partie pour rejouer.",
                })
            try:
                conn.close()
            except Exception:
                pass

    def process_message(self, role, message):
        if message.get("type") != "MOVE":
            return
        move = Move.from_dict(message["move"])

        if move.player != role:
            self.send(self.clients.get(role), {"type": "ERROR", "message": "Rôle de coup invalide."})
            return

        with self.lock:
            if len(self.clients) < 2:
                self.send(self.clients.get(role), {
                    "type": "ERROR",
                    "message": "En attente de la connexion de l'autre joueur.",
                })
                return
            try:
                self.state = Rules.apply_move(self.state, move, self.board)
            except ValueError as exc:
                self.send(self.clients.get(role), {"type": "ERROR", "message": str(exc)})
                return

            self.broadcast({
                "type": "STATE",
                "state": self.state.to_dict(),
                "last_move": move.to_dict(),
            })

    def broadcast(self, payload):
        for conn in list(self.clients.values()):
            try:
                self.send(conn, payload)
            except OSError:
                pass

    @staticmethod
    def send(conn, payload):
        if conn:
            conn.sendall((json.dumps(payload) + "\n").encode("utf-8"))

    @staticmethod
    def recv_one(conn):
        data = b""
        while b"\n" not in data:
            chunk = conn.recv(4096)
            if not chunk:
                raise ConnectionError("Connexion fermée.")
            data += chunk
        line = data.split(b"\n", 1)[0]
        return json.loads(line.decode("utf-8"))

    def stop(self):
        self.running = False
        try:
            if self.server_socket:
                self.server_socket.close()
        except Exception:
            pass
        for conn in list(self.clients.values()):
            try:
                conn.close()
            except Exception:
                pass
        self.clients.clear()
