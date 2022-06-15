# rename-books

Script to rename e-books

## Demo

[![asciicast](https://asciinema.org/a/EoeE4tjjEmGtrxFD0OWhkyW4E.svg)](https://asciinema.org/a/EoeE4tjjEmGtrxFD0OWhkyW4E)

## Requirements

- [x] Given a Path, check it exists & is a directory

- [ ] Iterate through and collection paths which are PDFs with name of the form:

  - `(1951) The Catcher in the Rye 2nd Edition (J. D. Salinger).pdf`

- [ ] For each item, allow the user to populate a structure of the form:

  ```rust
  {
    year: u32,
    title: String,
    subtitles: [String],
    authors: [String],
  }
  ```

  This is to be interactive.

  1. Prompt 1 - year. Pre-populated, press Enter to continue.

     ```
     Input year: 1951
     ```

  1. Prompt 2 - title. Pre-populated with sentence case (1st word title, rest
     lower). Here the title consists of all words except the last 2.

     ```
     Input title: The catcher in the rye 2nd edition
     ```

     into:

     ```
     Input title: The Catcher in the Rye
     ```

  1. Prompt 3 - subtitles. Pre-populated with the 2 unused last words of the
     previous section. Exactly what we need. Press Enter once to maybe input a
     2nd (or more) subtitle. Press Enter with no input to finish.

     ```
     Input subtitle(s): 2nd Edition
     Input subtitle(s):
     ```

  1. Prompt 4 - authors. Pre-populated with the surnames only. Again, press
     Enter with no input to finish:

     ```
     Input author(s): Salinger
     Input author(s):
     ```

  1. Prompt 5:

     ```
     Please confirm the data:

     ---------  ----------------------
     year       1951
     title      The Catcher in the Rye
     subtitles  ['2nd Edition']
     authors    ['Salinger']
     ---------  ----------------------
     ```

     Press Enter to accept, else press "y", "t", "s" or "a" to go back to
     re-enter/edit any of the existing fields. For example, if the title was
     incorrectly entered as "The Catcher in the R", then the prompt should be
     pre-populated with this string.

- [ ] Once done, rename the file to:

  ```
  1951 — The catcher in the Rye – 2nd Edition (Salinger).pdf
  ```

- [ ] Repeat through the collection.
