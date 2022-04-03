from pathlib import Path
from re import findall

from beartype import beartype
from loguru import logger

from rename_books.errors import Skip


@beartype
def change_name(path: Path, name: str, /) -> Path:
    new_path = path.with_name(name)
    suffix = "".join([new_path.suffix, path.suffix])
    return new_path.with_suffix(suffix)


@beartype
def change_suffix(path: Path, /, *suffixes: str) -> Path:
    return path.with_suffix("".join(suffixes))


@beartype
def get_dropbox_path() -> Path:
    return next(
        path
        for path in [
            Path("/data/derek/Dropbox"),
            Path("/mnt/c/Users/Derek/Dropbox"),
        ]
        if path.exists()
    )


@beartype
def get_input(
    question: str,
    *,
    extra_choices: dict[str, str] | None = None,
    pattern: str | None = None,
) -> str:
    choices = {"s": "skip"}
    if extra_choices is not None:
        choices.update(extra_choices)
    choices_str = ", ".join(f"{k}:{v}" for k, v in choices.items())
    prompt = f"{question} ({choices_str}): "
    while True:
        if (response := input(prompt)) == "s":
            raise Skip()
        else:
            if pattern is None:
                return response.strip()
            else:
                try:
                    (match,) = findall(pattern, response)
                except ValueError:
                    logger.error("{!r} is an invalid value", response)
                else:
                    return match


@beartype
def get_list_of_inputs(
    question: str, *, name_if_empty_error: str | None = None
) -> list[str]:
    out: list[str] = []
    while True:
        enum_question = f"{question} (#{len(out)+1})"
        response = get_input(enum_question, extra_choices={"Enter": "finish"})
        if response:
            out.append(response)
        else:
            if out:
                return out
            else:
                if name_if_empty_error is None:
                    return out
                else:
                    logger.error(
                        "{!r} is not allowed to be empty", name_if_empty_error
                    )


def get_temporary_path() -> Path:
    return get_dropbox_path().joinpath("Temporary")
