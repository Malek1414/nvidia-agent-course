# Provided by the course task, unchanged.
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath, PureWindowsPath

SEARCH_ROOT = Path(__file__).resolve().parents[1] / "sample_workspace"

def search_files(
    name_pattern: str,
    subpath: str = ".",
    max_results: int = 20,
) -> list[str]:
    """Return files whose names match a glob pattern."""

    if not isinstance(name_pattern, str) or not name_pattern.strip():
        raise ValueError("name_pattern must be a non-empty string")
    if not isinstance(subpath, str) or not subpath.strip():
        raise ValueError("subpath must be a non-empty string")
    if isinstance(max_results, bool) or not isinstance(max_results, int):
        raise ValueError("max_results must be an integer")
    if not 1 <= max_results <= 100:
        raise ValueError("max_results must be between 1 and 100")

    relative = PurePosixPath(subpath.replace("\\", "/"))
    if (
        relative.is_absolute()
        or PureWindowsPath(subpath).is_absolute()
        or ".." in relative.parts
    ):
        raise ValueError("subpath must stay inside the sample workspace")

    base = SEARCH_ROOT.resolve()
    folder = base.joinpath(*relative.parts).resolve()
    try:
        folder.relative_to(base)
    except ValueError as error:
        raise ValueError("subpath must stay inside the sample workspace") from error
    if not folder.is_dir():
        raise ValueError(f"subpath is not a directory: {subpath}")

    pattern = name_pattern.casefold()
    matches = [
        path.relative_to(base).as_posix()
        for path in folder.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and fnmatchcase(path.name.casefold(), pattern)
    ]
    return sorted(matches, key=str.casefold)[:max_results]
