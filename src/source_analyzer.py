from pathlib import Path
from typing import Dict, List, Set

from .analyzers.typescript import TypeScriptAnalyzer
from .analyzers.python import PythonAnalyzer
from .analyzers.ruby import RubyAnalyzer
from .analyzers.rust import RustAnalyzer


class SourceAnalyzer:
    """メインのソースコード解析クラス"""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.src_dir = (
            self.base_dir / "src" if (self.base_dir / "src").exists() else self.base_dir
        )
        self.dependencies: Dict[str, Set[str]] = {}

        # 各言語のアナライザーを初期化
        self.analyzers = [
            TypeScriptAnalyzer(self.base_dir),
            PythonAnalyzer(self.base_dir),
            RubyAnalyzer(self.base_dir),
            RustAnalyzer(self.base_dir),
        ]

    def normalize_path(self, path: Path) -> str:
        """パスを正規化してbase_dirからの相対パスとして返す"""
        try:
            return str(path.relative_to(self.base_dir))
        except ValueError:
            return str(path)

    def analyze_file(self, file_path: Path) -> None:
        """ファイルを解析する"""
        if not file_path.is_file():
            return

        normalized_path = self.normalize_path(file_path)
        self.dependencies[normalized_path] = set()

        # ファイルの内容を読み込む
        content = file_path.read_text(encoding="utf-8")

        # 適切なアナライザーを見つけて解析を実行
        for analyzer in self.analyzers:
            if analyzer.supports_file(file_path):
                imports = analyzer.analyze_imports(content, file_path)
                self.dependencies[normalized_path].update(imports)
                break

    def analyze_single_file(self, file_path: Path) -> Dict[str, List[str]]:
        """単一のファイルを解析する

        Args:
            file_path (Path): 解析対象のファイルパス

        Returns:
            Dict[str, List[str]]: ファイルの依存関係
        """
        self.analyze_file(file_path)
        return {k: list(v) for k, v in self.dependencies.items()}

    def analyze_directory(self) -> Dict[str, List[str]]:
        """ディレクトリ全体を解析する

        Returns:
            Dict[str, List[str]]: ディレクトリ内のファイルの依存関係
        """
        # すべてのアナライザーの対象拡張子を収集
        all_extensions = []
        for analyzer in self.analyzers:
            all_extensions.extend(analyzer.file_extensions)

        # ファイルを収集（srcディレクトリが存在する場合はそこから、存在しない場合はbase_dirから）
        target_files = []
        for ext in all_extensions:
            target_files.extend(self.src_dir.rglob(f"*{ext}"))

        # ファイルを解析
        for file_path in target_files:
            self.analyze_file(file_path)

        # 結果をlist型に変換
        return {k: list(v) for k, v in self.dependencies.items()}
