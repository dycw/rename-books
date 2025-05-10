from __future__ import annotations

from itertools import chain
from logging import getLogger

from click import command
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator
from tqdm import tqdm
from utilities.logging import basic_config
from utilities.random import shuffle
from utilities.text import ParseBoolError, parse_bool

from rename_books.classes import MetaData
from rename_books.constants import BOOKS

_LOGGER = getLogger(__name__)


@command()
def main() -> None:
    basic_config()
    paths = shuffle(list(chain(BOOKS.rglob("**/*.pdf"), BOOKS.rglob("**/*.epub"))))
    paths = [p for p in paths if not MetaData.is_normalized(p)]
    for path in tqdm(paths, ncols=100):
        if not MetaData.is_normalized(path):
            normalized = MetaData.normalize(path)
            result = prompt(
                f"""
>> {str(path)!r}
is not normalized; would from become
>> {str(normalized)!r}
Rename? """,
                completer=WordCompleter(["yes", "no"]),
                default="yes",
                mouse_support=True,
                validator=_validator,
                vi_mode=True,
            ).strip()
            if parse_bool(result):
                _ = path.rename(normalized)
            else:
                _LOGGER.info("Skipping %r...", str(path))


def _validator_core(text: str, /) -> bool:
    try:
        _ = parse_bool(text)
    except ParseBoolError:
        return False
    return True


_validator = Validator.from_callable(_validator_core)


if __name__ == "__main__":
    main()
