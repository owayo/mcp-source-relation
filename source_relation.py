import json
import sys
from pathlib import Path
from typing import Dict, List, Set

from mcp.server.fastmcp import FastMCP

from src.source_analyzer import SourceAnalyzer

# Initialize MCP server
mcp = FastMCP("source-relation")


def analyze_dependencies_recursively(
    analyzer: SourceAnalyzer, file_path: str, analyzed_files: Set[str]
) -> Dict[str, List[str]]:
    """ファイルの依存関係を再帰的に解析する

    Args:
        analyzer (SourceAnalyzer): 解析を行うアナライザーインスタンス
        file_path (str): 解析対象のファイルパス
        analyzed_files (Set[str]): 解析済みファイルのセット

    Returns:
        Dict[str, List[str]]: 解析されたすべての依存関係の辞書
    """
    if file_path in analyzed_files:
        return {}

    analyzed_files.add(file_path)
    dependencies: Dict[str, List[str]] = {}

    # ファイルを解析
    try:
        current_deps = analyzer.analyze_single_file(Path(file_path))
        direct_dependencies = current_deps.get(file_path, [])
        dependencies[file_path] = direct_dependencies

        # 各依存ファイルについても再帰的に解析
        for dependency in direct_dependencies:
            if dependency not in analyzed_files:
                nested_deps = analyze_dependencies_recursively(
                    analyzer, dependency, analyzed_files
                )
                dependencies.update(nested_deps)
    except Exception:
        pass

    return dependencies


@mcp.prompt()
def source_relation(path: str) -> str:
    """Return a prompt"""
    path_obj = Path(path)
    base_dir = str(path_obj.parent if path_obj.is_file() else path_obj)
    analyzer = SourceAnalyzer(base_dir)

    # ソースコードを解析
    if path_obj.is_file():
        analyzed_files: Set[str] = set()
        file_path = str(path_obj.absolute())
        dependencies = analyze_dependencies_recursively(
            analyzer, file_path, analyzed_files
        )
    else:
        dependencies = analyzer.analyze_directory()

    # 結果をまとめる
    result = {"dependencies": dependencies}

    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def get_source_relation(path: str) -> str:
    """Analyze dependencies between source files"""
    path_obj = Path(path)
    base_dir = str(path_obj.parent if path_obj.is_file() else path_obj)
    analyzer = SourceAnalyzer(base_dir)

    # ソースコードを解析
    if path_obj.is_file():
        analyzed_files: Set[str] = set()
        file_path = str(path_obj.absolute())
        dependencies = analyze_dependencies_recursively(
            analyzer, file_path, analyzed_files
        )
    else:
        dependencies = analyzer.analyze_directory()

    # 結果をまとめる
    result = {"dependencies": dependencies}

    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        mcp.run(transport="stdio")
    elif args[0] == "test" and len(args) == 2:
        print(get_source_relation(args[1]))
    else:
        print("""使用方法:
1. MCPサーバーとして実行:
   uv run source_relation.py

2. コマンドラインツールとして実行:
   uv run source_relation.py test /path/to/project または
   uv run source_relation.py test /path/to/file
""")
