import json
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from src.source_analyzer import SourceAnalyzer

# MCPサーバーの初期化
mcp = FastMCP("source-relation")


@mcp.prompt()
def source_relation(path: str) -> str:
    """プロンプトを返す"""
    path_obj = Path(path)
    analyzer = SourceAnalyzer(str(path_obj.parent if path_obj.is_file() else path_obj))

    # ソースコードの解析
    if path_obj.is_file():
        dependencies = analyzer.analyze_single_file(path_obj)
    else:
        dependencies = analyzer.analyze_directory()

    # 結果をまとめる
    result = {"dependencies": dependencies}

    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def get_source_relation(path: str) -> str:
    """ソース間の依存関係を解析する

    Args:
        path (str): 解析対象のファイルまたはディレクトリのパス

    Returns:
        str: 依存関係を表すJSON文字列
    """
    path_obj = Path(path)
    analyzer = SourceAnalyzer(str(path_obj.parent if path_obj.is_file() else path_obj))

    # ソースコードの解析
    if path_obj.is_file():
        dependencies = analyzer.analyze_single_file(path_obj)
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
