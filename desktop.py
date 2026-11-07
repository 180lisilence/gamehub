"""
desktop.py — TERMINAL ARCADE 桌面版启动器
双击运行，直接弹出游戏平台窗口，不打开浏览器。
"""
from __future__ import annotations

import threading
import time
import sys
import socket
from pathlib import Path

import webview

HOST = "127.0.0.1"
PORT = 8000


def run_server():
    """后台线程：启动 FastAPI + uvicorn。"""
    import uvicorn
    from app import app
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")


def wait_for_server(timeout: float = 20.0):
    """等服务器端口可连（onefile 解压慢，给足时间）。"""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.create_connection((HOST, PORT), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def main():
    # 1. 后台起服务器
    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    # 2. 先开一个黑色窗口（不指向 URL，避免连接拒绝报错页）
    window = webview.create_window(
        "TERMINAL ARCADE — 终端街机",
        width=1100,
        height=800,
        resizable=True,
        background_color="#000000",
    )

    # 3. 等服务器就绪后再加载页面
    def _load_when_ready():
        if wait_for_server():
            window.load_url(f"http://{HOST}:{PORT}")
        else:
            window.load_html("<body style='background:#000;color:#33ff33;font-family:monospace;padding:40px'><h2>服务器启动超时</h2><p>请关闭后重试。</p></body>")

    threading.Thread(target=_load_when_ready, daemon=True).start()

    # 4. 显示黑色窗口，等服务器加载完自动跳转到主页面
    webview.start()


if __name__ == "__main__":
    main()
