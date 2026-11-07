# TERMINAL ARCADE · 终端街机

> 一个 CRT 复古终端风的网页游戏平台：浏览器即玩，目录即游戏库，加游戏零平台代码改动。

[![Platform](https://img.shields.io/badge/platform-FastAPI-33ff77)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

🌐 **在线演示：** https://180lisilence.github.io/gamehub/

---

## 这是什么

`gamehub` 是一个用 **Python (FastAPI)** 写的网页游戏平台，视觉采用 **CRT 复古终端 × 街机** 风格：
扫描线、荧光等宽字体、开机自检动画、打字机标题。游戏卡片像「终端程序条目」，
筛选即「输入指令」，进游戏即 `RUN <id>`，返回即 `EXIT`。

核心理念是 **「目录即游戏库」**：平台代码与游戏本体完全解耦。后期加游戏 =
复制一个文件夹 + 写一份 `manifest.json`，平台代码零改动、自动注册、自动出现在首页/分类/搜索。

## 核心特性

- **即点即玩**：浏览器访问，无需下载安装，HTML5 小游戏秒开。
- **零代码扩展**：新增游戏只需放文件夹 + 写 manifest，平台自动扫描注册。
- **复古终端 UI**：CRT 扫描线、荧光绿/琥珀双色、开机自检与打字机动效。
- **筛选 / 搜索 / 分页**：分类、标签、关键字检索，服务端分页，推荐位（`featured`）。
- **热重载**：加完游戏访问 `/reload` 即可生效，无需重启服务。
- **多形态游戏**：HTML5 网页游戏 + 本地 exe 拉起（`/launch`）。

## 技术栈

FastAPI · Jinja2 · SQLite · 原生 HTML/CSS/JS · PyInstaller · uvicorn

平台层用 Python 负责路由、扫描、筛选、热度统计；游戏本体为 HTML5 单文件小游戏（JS），
由 Python 统一挂载在 `/games` 下。也可通过 `/launch` 拉起同目录的本地 exe。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务（开发模式）
python app.py
#   或：python main.py   （带开机动画的窗口形态）

# 3. 浏览器打开
#   http://127.0.0.1:8000

# 加完新游戏后，热重载（无需重启）：
#   http://127.0.0.1:8000/reload
```

## 项目结构

```
gamehub/
├── app.py                 # FastAPI 入口：启动即扫描 games/，渲染首页
├── main.py                # 带开机动画的窗口形态入口
├── desktop.py             # 桌面启动器（.bat 调用）
├── native_app.py          # 原生窗口外壳
├── game_window.py         # 游戏窗口
├── core/
│   ├── scanner.py         # 扫描 games/，解析 manifest.json
│   └── registry.py        # 游戏注册表（内存索引 + SQLite 持久化）
├── templates/             # Jinja2 模板（CRT 外壳 / 首页 / 游戏运行页）
├── static/                # 主题 CSS / 图片 / JS
├── games/                 # ★ 游戏库：后期加游戏只动这里
│   ├── 2048/
│   ├── snake/
│   └── notepad_demo/
├── data/                  # SQLite 与统计
└── requirements.txt
```

## 如何添加一款新游戏

在 `games/` 下新建 `<game_id>/`，放入游戏本体 `index.html`（可带自己的 js/css）和缩略图，再写一份 `manifest.json`：

```json
{
  "id": "2048",
  "title": "2048",
  "version": "1.0.0",
  "categories": ["休闲", "解谜"],
  "tags": ["数字", "益智", "单机"],
  "rating": 4.5,
  "description": "滑动合并数字，挑战 2048。",
  "entry": "index.html",
  "thumbnail": "thumb.png",
  "featured": true
}
```

保存后访问 `/reload` → 平台自动扫描注册 → 该游戏立即出现在首页、分类、搜索、标签中，平台代码零改动。

## 仓库说明

- 根目录 `index.html` 是项目介绍页（CRT 风格），同时作为 GitHub Pages 站点页面。
- `templates/index.html` 是平台运行时的首页（由 FastAPI 渲染），二者用途不同。

## 许可

示例游戏均为自制或采用开源协议素材，可自由学习、二次开发与部署。
