import json
import re
from pathlib import Path
from typing import Dict, List, Optional


class TypeScriptConfig:
    """TypeScript設定を管理するクラス"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.config_file = base_dir / "tsconfig.json"
        self.paths: Dict[str, List[str]] = {}
        self.base_url: str = "."
        self._load_config()

    def _load_config(self) -> None:
        """tsconfig.jsonを読み込む"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                config = json.load(f)

            if "compilerOptions" in config:
                compiler_options = config["compilerOptions"]
                self.base_url = compiler_options.get("baseUrl", ".")

                if "paths" in compiler_options:
                    self.paths = compiler_options["paths"]

    def resolve_alias(self, import_path: str, file_path: Path) -> Optional[Path]:
        """エイリアスパスを実際のファイルパスに解決する

        Args:
            import_path: エイリアスパス (例: "@/components/Button")
            file_path: インポート元のファイルパス

        Returns:
            解決されたファイルパス、見つからない場合はNone
        """
        for alias_pattern, target_paths in self.paths.items():
            # エイリアスパターンを正規表現に変換
            alias_regex = re.escape(alias_pattern).replace("\\*", "(.*)")
            match = re.match(f"^{alias_regex}$", import_path)

            if match:
                wildcard = match.group(1) if "*" in alias_pattern else ""
                for target_pattern in target_paths:
                    resolved_path = (
                        target_pattern.replace("*", wildcard)
                        if "*" in target_pattern
                        else target_pattern
                    )
                    full_path = (
                        self.base_dir / self.base_url / resolved_path
                    ).resolve()

                    # 拡張子の補完を試みる
                    for ext in [".ts", ".tsx", ".js", ".jsx"]:
                        test_path = full_path.with_suffix(ext)
                        if test_path.exists():
                            return test_path

                        # index.tsなどのパターンもチェック
                        index_path = full_path / f"index{ext}"
                        if index_path.exists():
                            return index_path

        return None
