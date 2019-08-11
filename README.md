# kanji-textbook-table

Simple software to convert a set of simple TSV formats for kanji
information into publishable tables.


## The TSV data format for "lists"

The first line of the format is the column names for the ten (10) columns:

```tsv
Level	Chapter	Japanese	Ruby	Reading	Meaning	Section	Extra	Grammar Point	Notes
```

After this initial line, all further lines are data, with the columns as described below.

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

This column is optional. It is a string.

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
python3 format.py --tsv ~/tmp/kanji-list.tsv --template ./word-html-frame.template.html --output /tmp/out.html
```
