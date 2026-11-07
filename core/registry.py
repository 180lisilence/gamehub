"""
registry.py — 游戏注册表：启动时扫描一次，提供查询/筛选/分页。
M1 阶段纯内存；M4 再加 SQLite 热度统计。
"""
from __future__ import annotations

from typing import List, Optional

from .scanner import Game, scan_games


class GameRegistry:
    def __init__(self, games_dir: str):
        self.games_dir = games_dir
        self._games: List[Game] = []

    def reload(self) -> None:
        """重新扫描 games/ 目录。加游戏后调用即可热更新。"""
        self._games = scan_games(self.games_dir)

    @property
    def all(self) -> List[Game]:
        return self._games

    def get_by_id(self, game_id: str) -> Optional[Game]:
        for g in self._games:
            if g.id == game_id:
                return g
        return None

    @property
    def featured(self) -> List[Game]:
        return [g for g in self._games if g.featured]

    def categories(self) -> List[str]:
        """所有出现过的分类，按出现次数排序。"""
        counts: dict[str, int] = {}
        for g in self._games:
            for c in g.categories:
                counts[c] = counts.get(c, 0) + 1
        return sorted(counts.keys(), key=lambda c: (-counts[c], c))

    def tags(self) -> List[str]:
        counts: dict[str, int] = {}
        for g in self._games:
            for t in g.tags:
                counts[t] = counts.get(t, 0) + 1
        return sorted(counts.keys(), key=lambda t: (-counts[t], t))

    def filter(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Game]:
        result = self._games
        if category:
            result = [g for g in result if category in g.categories]
        if tag:
            result = [g for g in result if tag in g.tags]
        if search:
            kw = search.lower()
            result = [
                g for g in result
                if kw in g.title.lower() or kw in g.description.lower()
            ]
        return result
