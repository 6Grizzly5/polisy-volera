import json
import socket
import threading

from PyQt6.QtCore import QObject, pyqtSignal
from common.constants import PROTOCOL_VERSION

class NetworkClient(QObject):
    messageReceived = pyqtSignal(dict)
    disconnectedSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sock = None
        self.running = False
        self.send_lock = threading.Lock()

    def connect(self, host, port, role):
        self.sock = socket.create_connection((host, port), timeout=5)
        self.sock.settimeout(None)
        self.running = True
        self.send({"type": "HELLO", "version": PROTOCOL_VERSION, "role": role})
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def receive_loop(self):
        buffer = b""
        sock = self.sock
        try:
            while self.running:
                data = sock.recv(4096)
                if not data:
                    break
                buffer += data
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if line.strip():
                        self.messageReceived.emit(
                            json.loads(line.decode("utf-8"))
                        )
        except Exception as exc:
            if self.running:
                self.messageReceived.emit({
                    "type": "ERROR",
                    "message": f"Connexion réseau : {exc}"
                })
        finally:
            self.running = False
            self.disconnectedSignal.emit()

    def send(self, payload):
        if not self.sock:
            raise OSError("La connexion au serveur n'est pas ouverte.")
        data = (json.dumps(payload) + "\n").encode("utf-8")
        with self.send_lock:
            self.sock.sendall(data)

    def send_move(self, move):
        self.send({
            "type": "MOVE",
            "move": move.to_dict(),
        })

    def close(self):
        self.running = False
        if not self.sock:
            return
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass
        self.sock = None
