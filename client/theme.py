"""Thème visuel de l'application (couleurs + feuille de style Qt).

Ce module ne contient AUCUNE logique de jeu : uniquement de l'apparence.
"""

# --- Palette "néon arcade" ---------------------------------------------
BG_TOP = "#070A1C"
BG_MID = "#120B30"
BG_BOT = "#060818"

BG_ALT = "#10153A"
SURFACE = "#1A2150"
SURFACE_HOVER = "#252E6B"
BORDER = "#2C3366"

TEXT = "#F2F4FF"
TEXT_MUTED = "#8C94C8"

VIOLET = "#7C5CFF"
CYAN = "#35C8FF"
PINK = "#FF4D7D"
GOLD = "#FFC857"
GOLD_DEEP = "#FF9F2E"

ACCENT = GOLD
POLICE_COLOR = CYAN
THIEF_COLOR = PINK
SUCCESS = "#3DDC97"
DANGER = PINK

FONT_FAMILIES = ["Bahnschrift", "Segoe UI Variable", "Segoe UI", "Arial"]
FONT_CSS = '"Bahnschrift", "Segoe UI Variable", "Segoe UI", Arial, sans-serif'

APP_STYLESHEET = f"""
QWidget {{
    font-family: {FONT_CSS};
    font-size: 14px;
    color: {TEXT};
}}

QLabel {{
    background: transparent;
}}

QLabel#gameTitle {{
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 3px;
    color: {TEXT};
}}

QLabel#fieldLabel {{
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 4px;
    color: {GOLD};
}}

QLabel#statusInfo {{
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
    color: {TEXT};
    padding: 12px 16px;
    background: transparent;
}}

QLabel#lanInfo {{
    font-size: 12px;
    color: {GOLD};
}}

QLabel#menuInfo {{
    font-size: 12px;
    color: {TEXT_MUTED};
}}

QLabel#badge {{
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    color: {CYAN};
    background-color: rgba(53, 200, 255, 25);
    border: 1px solid rgba(53, 200, 255, 120);
    border-radius: 13px;
    padding: 5px 14px;
}}

/* Boutons génériques (boîtes de dialogue) */
QPushButton {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 9px 18px;
    font-weight: 700;
}}
QPushButton:hover {{
    background-color: {SURFACE_HOVER};
    border-color: {GOLD};
}}

QComboBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 9px 14px;
    font-weight: 700;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_ALT};
    border: 1px solid {BORDER};
    selection-background-color: {SURFACE_HOVER};
    selection-color: {GOLD};
    outline: none;
}}

QLineEdit {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 9px 12px;
    selection-background-color: {GOLD};
    selection-color: #1A1405;
}}
QLineEdit:focus {{
    border-color: {GOLD};
}}

QDialog, QMessageBox, QInputDialog {{
    background-color: {BG_ALT};
}}
QMessageBox QPushButton, QInputDialog QPushButton {{
    min-width: 80px;
}}

QToolTip {{
    background-color: {BG_ALT};
    color: {TEXT};
    border: 1px solid {BORDER};
    padding: 4px 8px;
}}
"""
