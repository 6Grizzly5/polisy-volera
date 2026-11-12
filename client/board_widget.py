from math import hypot

from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QFont
from PyQt6.QtWidgets import QWidget

from common.constants import THIEF, POLICE


class BoardWidget(QWidget):
    positionClicked = pyqtSignal(int)

    # Coordonnées du vrai plateau circulaire.
    POINTS = {
        0: (300, 300),
        1: (300, 55),
        2: (300, 190),
        3: (480, 120),
        4: (410, 300),
        5: (545, 300),
        6: (480, 480),
        7: (300, 410),
        8: (300, 545),
        9: (120, 480),
        10: (190, 300),
        11: (55, 300),
        12: (120, 120),
    }

    def __init__(self, board, state, parent=None):
        super().__init__(parent)
        self.board = board
        self.state = state
        self.selected = None
        self.setMinimumSize(620, 620)

    def set_state(self, state):
        self.state = state
        self.selected = None
        self.update()

    def _point(self, pos):
        x, y = self.POINTS[pos]
        side = min(self.width(), self.height())
        ox = (self.width() - side) / 2
        oy = (self.height() - side) / 2
        scale = side / 600
        return QPointF(ox + x * scale, oy + y * scale)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height())
        ox = (self.width() - side) / 2
        oy = (self.height() - side) / 2
        scale = side / 600

        p.fillRect(self.rect(), QBrush(Qt.GlobalColor.white))

        # Grand cercle traditionnel.
        p.setPen(QPen(Qt.GlobalColor.black, max(2, int(3 * scale))))
        p.drawEllipse(int(ox + 40 * scale), int(oy + 40 * scale),
                      int(520 * scale), int(520 * scale))

        # Toutes les arêtes du graphe, y compris les arcs extérieurs.
        drawn = set()
        p.setPen(QPen(Qt.GlobalColor.black, max(2, int(2.5 * scale))))
        for a in self.board.positions():
            for b in self.board.get_neighbors(a):
                edge = tuple(sorted((a, b)))
                if edge in drawn:
                    continue
                drawn.add(edge)
                p.drawLine(self._point(a), self._point(b))

        # Sommets.
        for pos in self.POINTS:
            c = self._point(pos)
            r = 18 * scale
            if pos == self.selected:
                fill = Qt.GlobalColor.yellow
            else:
                fill = Qt.GlobalColor.white
            p.setBrush(QBrush(fill))
            p.setPen(QPen(Qt.GlobalColor.black, 2))
            p.drawEllipse(c, r, r)
            p.setPen(QPen(Qt.GlobalColor.darkGray))
            p.setFont(QFont("Arial", max(9, int(10 * scale))))
            text = str(pos)
            p.drawText(c + QPointF(-4 if pos < 10 else -7, 4), text)

        self._draw_piece(p, self.state.thief_position, THIEF)
        for pos in self.state.police_positions:
            self._draw_piece(p, pos, POLICE)

    def _draw_piece(self, p, pos, role):
        c = self._point(pos)
        r = 14 * min(self.width(), self.height()) / 600
        brush = Qt.GlobalColor.darkRed if role == THIEF else Qt.GlobalColor.darkBlue
        p.setBrush(QBrush(brush))
        p.setPen(QPen(Qt.GlobalColor.black, 2))
        p.drawEllipse(c, r, r)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        click = event.position()
        side = min(self.width(), self.height())
        threshold = 34 * side / 600
        best = None
        best_distance = threshold
        for pos in self.POINTS:
            c = self._point(pos)
            d = hypot(click.x() - c.x(), click.y() - c.y())
            if d < best_distance:
                best = pos
                best_distance = d
        if best is not None:
            self.positionClicked.emit(best)
