import math
import time
from math import hypot

from PyQt6.QtCore import Qt, QPointF, QRectF, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget

from client import theme
from client.widgets import draw_glow, draw_orb, game_font, with_alpha
from common.constants import CENTER, GAME_ONGOING, POLICE, THIEF


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
        self._hover = None
        self.setMinimumSize(620, 620)
        self.setMouseTracking(True)
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self.update)

    def showEvent(self, event):
        self._timer.start()
        super().showEvent(event)

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)

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
        t = time.monotonic()
        wave = 0.5 + 0.5 * math.sin(t * 3.2)

        center = QPointF(ox + 300 * scale, oy + 300 * scale)
        radius = 262 * scale

        # Lueur de fond + disque du plateau.
        draw_glow(p, center, radius * 1.25, theme.VIOLET, 70)
        disc = QRadialGradient(center, radius)
        disc.setColorAt(0.0, QColor(46, 38, 110, 235))
        disc.setColorAt(1.0, QColor(10, 12, 38, 245))
        p.setBrush(QBrush(disc))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(center, radius, radius)

        # Anneau néon extérieur.
        p.setBrush(Qt.BrushStyle.NoBrush)
        for w, a in ((16, 20), (9, 40), (4, 90)):
            p.setPen(QPen(with_alpha(theme.VIOLET, a), w * scale))
            p.drawEllipse(center, radius, radius)
        p.setPen(QPen(QColor(190, 175, 255, 230), max(1.5, 2 * scale)))
        p.drawEllipse(center, radius, radius)
        p.setPen(QPen(with_alpha(theme.CYAN, 45), max(1, 1.5 * scale)))
        p.drawEllipse(center, radius + 16 * scale, radius + 16 * scale)

        # Arêtes du graphe (halo + trait net).
        drawn = set()
        edges = []
        for a in self.board.positions():
            for b in self.board.get_neighbors(a):
                edge = tuple(sorted((a, b)))
                if edge in drawn:
                    continue
                drawn.add(edge)
                edges.append(edge)
        for a, b in edges:
            pa, pb = self._point(a), self._point(b)
            p.setPen(QPen(with_alpha(theme.VIOLET, 38), 8 * scale, Qt.PenStyle.SolidLine,
                          Qt.PenCapStyle.RoundCap))
            p.drawLine(pa, pb)
            p.setPen(QPen(QColor(150, 165, 255, 150), max(1.5, 2.2 * scale),
                          Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(pa, pb)
        # Sommets.
        num_font = game_font(max(9, 12 * scale), QFont.Weight.DemiBold)
        for pos in self.POINTS:
            c = self._point(pos)
            is_center = pos == CENTER
            r = (23 if is_center else 18) * scale
            selected = pos == self.selected
            hovered = pos == self._hover

            if is_center:
                draw_glow(p, c, r * 2.4, theme.GOLD, 55 + 35 * wave)
            if selected:
                draw_glow(p, c, r * 2.6, theme.GOLD, 150)

            node = QRadialGradient(c - QPointF(r * 0.3, r * 0.3), r * 1.6)
            node.setColorAt(0.0, QColor(52, 60, 130))
            node.setColorAt(1.0, QColor(14, 17, 48))
            p.setBrush(QBrush(node))
            if selected:
                ring = QColor(theme.GOLD)
            elif is_center:
                ring = QColor(theme.GOLD).darker(115)
            elif hovered:
                ring = QColor(theme.CYAN)
            else:
                ring = QColor(95, 110, 210)
            p.setPen(QPen(ring, max(1.5, (2.6 if is_center or selected else 2) * scale)))
            p.drawEllipse(c, r, r)

            p.setFont(num_font)
            p.setPen(QColor(theme.GOLD) if is_center else QColor(150, 160, 215))
            p.drawText(QRectF(c.x() - r, c.y() - r, 2 * r, 2 * r),
                       Qt.AlignmentFlag.AlignCenter, str(pos))

        # Pions.
        r = 15 * scale
        thief_turn = self.state.status == GAME_ONGOING and self.state.current_player == THIEF
        police_turn = self.state.status == GAME_ONGOING and self.state.current_player == POLICE
        draw_orb(p, self._point(self.state.thief_position), r, theme.THIEF_COLOR, False,
                 wave if thief_turn else 0.0)
        for pos in self.state.police_positions:
            draw_orb(p, self._point(pos), r, theme.POLICE_COLOR, True,
                     wave if police_turn else 0.0)

    def _nearest(self, point):
        side = min(self.width(), self.height())
        best = None
        best_distance = 34 * side / 600
        for pos in self.POINTS:
            c = self._point(pos)
            d = hypot(point.x() - c.x(), point.y() - c.y())
            if d < best_distance:
                best = pos
                best_distance = d
        return best

    def mouseMoveEvent(self, event):
        hovered = self._nearest(event.position())
        if hovered != self._hover:
            self._hover = hovered
            self.setCursor(Qt.CursorShape.PointingHandCursor if hovered is not None
                           else Qt.CursorShape.ArrowCursor)
            self.update()

    def leaveEvent(self, event):
        self._hover = None
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        best = self._nearest(event.position())
        if best is not None:
            self.positionClicked.emit(best)
