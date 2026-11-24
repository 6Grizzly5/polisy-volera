"""Widgets purement visuels (style "jeu vidéo").

Aucune logique de jeu ici : fond animé, titre néon, boutons, cartes de rôle,
panneau de statut et dessin des pions.
"""
import math
import random
import time

from PyQt6.QtCore import QEasingCurve, QPointF, QRectF, QSize, Qt, QTimer, QVariantAnimation
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QFontMetrics, QLinearGradient, QPainter, QPainterPath, QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import QLabel, QPushButton, QWidget

from client import theme


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def game_font(pixel_size, weight=QFont.Weight.Bold, spacing=0.0):
    font = QFont()
    font.setFamilies(theme.FONT_FAMILIES)
    font.setPixelSize(int(pixel_size))
    font.setWeight(weight)
    if spacing:
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, spacing)
    return font


def with_alpha(color, alpha):
    c = QColor(color)
    c.setAlpha(max(0, min(255, int(alpha))))
    return c


def draw_glow(p, center, radius, color, alpha=120):
    grad = QRadialGradient(center, radius)
    grad.setColorAt(0.0, with_alpha(color, alpha))
    grad.setColorAt(1.0, with_alpha(color, 0))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(grad))
    p.drawEllipse(center, radius, radius)


def draw_orb(p, center, r, color, police, pulse=0.0):
    """Dessine un pion lumineux. pulse : 0..1 (battement de lueur)."""
    base = QColor(color)
    draw_glow(p, center, r * (2.3 + 0.5 * pulse), base, 90 + 70 * pulse)

    # Ombre portée.
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor(0, 0, 0, 110)))
    p.drawEllipse(center + QPointF(0, r * 0.28), r * 1.05, r * 1.05)

    # Corps.
    grad = QRadialGradient(center - QPointF(r * 0.35, r * 0.4), r * 1.7)
    grad.setColorAt(0.0, base.lighter(165))
    grad.setColorAt(0.55, base)
    grad.setColorAt(1.0, base.darker(190))
    p.setBrush(QBrush(grad))
    p.setPen(QPen(QColor(255, 255, 255, 235), max(1.5, r * 0.12)))
    p.drawEllipse(center, r, r)

    # Reflet.
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor(255, 255, 255, 70)))
    p.drawEllipse(center - QPointF(r * 0.28, r * 0.42), r * 0.42, r * 0.22)

    # Icône.
    p.setBrush(QBrush(QColor(255, 255, 255, 240)))
    if police:
        star = QPainterPath()
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rad = r * (0.5 if i % 2 == 0 else 0.21)
            pt = QPointF(center.x() + rad * math.cos(ang),
                         center.y() + rad * math.sin(ang) + r * 0.04)
            if i == 0:
                star.moveTo(pt)
            else:
                star.lineTo(pt)
        star.closeSubpath()
        p.drawPath(star)
    else:
        band = QRectF(center.x() - r * 0.62, center.y() - r * 0.3, r * 1.24, r * 0.5)
        p.setBrush(QBrush(QColor(20, 5, 20, 190)))
        p.drawRoundedRect(band, r * 0.22, r * 0.22)
        p.setBrush(QBrush(QColor(255, 255, 255, 245)))
        for dx in (-0.27, 0.27):
            p.drawEllipse(center + QPointF(r * dx, -r * 0.05), r * 0.14, r * 0.09)


# ----------------------------------------------------------------------
# Fond animé
# ----------------------------------------------------------------------
class AnimatedBackground(QWidget):
    """Fond dégradé avec lueurs et particules flottantes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        rnd = random.Random(7)
        self._particles = [
            (rnd.random(), rnd.random(), rnd.uniform(0.01, 0.045),
             rnd.uniform(0.8, 2.4), rnd.uniform(0, 6.28))
            for _ in range(70)
        ]
        self._t0 = time.monotonic()
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self.update)

    def showEvent(self, event):
        self._timer.start()
        super().showEvent(event)

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        t = time.monotonic() - self._t0

        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0.0, QColor(theme.BG_TOP))
        bg.setColorAt(0.55, QColor(theme.BG_MID))
        bg.setColorAt(1.0, QColor(theme.BG_BOT))
        p.fillRect(self.rect(), bg)

        big = max(w, h)
        for cx, cy, rad, color, alpha in (
            (0.12, 0.05, 0.75, theme.VIOLET, 85),
            (0.95, 0.98, 0.85, theme.CYAN, 42),
            (0.95, 0.02, 0.5, theme.PINK, 32),
        ):
            g = QRadialGradient(QPointF(cx * w, cy * h), rad * big)
            g.setColorAt(0.0, with_alpha(color, alpha))
            g.setColorAt(1.0, with_alpha(color, 0))
            p.fillRect(self.rect(), g)

        p.setPen(Qt.PenStyle.NoPen)
        for x, y, speed, size, phase in self._particles:
            yy = (y - t * speed) % 1.0
            xx = x + 0.012 * math.sin(t * 0.5 + phase)
            alpha = 35 + 75 * (0.5 + 0.5 * math.sin(t * 1.3 + phase))
            p.setBrush(QBrush(QColor(200, 215, 255, int(alpha))))
            p.drawEllipse(QPointF(xx * w, yy * h), size, size)

        vig = QRadialGradient(QPointF(w / 2, h / 2), big * 0.78)
        vig.setColorAt(0.55, QColor(0, 0, 0, 0))
        vig.setColorAt(1.0, QColor(0, 0, 0, 150))
        p.fillRect(self.rect(), vig)


# ----------------------------------------------------------------------
# Titre néon
# ----------------------------------------------------------------------
class TitleWidget(QWidget):
    def __init__(self, text, subtitle, parent=None):
        super().__init__(parent)
        self.text = text
        self.subtitle = subtitle
        self.setMinimumHeight(140)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        path = QPainterPath()
        path.addText(0, 0, game_font(56, QFont.Weight.Black, 6), self.text)
        br = path.boundingRect()
        scale = min(1.3, (w - 30) / br.width())
        p.save()
        p.translate(w / 2 - br.width() * scale / 2 - br.x() * scale, h * 0.5)
        p.scale(scale, scale)

        for width, alpha in ((22, 18), (14, 30), (8, 50)):
            pen = QPen(with_alpha(theme.GOLD, alpha), width)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path)

        fill = QLinearGradient(0, br.top(), 0, br.bottom())
        fill.setColorAt(0.0, QColor("#FFFFFF"))
        fill.setColorAt(0.55, QColor(theme.GOLD))
        fill.setColorAt(1.0, QColor(theme.GOLD_DEEP))
        p.setPen(QPen(QColor(255, 255, 255, 200), 1))
        p.setBrush(QBrush(fill))
        p.drawPath(path)
        p.restore()

        p.setFont(game_font(12, QFont.Weight.DemiBold, 4))
        p.setPen(QColor(theme.TEXT_MUTED))
        p.drawText(QRectF(0, h * 0.5 + 18, w, 24),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                   self.subtitle.upper())


# ----------------------------------------------------------------------
# Boutons
# ----------------------------------------------------------------------
class GameButton(QPushButton):
    """Bouton lumineux. variant : 'primary' | 'secondary' | 'ghost'."""

    def __init__(self, text, variant="secondary", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self._hover = 0.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(54 if variant != "ghost" else 42)
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._set_hover)

    def sizeHint(self):
        fm = QFontMetrics(game_font(15, QFont.Weight.Bold, 2.5))
        return QSize(fm.horizontalAdvance(self.text().upper()) + 80, self.minimumHeight())

    def _set_hover(self, value):
        self._hover = float(value)
        self.update()

    def _animate_to(self, target):
        self._anim.stop()
        self._anim.setStartValue(self._hover)
        self._anim.setEndValue(target)
        self._anim.start()

    def enterEvent(self, event):
        self._animate_to(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(0.0)
        super().leaveEvent(event)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        hv = self._hover
        rect = QRectF(self.rect()).adjusted(6, 6, -6, -6)
        if self.isDown():
            rect.translate(0, 1.5)
        radius = rect.height() * 0.32
        gold = QColor(theme.GOLD)

        if self.variant == "primary":
            for i, a in enumerate((16, 26, 40)):
                g = rect.adjusted(-6 + i * 2, -6 + i * 2, 6 - i * 2, 6 - i * 2)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(with_alpha(gold, a * (0.6 + hv))))
                p.drawRoundedRect(g, radius + 4, radius + 4)
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            grad.setColorAt(0.0, QColor("#FFE08A").lighter(100 + int(10 * hv)))
            grad.setColorAt(1.0, QColor(theme.GOLD_DEEP))
            p.setBrush(QBrush(grad))
            p.setPen(QPen(QColor(255, 240, 200, 230), 1.5))
            p.drawRoundedRect(rect, radius, radius)
            sheen = QRectF(rect.x() + 3, rect.y() + 2, rect.width() - 6, rect.height() * 0.45)
            sg = QLinearGradient(sheen.topLeft(), sheen.bottomLeft())
            sg.setColorAt(0.0, QColor(255, 255, 255, 110))
            sg.setColorAt(1.0, QColor(255, 255, 255, 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(sg))
            p.drawRoundedRect(sheen, radius - 2, radius - 2)
            text_color = QColor("#2A1600")
        elif self.variant == "secondary":
            if hv > 0:
                p.setPen(Qt.PenStyle.NoPen)
                for i, a in enumerate((14, 24)):
                    g = rect.adjusted(-5 + i * 2, -5 + i * 2, 5 - i * 2, 5 - i * 2)
                    p.setBrush(QBrush(with_alpha(theme.CYAN, a * hv)))
                    p.drawRoundedRect(g, radius + 3, radius + 3)
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            grad.setColorAt(0.0, QColor(255, 255, 255, int(26 + 24 * hv)))
            grad.setColorAt(1.0, QColor(255, 255, 255, int(8 + 14 * hv)))
            p.setBrush(QBrush(grad))
            border = QColor(theme.CYAN)
            border.setAlpha(int(90 + 150 * hv))
            p.setPen(QPen(border, 1.6))
            p.drawRoundedRect(rect, radius, radius)
            text_color = QColor(theme.TEXT)
        else:  # ghost
            if hv > 0:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(QColor(255, 255, 255, int(18 * hv))))
                p.drawRoundedRect(rect, radius, radius)
            c1, c2 = QColor(theme.TEXT_MUTED), QColor(theme.TEXT)
            text_color = QColor(
                int(c1.red() + (c2.red() - c1.red()) * hv),
                int(c1.green() + (c2.green() - c1.green()) * hv),
                int(c1.blue() + (c2.blue() - c1.blue()) * hv),
            )

        p.setFont(game_font(15, QFont.Weight.Bold, 2.5))
        p.setPen(text_color)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text().upper())


class RoleCard(QPushButton):
    """Grande carte sélectionnable (Police / Voleur)."""

    def __init__(self, police, title, subtitle, parent=None):
        super().__init__(title, parent)
        self.police = police
        self.title = title
        self.subtitle = subtitle
        self.color = theme.POLICE_COLOR if police else theme.THIEF_COLOR
        self._hover = False
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(170)
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self.update)

    def showEvent(self, event):
        self._timer.start()
        super().showEvent(event)

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        checked = self.isChecked()
        rect = QRectF(self.rect()).adjusted(8, 8, -8, -8)
        col = QColor(self.color)
        t = time.monotonic()

        if checked:
            p.setPen(Qt.PenStyle.NoPen)
            for i, a in enumerate((14, 24, 36)):
                g = rect.adjusted(-8 + i * 3, -8 + i * 3, 8 - i * 3, 8 - i * 3)
                p.setBrush(QBrush(with_alpha(col, a)))
                p.drawRoundedRect(g, 24, 24)

        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        if checked:
            grad.setColorAt(0.0, with_alpha(col, 60))
            grad.setColorAt(1.0, QColor(10, 14, 40, 230))
        else:
            grad.setColorAt(0.0, QColor(255, 255, 255, 24 if self._hover else 14))
            grad.setColorAt(1.0, QColor(10, 14, 40, 200))
        p.setBrush(QBrush(grad))
        border = with_alpha(col, 255) if checked else QColor(255, 255, 255, 70 if self._hover else 35)
        p.setPen(QPen(border, 2.2 if checked else 1.4))
        p.drawRoundedRect(rect, 20, 20)

        center = QPointF(rect.center().x(), rect.top() + 56)
        pulse = 0.5 + 0.5 * math.sin(t * 3.0) if checked else 0.0
        draw_orb(p, center, 24, col, self.police, pulse)

        p.setFont(game_font(19, QFont.Weight.Black, 3))
        p.setPen(col.lighter(125) if checked else QColor(theme.TEXT))
        p.drawText(QRectF(rect.x(), rect.top() + 92, rect.width(), 26),
                   Qt.AlignmentFlag.AlignCenter, self.title.upper())

        p.setFont(game_font(12, QFont.Weight.DemiBold, 0.5))
        p.setPen(QColor(theme.TEXT_MUTED if not checked else theme.TEXT))
        p.drawText(QRectF(rect.x() + 10, rect.top() + 120, rect.width() - 20, 34),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
                   | Qt.TextFlag.TextWordWrap, self.subtitle)


# ----------------------------------------------------------------------
# Panneau de statut
# ----------------------------------------------------------------------
class StatusLabel(QLabel):
    """QLabel dont le cadre change de couleur selon le message affiché."""

    def paintEvent(self, event):
        text = self.text()
        if text.startswith("À VOUS") or text.startswith("Position"):
            col, glow = QColor(theme.GOLD), True
        elif "⚠" in text:
            col, glow = QColor(theme.PINK), True
        else:
            col, glow = QColor(theme.VIOLET), False

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(5, 5, -5, -5)
        if glow:
            p.setPen(Qt.PenStyle.NoPen)
            for i, a in enumerate((14, 24)):
                g = rect.adjusted(-4 + i * 2, -4 + i * 2, 4 - i * 2, 4 - i * 2)
                p.setBrush(QBrush(with_alpha(col, a)))
                p.drawRoundedRect(g, 16, 16)
        grad = QLinearGradient(rect.topLeft(), rect.topRight())
        grad.setColorAt(0.0, with_alpha(col, 50))
        grad.setColorAt(0.5, QColor(12, 16, 46, 215))
        grad.setColorAt(1.0, with_alpha(col, 50))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(with_alpha(col, 210 if glow else 120), 1.5))
        p.drawRoundedRect(rect, 14, 14)
        p.end()
        super().paintEvent(event)
