import json
import socket
import unittest

from common.constants import POLICE, THIEF
from server.game_server import GameServer


def send_message(sock, message):
    sock.sendall((json.dumps(message) + "\n").encode("utf-8"))


def receive_message(sock):
    data = b""
    while b"\n" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Le serveur a fermé la connexion.")
        data += chunk
    line = data.split(b"\n", 1)[0]
    return json.loads(line.decode("utf-8"))


class LanServerTests(unittest.TestCase):
    def setUp(self):
        self.server = GameServer(POLICE, host="127.0.0.1", port=0)
        self.server.start()
        self.port = self.server.server_socket.getsockname()[1]
        self.sockets = []

    def tearDown(self):
        for sock in self.sockets:
            try:
                sock.close()
            except OSError:
                pass
        self.server.stop()

    def connect_player(self, role):
        sock = socket.create_connection(("127.0.0.1", self.port), timeout=2)
        sock.settimeout(2)
        self.sockets.append(sock)
        send_message(sock, {
            "type": "HELLO",
            "version": 1,
            "role": role,
        })
        return sock

    def test_two_opposite_roles_start_and_sync_a_move(self):
        police = self.connect_player(POLICE)
        self.assertEqual(receive_message(police)["type"], "WAITING")

        thief = self.connect_player(THIEF)
        self.assertEqual(receive_message(police)["type"], "START")
        self.assertEqual(receive_message(thief)["type"], "START")

        send_message(thief, {
            "type": "MOVE",
            "move": {"player": THIEF, "from": 0, "to": 2},
        })
        police_state = receive_message(police)
        thief_state = receive_message(thief)
        self.assertEqual(police_state["type"], "STATE")
        self.assertEqual(thief_state["type"], "STATE")
        self.assertEqual(police_state["state"]["thief"], 2)
        self.assertEqual(thief_state["state"], police_state["state"])

    def test_duplicate_role_is_rejected_with_guidance(self):
        first = self.connect_player(POLICE)
        self.assertEqual(receive_message(first)["type"], "WAITING")

        duplicate = self.connect_player(POLICE)
        response = receive_message(duplicate)
        self.assertEqual(response["type"], "ERROR")
        self.assertIn("Voleur", response["message"])


if __name__ == "__main__":
    unittest.main()