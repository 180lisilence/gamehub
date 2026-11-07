"""
native_app.py — TERMINAL ARCADE PyQt6 原生窗口版
单窗口：左侧游戏列表 + 右侧游戏画面，深色 CRT 绿色主题。
"""
from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QLabel, QLineEdit, QPushButton,
    QStackedWidget, QFrame,
)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QFont, QColor

# ---- 路径 ----
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
    EXE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent
    EXE_DIR = Path(__file__).parent

sys.path.insert(0, str(BASE_DIR))
from core.scanner import scan_games

GAMES_DIR = EXE_DIR / "games"

# ---- 颜色 ----
BG = "#0a0e0a"
BG_LIGHT = "#0f1a0f"
GREEN = "#33ff33"
GREEN_DIM = "#1a8f1a"
AMBER = "#ffb000"
TEXT = "#c8ffc8"
TEXT_DIM = "#5a9a5a"
BORDER = "#1a4a1a"

STYLE = f"""
QMainWindow, QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: Consolas, monospace;
    font-size: 13px;
}}
QListWidget {{
    background-color: {BG_LIGHT};
    border: 1px solid {BORDER};
    color: {GREEN};
    padding: 4px;
}}
QListWidget::item {{
    padding: 10px 8px;
    border-bottom: 1px solid {BORDER};
}}
QListWidget::item:hover {{
    background-color: rgba(51,255,51,0.08);
}}
QListWidget::item:selected {{
    background-color: {GREEN};
    color: {BG};
}}
QLineEdit {{
    background-color: {BG_LIGHT};
    border: 1px solid {BORDER};
    color: {GREEN};
    padding: 6px;
}}
QPushButton {{
    background-color: transparent;
    border: 1px solid {GREEN};
    color: {GREEN};
    padding: 6px 16px;
    font-family: Consolas, monospace;
}}
QPushButton:hover {{
    background-color: {GREEN};
    color: {BG};
}}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TERMINAL ARCADE — 终端街机")
        self.resize(1000, 700)
        self.setStyleSheet(STYLE)

        self.games = scan_games(str(GAMES_DIR))

        # 中心堆叠：0=列表页  1=游戏页
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self._build_list_page()
        self._build_game_page()

    def _build_list_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 标题
        title = QLabel("TERMINAL ARCADE")
        title.setStyleSheet(f"color:{GREEN}; font-size:24px; font-weight:bold;")
        layout.addWidget(title)

        sub = QLabel("root@terminal:~/arcade$ cd /")
        sub.setStyleSheet(f"color:{TEXT_DIM}; font-size:11px;")
        layout.addWidget(sub)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color:{BORDER};")
        layout.addWidget(line)

        # 搜索框
        self.search = QLineEdit()
        self.search.setPlaceholderText("$ SEARCH:")
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)

        # 游戏列表
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_play)
        layout.addWidget(self.list_widget)

        # 状态栏
        self.status = QLabel(f"-- {len(self.games)} games loaded · double-click to RUN --")
        self.status.setStyleSheet(f"color:{TEXT_DIM}; font-size:11px;")
        layout.addWidget(self.status)

        self._populate("")
        self.stack.addWidget(page)

    def _build_game_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部栏：返回按钮 + 标题
        topbar = QWidget()
        topbar.setStyleSheet(f"background-color:{BG_LIGHT}; border-bottom:1px solid {BORDER};")
        top_layout = QHBoxLayout(topbar)
        top_layout.setContentsMargins(10, 8, 10, 8)

        self.back_btn = QPushButton("← EXIT / 返回列表")
        self.back_btn.clicked.connect(self._back_to_list)
        top_layout.addWidget(self.back_btn)

        self.game_title = QLabel("")
        self.game_title.setStyleSheet(f"color:{GREEN}; font-size:16px; font-weight:bold;")
        top_layout.addWidget(self.game_title)
        top_layout.addStretch()

        layout.addWidget(topbar)

        # 网页视图
        self.web = QWebEngineView()
        self.web.setStyleSheet("background:#000;")
        layout.addWidget(self.web)

        self.stack.addWidget(page)

    def _populate(self, keyword):
        self.list_widget.clear()
        for g in self.games:
            if keyword and keyword.lower() not in g.title.lower() and keyword.lower() not in g.description.lower():
                continue
            item = QListWidgetItem(f"  {g.title}   ★{g.rating}  [{g.age_rating}]")
            item.setData(Qt.ItemDataRole.UserRole, g)
            self.list_widget.addItem(item)

    def _filter(self, text):
        self._populate(text.strip())

    def _on_play(self, item: QListWidgetItem):
        game = item.data(Qt.ItemDataRole.UserRole)
        self.game_title.setText(f"RUN {game.id} — {game.title}")

        game_path = GAMES_DIR / game.folder / game.entry
        if game_path.exists():
            self.web.setUrl(QUrl.fromLocalFile(str(game_path)))
            self.stack.setCurrentIndex(1)

    def _back_to_list(self):
        self.web.stop()
        self.web.setUrl(QUrl("about:blank"))
        self.stack.setCurrentIndex(0)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
