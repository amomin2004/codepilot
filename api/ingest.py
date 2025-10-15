from pathlib import Path
import os


"""
Args:
    root: absolute/relative path to the repo folder
    include_exts: list of extensions to include, e.g. [".py", ".ts", ".js"]
    exclude_dirs: list of directories to exclude, e.g. ["node_modules", "dist"]
    
Returns:
    List of relative file paths from root, sorted for determinism
"""

def list_source_files(root: str | Path, include_exts: list[str], exclude_dirs: list[str]) -> list[str]:
    absolutePath = Path(root).resolve()
    if not absolutePath.is_dir():
        raise ValueError(f"Root path is not a directory: {absolutePath}")

    exclude_dirs = set(exclude_dirs)
    include_exts = set((e if e.startswith(".") else f".{e}").lower() for e in include_exts)

    collected_files = []

    for dirpath, dirnames, filenames in os.walk(absolutePath):
        dirnames[:] = [
            d for d in dirnames
            if d not in exclude_dirs and not (Path(dirpath) / d).is_symlink()
        ]

        for file in filenames:

            full_path = Path(dirpath) / file

            if full_path.is_symlink():
                continue

            if full_path.suffix.lower() not in include_exts:
                continue

            if (".min." in file or file in {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock"}):
                continue

            try:
                relative_path = full_path.relative_to(absolutePath)
            except ValueError:
                continue

            collected_files.append(relative_path.as_posix())

    return sorted(set(collected_files))