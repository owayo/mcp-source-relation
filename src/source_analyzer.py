from pathlib import Path
from typing import Dict, List, Set

from .analyzers.python import PythonAnalyzer
from .analyzers.ruby import RubyAnalyzer
from .analyzers.rust import RustAnalyzer
from .analyzers.typescript import TypeScriptAnalyzer


class SourceAnalyzer:
    """メインのソースコード解析クラス"""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.src_dir = (
            self.base_dir / "src" if (self.base_dir / "src").exists() else self.base_dir
        )
        self.dependencies: Dict[str, Set[str]] = {}
        self._analyzed_files: Set[str] = set()

        # 各言語のアナライザーを初期化
        self.analyzers = [
            TypeScriptAnalyzer(self.base_dir),
            PythonAnalyzer(self.base_dir),
            RubyAnalyzer(self.base_dir),
            RustAnalyzer(self.base_dir),
        ]

    def normalize_path(self, path: Path) -> str:
        """パスを正規化して絶対パスとして返す

        Args:
            path (Path): 正規化対象のパス

        Returns:
            str: 正規化された絶対パス
        """
        try:
            return str(path.absolute())
        except ValueError:
            return str(path)

    def analyze_file(self, file_path: Path) -> None:
        """ファイルを解析する

        Args:
            file_path (Path): 解析対象のファイルパス
        """
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

    def get_recursive_dependencies(self, file_path: str) -> List[str]:
        """指定されたファイルの再帰的な依存関係を取得する

        Args:
            file_path (str): 分析対象のファイルパス

        Returns:
            List[str]: 再帰的に解決された依存関係のリスト
        """
        self._analyzed_files.clear()
        return self._analyze_dependencies(file_path)

    def _analyze_dependencies(self, file_path: str) -> List[str]:
        """再帰的に依存関係を分析する内部メソッド

        Args:
            file_path (str): 分析対象のファイルパス

        Returns:
            List[str]: 依存関係のリスト
        """
        if file_path in self._analyzed_files:
            return []

        self._analyzed_files.add(file_path)
        all_dependencies = []

        direct_dependencies = list(self.dependencies.get(file_path, set()))
        for dependency in direct_dependencies:
            if dependency not in all_dependencies:
                all_dependencies.append(dependency)
                # 依存先の依存関係を再帰的に取得
                nested_dependencies = self._analyze_dependencies(dependency)
                for nested_dep in nested_dependencies:
                    if nested_dep not in all_dependencies:
                        all_dependencies.append(nested_dep)

        return all_dependencies

    def analyze_single_file(self, file_path: Path) -> Dict[str, List[str]]:
        """単一のファイルを解析する

        Args:
            file_path (Path): 解析対象のファイルパス

        Returns:
            Dict[str, List[str]]: ファイルの完全な依存関係（直接および間接的な依存関係を含む）
        """
        self.analyze_file(file_path)
        normalized_path = self.normalize_path(file_path)
        return {normalized_path: self.get_recursive_dependencies(normalized_path)}

    def analyze_directory(self) -> Dict[str, List[str]]:
        """ディレクトリ全体を解析する

        Returns:
            Dict[str, List[str]]: ディレクトリ内のファイルの完全な依存関係
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

        # 各ファイルの再帰的な依存関係を取得
        complete_dependencies = {}
        for file_path in self.dependencies.keys():
            complete_dependencies[file_path] = self.get_recursive_dependencies(
                file_path
            )

        return complete_dependencies
