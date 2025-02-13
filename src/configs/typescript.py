import json
import json5
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
        """tsconfig.jsonを読み込む

        Notes:
            - JSONおよびJSON5形式のtsconfig.jsonファイルに対応
            - ファイルが存在しない場合はデフォルト設定を使用
            - パース時のエラーはログに記録
        """
        if not self.config_file.exists():
            print(f"Warning: {self.config_file} not found. Using default settings.")
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                content = f.read()
                try:
                    # まずJSON5としてパースを試みる
                    config = json5.loads(content)
                except Exception as e:
                    print(f"Warning: Failed to parse {self.config_file} as JSON5: {e}")
                    try:
                        # 通常のJSONとしてパースを試みる
                        config = json.loads(content)
                    except json.JSONDecodeError as je:
                        print(f"Error: Failed to parse {self.config_file}: {je}")
                        return

            if isinstance(config, dict) and "compilerOptions" in config:
                compiler_options = config["compilerOptions"]
                self.base_url = compiler_options.get("baseUrl", ".")

                if "paths" in compiler_options:
                    self.paths = compiler_options["paths"]
        except Exception as e:
            print(f"Error: Failed to read {self.config_file}: {e}")

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
