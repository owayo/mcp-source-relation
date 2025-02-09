import re
from pathlib import Path
from typing import Set

from .base import BaseAnalyzer
from ..configs.typescript import TypeScriptConfig


class TypeScriptAnalyzer(BaseAnalyzer):
    """TypeScript/JavaScript用アナライザー"""

    def __init__(self, base_dir: Path):
        super().__init__(base_dir)
        self.ts_config = TypeScriptConfig(base_dir)

    @property
    def file_extensions(self) -> list[str]:
        return [".ts", ".tsx", ".js", ".jsx"]

    def analyze_imports(self, content: str, file_path: Path) -> Set[str]:
        imports = set()
        patterns = [
            # 通常のインポート
            r'import\s+(?:{[^}]*}|\*\s+as\s+[^,]+|[^,{]*)\s+from\s+[\'"]([^\'""]+)[\'"]',
            # 型のインポート
            r'import\s+type\s+(?:{[^}]*}|\*\s+as\s+[^,]+|[^,{]*)\s+from\s+[\'"]([^\'""]+)[\'"]',
            # CSSのインポート
            r'import\s+[\'"]([^\'""]+)[\'"]',
            # require
            r'require\([\'"]([^\'""]+)[\'"]\)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                import_path = match.group(1)

                resolved_path = None
                if import_path.startswith("."):
                    # 相対パスの解決
                    resolved_path = self.resolve_relative_path(
                        import_path, file_path, allow_index=True
                    )
                else:
                    # エイリアスパスの解決
                    resolved_path = self.ts_config.resolve_alias(import_path, file_path)

                if resolved_path:
                    normalized_path = self.normalize_path(resolved_path)
                    imports.add(normalized_path)

        return imports
