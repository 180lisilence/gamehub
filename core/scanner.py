"""
scanner.py — 扫描 games/ 目录，解析每个游戏的 manifest.json
后期加游戏 = 复制文件夹 + 写 manifest.json，平台代码零改动。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


@dataclass
class Game:
    id: str
    title: str
    version: str = "1.0.0"
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    rating: float = 0.0
    age_rating: str = "全年龄"
    description: str = ""
    entry: str = "index.html"
    thumbnail: str = ""
    featured: bool = False
    # 类型：html = 网页游戏（iframe 打开）；exe = 本地 Windows 程序（点按钮启动）
    type: str = "html"
    exe: str = ""             # type=exe 时填写，相对游戏文件夹的 exe 路径（也可写绝对路径）
    # 运行时字段
    folder: str = ""          # 相对 games/ 的文件夹名
    has_thumbnail: bool = False
    has_exe: bool = False      # type=exe 时，exe 文件是否真实存在

    def to_dict(self) -> dict:
        return asdict(self)


def _manifest_schema_ok(data: dict) -> bool:
    """manifest 至少要有 id 和 title。"""
    return bool(data.get("id") and data.get("title"))


def scan_games(games_dir: str | Path) -> List[Game]:
    """
    扫描 games/ 下所有子目录，读取 manifest.json，返回 Game 列表。
    损坏的 manifest 会被跳过并打印警告，不影响其他游戏。
    """
    games_path = Path(games_dir)
    if not games_path.exists():
        return []

    games: List[Game] = []
    for child in sorted(games_path.iterdir()):
        if not child.is_dir():
            continue
        manifest_file = child / "manifest.json"
        if not manifest_file.exists():
            print(f"[scanner] 跳过 {child.name}: 缺少 manifest.json")
            continue

        try:
            raw = json.loads(manifest_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"[scanner] 跳过 {child.name}: manifest.json 解析失败 ({e})")
            continue

        if not _manifest_schema_ok(raw):
            print(f"[scanner] 跳过 {child.name}: manifest 缺少 id/title")
            continue

        thumb = raw.get("thumbnail", "")
        has_thumb = bool(thumb) and (child / thumb).exists()

        g_type = raw.get("type", "html")
        exe_rel = raw.get("exe", "")
        # exe 路径：支持相对游戏文件夹，也支持绝对路径
        has_exe = False
        if g_type == "exe" and exe_rel:
            exe_candidate = Path(exe_rel)
            if not exe_candidate.is_absolute():
                exe_candidate = child / exe_rel
            has_exe = exe_candidate.exists()

        game = Game(
            id=raw["id"],
            title=raw["title"],
            version=raw.get("version", "1.0.0"),
            categories=list(raw.get("categories", [])),
            tags=list(raw.get("tags", [])),
            rating=float(raw.get("rating", 0)),
            age_rating=raw.get("age_rating", "全年龄"),
            description=raw.get("description", ""),
            entry=raw.get("entry", "index.html"),
            thumbnail=thumb,
            featured=bool(raw.get("featured", False)),
            type=g_type,
            exe=exe_rel,
            folder=child.name,
            has_thumbnail=has_thumb,
            has_exe=has_exe,
        )
        games.append(game)

    return games
