from __future__ import annotations

from pathlib import Path
from re import findall

from loguru import logger

from rename_books.errors import Skip


def change_name(path: Path, name: str) -> Path:
    new_path = path.with_name(name)
    suffix = "".join([new_path.suffix, path.suffix])
    return new_path.with_suffix(suffix)


def change_suffix(path: Path, *suffixes: str) -> Path:
    return path.with_suffix("".join(suffixes))


def get_input(
    question: str,
    *,
    extra_choices: dict[str, str] | None = None,
    pattern: str = None,
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
                    logger.error(f"{response!r} is an invalid value")
                else:
                    return match


def get_list_of_inputs(
    question: str, *, name_if_empty_error: str | None = None
) -> list[str]:
    out = []
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
                        f"{name_if_empty_error!r} is not allowed to be empty"
                    )
