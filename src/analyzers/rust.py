import re
from pathlib import Path
from typing import Set

from .base import BaseAnalyzer


class RustAnalyzer(BaseAnalyzer):
    """Rust用アナライザー"""

    @property
    def file_extensions(self) -> list[str]:
        return [".rs"]

    def analyze_imports(self, content: str, file_path: Path) -> Set[str]:
        imports = set()
        patterns = [
            r"mod\s+([a-zA-Z_][a-zA-Z0-9_]*);",  # mod宣言
            r"use\s+(?:crate|super|self)::([^;]+);",  # use文
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                module_path = match.group(1)
                components = module_path.split("::")

                # モジュールパスを解決
                current_dir = file_path.parent
                for component in components:
                    # modディレクトリ内のファイルをチェック
                    mod_file = current_dir / component / "mod.rs"
                    if mod_file.exists():
                        normalized_path = self.normalize_path(mod_file)
                        imports.add(normalized_path)

                    # 直接のRustファイルをチェック
                    rs_file = current_dir / f"{component}.rs"
                    if rs_file.exists():
                        normalized_path = self.normalize_path(rs_file)
                        imports.add(normalized_path)

                    current_dir = current_dir / component

        return imports
