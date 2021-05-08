from pathlib import Path

from rename_books.rename_books import main


DIRECTORY = Path("/data/derek/Dropbox/Temporary/")


def main_vsi() -> None:
    main(subtitles=["A very short introduction"])


if __name__ == "__main__":
    main_vsi()
