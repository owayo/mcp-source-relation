import ast
from pathlib import Path
from typing import Set, Optional

from .base import BaseAnalyzer
from ..utils.path import search_in_path


class PythonAnalyzer(BaseAnalyzer):
    """Python用アナライザー

    Attributes:
        base_dir (Path): 基準となるディレクトリパス
        search_paths (list[Path]): モジュール検索パスのリスト
    """

    def __init__(self, base_dir: Path):
        super().__init__(base_dir)
        self.search_paths = [
            self.base_dir,
            self.base_dir / "src",
        ]

    @property
    def file_extensions(self) -> list[str]:
        """対象とするファイル拡張子のリストを返す

        Returns:
            list[str]: ファイル拡張子のリスト
        """
        return [".py"]

    def resolve_relative_path(
        self, import_name: str, current_file: Path, allow_init: bool = True
    ) -> Optional[Path]:
        """相対インポートのパス解決を行う

        Args:
            import_name (str): インポート名
            current_file (Path): 現在のファイルパス
            allow_init (bool): __init__.pyの許可フラグ

        Returns:
            Optional[Path]: 解決されたパス。見つからない場合はNone
        """

        try:
            # インポート名をパスに変換
            import_path = Path(import_name.replace(".", "/"))
            if allow_init:
                patterns = [f"{import_path}.py", f"{import_path}/__init__.py"]
            else:
                patterns = [f"{import_path}.py"]

            # 現在のファイルからの相対パスで検索
            current_dir = current_file.parent
            for pattern in patterns:
                potential_path = current_dir / pattern
                if potential_path.exists():
                    return potential_path

            return None

        except Exception:
            return None

    def analyze_imports(self, content: str, file_path: Path) -> Set[str]:
        """ファイル内のインポート文を解析する

        Args:
            content (str): ファイルの内容
            file_path (Path): ファイルパス

        Returns:
            Set[str]: インポートされているファイルパスの集合
        """
        imports = set()

        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom):
                    # from文の場合
                    if node.level > 0:  # 相対インポート
                        current = file_path.parent
                        for _ in range(node.level - 1):
                            current = current.parent
                        if node.module:
                            import_path = current / Path(node.module.replace(".", "/"))
                        else:
                            import_path = current
                    else:  # 絶対インポート
                        import_path = Path(
                            node.module.replace(".", "/") if node.module else ""
                        )
                else:
                    # import文の場合
                    for name in node.names:
                        import_path = Path(name.name.split(".")[0])

                # モジュールの解決を試みる
                if isinstance(import_path, Path):
                    # まず相対パスで解決を試みる
                    resolved_path = self.resolve_relative_path(
                        str(import_path), file_path, allow_init=True
                    )

                    # 相対パスで見つからない場合は検索パスから探す
                    if not resolved_path:
                        resolved_path = search_in_path(
                            str(import_path),
                            self.search_paths,
                            self.file_extensions,
                            allow_init=True,
                        )

                    if resolved_path:
                        normalized_path = self.normalize_path(resolved_path)
                        imports.add(normalized_path)

        return imports
