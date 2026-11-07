# -*- coding: utf-8 -*-
"""
exe 开机动画（Splash Screen）
启动后无边框窗口播放 splash.mp4（白色翻盖纸盒开盖动画），
播完（或鼠标点击 / Esc 跳过）后自动进入主程序窗口。
兼容：直接 python 运行 / PyInstaller 打包成 exe。
"""
import os
import sys
import cv2
import tkinter as tk
from PIL import Image, ImageTk


def resource_path(rel_path: str) -> str:
    """兼容开发环境与 PyInstaller 打包后的资源路径。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)


class SplashScreen:
    """无边框开机动画窗口。"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # 去掉标题栏/边框

        self.cap = cv2.VideoCapture(resource_path("splash.mp4"))
        if not self.cap.isOpened():
            # 视频打不开就直接跳过动画，避免卡死
            self.root.destroy()
            return

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
        self.delay = max(1, int(1000 / self.fps))

        w, h = 1280, 720
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
        self.root.configure(bg="#f2f2f2")

        self.label = tk.Label(self.root, bg="#f2f2f2")
        self.label.pack()

        self.root.bind("<Button-1>", lambda e: self.finish())
        self.root.bind("<Escape>", lambda e: self.finish())

        self.playing = True
        self.photo = None
        self.root.after(0, self.update_frame)

    def update_frame(self):
        if not self.playing:
            return
        ok, frame = self.cap.read()
        if not ok:  # 视频播放完毕
            self.finish()
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        self.photo = ImageTk.PhotoImage(img)  # 保持引用防回收
        self.label.configure(image=self.photo)
        self.root.after(self.delay, self.update_frame)

    def finish(self):
        if not self.playing:
            return
        self.playing = False
        self.cap.release()
        # 先退出主循环，再销毁窗口，避免在回调里嵌套新建 Tk
        self.root.quit()

    def show(self):
        if not self.cap.isOpened():
            return
        self.root.mainloop()
        self.root.destroy()


def open_main_window():
    """主程序界面占位。后续接入真实业务界面时替换这里即可。"""
    win = tk.Tk()
    win.title("主程序")
    win.geometry("960x640")
    win.configure(bg="white")
    tk.Label(win, text="开机动画播放完成，这里是主程序界面",
             font=("Microsoft YaHei", 20), bg="white", fg="#333").pack(expand=True)
    win.mainloop()


if __name__ == "__main__":
    splash = SplashScreen()
    splash.show()          # splash 主循环结束后再开主窗口，避免嵌套
    open_main_window()
