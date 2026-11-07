"""
game_window.py — 独立的游戏窗口进程
被 native_app.py 用 subprocess 调用，打开一个原生窗口跑 HTML5 游戏。
用法: python game_window.py <html文件路径> <窗口标题>
"""
import sys
import webview


def main():
    if len(sys.argv) < 3:
        print("用法: game_window.py <html_path> <title>")
        sys.exit(1)

    html_path = sys.argv[1]
    title = sys.argv[2]

    webview.create_window(
        title,
        url=html_path,
        width=900,
        height=700,
        resizable=True,
    )
    webview.start()


if __name__ == "__main__":
    main()
