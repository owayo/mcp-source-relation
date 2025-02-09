from abc import ABC, abstractmethod
from pathlib import Path
from typing import Set

from ..utils.path import normalize_path, resolve_relative_path


class BaseAnalyzer(ABC):
    """基本アナライザークラス"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """対応するファイル拡張子のリスト"""
        pass

    @abstractmethod
    def analyze_imports(self, content: str, file_path: Path) -> Set[str]:
        """ファイルのインポート文を解析する

        Args:
            content: ファイルの内容
            file_path: ファイルパス

        Returns:
            インポートされているファイルのパスのセット
        """
        pass

    def supports_file(self, file_path: Path) -> bool:
        """このアナライザーがファイルをサポートしているかどうかを判定する"""
        return file_path.suffix in self.file_extensions

    def normalize_path(self, path: Path) -> str:
        """パスを正規化する"""
        return normalize_path(path, self.base_dir)

    def resolve_relative_path(
        self,
        import_path: str,
        current_file: Path,
        allow_index: bool = True,
        allow_mod: bool = False,
    ) -> Path | None:
        """相対パスを解決する"""
        return resolve_relative_path(
            import_path,
            current_file,
            self.file_extensions,
            allow_index,
            allow_mod,
        )
