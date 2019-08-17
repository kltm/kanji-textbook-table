# textbook-project-data

Simple software to convert three simple TSV formats for vocabulry and
kanji information into publishable tables.

The first piece of software (parse.py) produces a parsed JSON version
that can be fed into other programs for further processing.

## The TSV data format for kanji lists

The first line of the format is the column names for the twelve (12) columns:

```tsv
Level	Chapter	W/R	Kanji	Hiragana	Introduced	New Kanji	New Reading	Meaning	Section	L. #W/R	Notes
```

After this initial line, all further lines are data, with the columns
as described below. Completely blank lines and lines where all fields
are blank can be skipped.

## The TSV data format for kanji details

The first line of the format is the column names for the fourteen (14) columns:

```tsv
Level	Chapter	W/R	Kanji	Reading	Highlighted Reading	Meaning	Radical	Radical  Meaning	Radical Example	Radical Example Notes	Example Word	Highlighted Example Word	Stroke Order
```

After this initial line, all further lines are data, with the columns
as described below. Completely blank lines and lines where all fields
are blank can be skipped.

## The TSV data format for vocabulary lists

The first line of the format is the column names for the ten (10) columns:

```tsv
Level	Chapter	Japanese	Ruby	Reading	Meaning	Section	Extra	Grammar Point	Notes
```

After this initial line, all further lines are data, with the columns
as described below. Completely blank lines and lines where all fields
are blank can be skipped.

There is a special relationship between "Japanese" and "Ruby". The
listed ruby is an in-order description of what kanji need to be hinted
for reading in the "Japanese" column. This program will err if there
is anything wrong with that map.

### Level

This column is required. It is an integer.

### Chapter

This column is required. It is an integer.

### Japanese

This column is required. It is a string.

### Ruby

This column is optional. It is a comma-separated string of
pipe-separated items. Each of these pipe-separated items is a kanji
set on the left side and the reading in hiragana of the kanji set on
the right side. These kanji sets should map in order onto the
"Japanese" in the previous column.

### Reading

This column is required. It is a string.

### Meaning

This column is required. It is a string.

### Section

This column is empty or structured strings. If it is empty, it
indicates a headerless introduction section that comes before other
things; otherwise, it should be of the format: \[会読\]\[\\w\].

### Extra

This column is optional. It is either empty or contains a "*".

### Grammar Point

This column is optional. It is a string.

### Notes

This column is optional. It is a string.

## TSV example:

An example of the format is:

```tsv
Level	Chapter	Japanese	Ruby	Reading	Meaning	Section	Extra	Grammar Point	Notes
6	1	土井善晴	土井善晴|どいよしはる	どいよしはる	Yoshiharu Doi, a well-known Japanese chef (son of Masaru Doi)	読１	*
6	1	やはり		やはり	formal form of やっぱり	読１
6	1	雑煮	雑煮|ぞうに	ぞうに	mochi soup eaten during the new year celebration	読１
```

## How to run the code

The code is written in Python 3.6.8, developed on Ubuntu 18.04.3 LTS,
using very basic libraries.

Example usage:

```bash
python3 format.py --template ./word-html-frame.template.html  --output /tmp/chapter --tsv ~/tmp/kanji-list.tsv
```

Will write the output to /tmp in the form of "chapter-1.html", ...,
"chapter-8.html", etc.
