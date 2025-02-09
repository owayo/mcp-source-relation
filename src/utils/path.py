from pathlib import Path
from typing import Optional, List


def normalize_path(path: Path, base_dir: Path) -> str:
    """パスを正規化してbase_dirからの相対パスとして返す"""
    try:
        return str(path.relative_to(base_dir))
    except ValueError:
        return str(path)


def resolve_relative_path(
    import_path: str,
    current_file: Path,
    possible_exts: List[str],
    allow_index: bool = True,
    allow_mod: bool = False,
    allow_init: bool = False,
) -> Optional[Path]:
    """相対パスを解決する

    Args:
        import_path: 解決するインポートパス
        current_file: 現在のファイルパス
        possible_exts: 可能な拡張子のリスト
        allow_index: index.{ext}ファイルを許可するか
        allow_mod: Rustのmod.rsファイルを許可するか
        allow_init: Python の __init__.py を許可するか

    Returns:
        解決されたファイルパス、見つからない場合はNone
    """
    # 拡張子付きの場合は直接チェック
    absolute_path = (current_file.parent / import_path).resolve()
    if absolute_path.exists():
        return absolute_path

    # ベースパスを計算（拡張子なしの場合）
    base_path = absolute_path.parent / absolute_path.stem

    # 以下の順序で検索:
    # 1. 拡張子を補完
    for ext in possible_exts:
        test_path = base_path.with_suffix(ext)
        if test_path.exists():
            return test_path

    # 2. ディレクトリ内のindex/mod/initファイル
    if base_path.is_dir():
        # TypeScript/JavaScriptのindex
        if allow_index:
            for ext in possible_exts:
                index_path = base_path / f"index{ext}"
                if index_path.exists():
                    return index_path

        # Rustのmod.rs
        if allow_mod:
            mod_path = base_path / "mod.rs"
            if mod_path.exists():
                return mod_path

        # Pythonの__init__.py
        if allow_init:
            init_path = base_path / "__init__.py"
            if init_path.exists():
                return init_path

    return None


def search_in_path(
    import_name: str,
    search_paths: List[Path],
    possible_exts: List[str],
    allow_index: bool = True,
    allow_mod: bool = False,
    allow_init: bool = False,
) -> Optional[Path]:
    """検索パスから指定されたインポートを探す

    Args:
        import_name: インポート名
        search_paths: 検索パスのリスト
        possible_exts: 可能な拡張子のリスト
        allow_index: index.{ext}ファイルを許可するか
        allow_mod: Rustのmod.rsファイルを許可するか
        allow_init: Python の __init__.py を許可するか

    Returns:
        見つかったファイルのパス、見つからない場合はNone
    """
    for search_path in search_paths:
        test_path = search_path / import_name
        resolved = resolve_relative_path(
            str(test_path),
            search_path,
            possible_exts,
            allow_index,
            allow_mod,
            allow_init,
        )
        if resolved:
            return resolved
    return None
