import re
from pathlib import Path
from typing import Set

from .base import BaseAnalyzer
from ..utils.path import search_in_path


class RubyAnalyzer(BaseAnalyzer):
    """Ruby用アナライザー"""

    def __init__(self, base_dir: Path):
        super().__init__(base_dir)
        # Ruby標準ライブラリやGemのパスは除外
        self.search_paths = [
            self.base_dir / "lib",
            self.base_dir / "app",
            self.base_dir,
        ]

    @property
    def file_extensions(self) -> list[str]:
        return [".rb"]

    def analyze_imports(self, content: str, file_path: Path) -> Set[str]:
        imports = set()
        patterns = [
            r'require\s+[\'"](.+?)[\'"]',
            r'require_relative\s+[\'"](.+?)[\'"]',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                path = match.group(1)

                resolved_path = None
                if pattern.startswith("require_relative"):
                    # require_relativeは現在のファイルからの相対パス
                    resolved_path = self.resolve_relative_path(
                        path, file_path, allow_index=False
                    )
                else:
                    # requireはライブラリパスから探索
                    # 拡張子がない場合は.rbを補完
                    if "." not in path:
                        path = f"{path}.rb"
                    resolved_path = search_in_path(
                        path,
                        self.search_paths,
                        self.file_extensions,
                        allow_index=False,
                    )

                if resolved_path:
                    normalized_path = self.normalize_path(resolved_path)
                    imports.add(normalized_path)

        return imports
