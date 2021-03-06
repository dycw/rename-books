from pathlib import Path


def change_name(path: Path, name: str) -> Path:
    new_path = path.with_name(name)
    suffix = "".join([new_path.suffix, path.suffix])
    return new_path.with_suffix(suffix)


def change_suffix(path: Path, *suffixes: str) -> Path:
    return path.with_suffix("".join(suffixes))
