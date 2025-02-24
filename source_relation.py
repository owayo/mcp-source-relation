import json
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from src.source_analyzer import SourceAnalyzer

# Initialize MCP server
mcp = FastMCP("source-relation")


@mcp.prompt()
def source_relation(path: str) -> str:
    """Return a prompt"""
    path_obj = Path(path)
    analyzer = SourceAnalyzer(str(path_obj.parent if path_obj.is_file() else path_obj))

    # Analyze source code
    if path_obj.is_file():
        dependencies = analyzer.analyze_single_file(path_obj)
    else:
        dependencies = analyzer.analyze_directory()

    # Summarize results
    result = {"dependencies": dependencies}

    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def get_source_relation(path: str) -> str:
    """
    Analyze dependencies between source files
    """
    path_obj = Path(path)
    analyzer = SourceAnalyzer(str(path_obj.parent if path_obj.is_file() else path_obj))

    # Analyze source code
    if path_obj.is_file():
        dependencies = analyzer.analyze_single_file(path_obj)
    else:
        dependencies = analyzer.analyze_directory()

    # Summarize results
    result = {"dependencies": dependencies}

    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        mcp.run(transport="stdio")
    elif args[0] == "test" and len(args) == 2:
        print(get_source_relation(args[1]))
    else:
        print("""Usage:
1. Run as MCP server:
   uv run source_relation.py

2. Run as command line tool:
   uv run source_relation.py test /path/to/project or
   uv run source_relation.py test /path/to/file
""")
