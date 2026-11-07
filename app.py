"""
TERMINAL ARCADE — 终端街机
FastAPI 入口：启动即扫描 games/，渲染首页。

运行：
    cd gamehub
    pip install -r requirements.txt
    python app.py
然后浏览器打开 http://127.0.0.1:8000
"""
from __future__ import annotations

import sys
from pathlib import Path

import jinja2
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.registry import GameRegistry

# ---- 路径处理：兼容 PyInstaller 打包 ----
# 打包后：templates/static 在 _MEIPASS 临时目录；games/ 在 exe 旁边（外部，方便加游戏）
# 开发时：全部相对脚本目录
if getattr(sys, "frozen", False):
    BUNDLE_DIR = Path(sys._MEIPASS)          # PyInstaller 解压目录（内含 templates/static）
    EXE_DIR = Path(sys.executable).parent     # exe 所在目录（games/ 放这里）
else:
    BUNDLE_DIR = Path(__file__).parent
    EXE_DIR = Path(__file__).parent

TEMPLATES_DIR = BUNDLE_DIR / "templates"
STATIC_DIR = BUNDLE_DIR / "static"
GAMES_DIR = EXE_DIR / "games"

app = FastAPI(title="TERMINAL ARCADE")

# 静态文件
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 游戏本体静态挂载
app.mount("/games", StaticFiles(directory=GAMES_DIR), name="games")

# Jinja2 模板（关闭缓存，兼容 Python 3.14）
_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
    cache_size=0,
    auto_reload=True,
)
templates = Jinja2Templates(env=_jinja_env)

# 启动时扫描游戏库
registry = GameRegistry(str(GAMES_DIR))
registry.reload()


@app.on_event("startup")
def startup():
    registry.reload()
    print(f"[startup] 已加载 {len(registry.all)} 款游戏")
    for g in registry.all:
        print(f"  - [{g.id}] {g.title}  (分类: {', '.join(g.categories) or '无'})")


@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    category: str | None = None,
    tag: str | None = None,
    q: str | None = None,
    page: int = 1,
):
    filtered = registry.filter(category=category, tag=tag, search=q)
    featured = registry.featured

    # 分页（每页 12 款）
    per_page = 12
    total = len(filtered)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    page_items = filtered[start:start + per_page]

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "platform_name": "TERMINAL ARCADE",
            "games": page_items,
            "featured_games": featured,
            "categories": registry.categories(),
            "tags": registry.tags(),
            "current_category": category,
            "current_tag": tag,
            "current_q": q,
            "page": page,
            "total_pages": total_pages,
            "total": total,
        },
    )


@app.get("/play/{game_id}", response_class=HTMLResponse)
def play(request: Request, game_id: str):
    game = registry.get_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    return templates.TemplateResponse(
        request,
        "game.html",
        {
            "game": game,
            "game_url": f"/games/{game.folder}/{game.entry}",
            "platform_name": "TERMINAL ARCADE",
        },
    )


@app.get("/reload")
def reload_games():
    """热重载：加完游戏访问这个地址即可，不用重启。"""
    registry.reload()
    return {"status": "ok", "loaded": len(registry.all)}


@app.get("/launch/{game_id}")
def launch(game_id: str):
    """启动本地 exe 游戏。仅 type=exe 的游戏可用。"""
    import subprocess
    game = registry.get_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    if game.type != "exe":
        raise HTTPException(status_code=400, detail="该游戏不是 exe 类型")

    # 解析 exe 路径（相对游戏文件夹或绝对路径）
    exe_path = Path(game.exe)
    if not exe_path.is_absolute():
        exe_path = GAMES_DIR / game.folder / game.exe
    if not exe_path.exists():
        raise HTTPException(status_code=404, detail=f"找不到 exe 文件: {exe_path}")

    work_dir = str(exe_path.parent)
    try:
        # 用游戏所在目录当工作目录，保证它能找到同目录的 DLL/资源
        subprocess.Popen([str(exe_path)], cwd=work_dir)
        return {"status": "ok", "launched": exe_path.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动失败: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
