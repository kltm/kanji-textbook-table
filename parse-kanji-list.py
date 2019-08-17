####
#### Convert a TSV into a fully parsed JSON list blob that could be
#### used by a mustache (or other logicless) template.
####
#### Example usage to analyze the usual suspects:
####  python3 parse.py --help
####
#### Get report of current problems:
####  python3 parse-kanji-list.py --tsv ~/Downloads/UCSC中上級教科書_漢字・単語リスト\ -\ 漢字リス ト.tsv --output /tmp/parsed-kanji-list.json
####
#### As part of a pipeline:
####  python3 parse-kanji-list.py --tsv ~/Downloads/UCSC中上級教科書_漢字リスト\ -\ 漢字リス ト\(4\).tsv --output /tmp/parsed-kanji-list.json && python3 chapter-bin.py -v --input /tmp/parsed-vocab-list.json --output /tmp/chapters.json && python3 apply-to-chapters.py --input /tmp/chapters.json --template ./word-html-frame.template.html --output /tmp/chapter
####

import sys
import argparse
import logging
import csv
import pystache
import json
import os

## Logger basic setup.
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('parse')
LOGGER.setLevel(logging.WARNING)

def die_screaming(string):
    """ Die and take our toys home. """
    LOGGER.error(string)
    sys.exit(1)

def main():

    ## Deal with incoming.
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='More verbose output')
    parser.add_argument('-t', '--tsv',
                        help='The TSV data file to read in')
    parser.add_argument('-o', '--output',
                        help='The file to output to')
    args = parser.parse_args()

    ## Up the verbosity level if we want.
    if args.verbose:
        LOGGER.setLevel(logging.INFO)
        LOGGER.info('Verbose: on')

    ## Ensure arguments and read in what is necessary.
    if not args.tsv:
        die_screaming('need an input tsv argument')
    LOGGER.info('Will use "' + args.tsv + '" as data')

    if not args.output:
        die_screaming('need an output file argument')
    LOGGER.info('Will output to: ' + args.output)

    ## Setup some general metadata checking for the different formats.
    required_total_columns = 12
    required_columns = ["level", "chapter", "read-write", "kanji", "hiragana", "meaning"]

    ## Bring on all data in one sweep, formatting and adding
    ## appropriate parts to internal format so that we can simply
    ## output in any mustache template.
    data_list = []
    with open(args.tsv, 'r') as tsv_in:
        tsv_in = csv.reader(tsv_in, delimiter='\t')

        ## Process data.
        first_line_p = True
        last_read_write_token = None
        changed_read_write_count = 0
        i = 0
        for line in tsv_in:
            i = i + 1
            if first_line_p:
                first_line_p = False
                continue
            else:
                count = len(line)
                if len(set(line)) == 1 and line[0] == "":
                    LOGGER.info("Skipping completely empty line: " + str(i))
                    continue
                elif not count == required_total_columns:
                    die_screaming('malformed line: '+ str(i) +' '+ '\t'.join(line))
                else:

                    # LOGGER.info("-------")
                    # LOGGER.info(type(line[3]))
                    # LOGGER.info(len(line[3]))
                    # LOGGER.info(line[3])

                    ## Base parsing everything into a common object.
                    ## Additional metadata that we'll want.
                    data_object = {}
                    data_object["row"] = str(i) # inserted

                    data_object["level"] = str(line[0]) # req
                    data_object["chapter"] = str(line[1]) # req
                    data_object["read-write"] = line[2] if (type(line[2]) is str and line[2] in ["W", "R"]) else None # req
                    data_object["kanji"] = str(line[3]) # req
                    data_object["hiragana"] = str(line[4]) # req
                    data_object["introduced"] = str(line[5]) # opt
                    data_object["kanji-new"] = str(line[6]) # opt
                    data_object["reading-new"] = str(line[7]) # opt
                    data_object["meaning"] = line[8] # req
                    data_object["section"] = line[9] if (type(line[9]) is str and len(line[9]) > 0) else None # opt
                    data_object["kanji-replacement"] = str(line[10]) # opt
                    data_object["notes"] = line[11] if (type(line[11]) is str and len(line[11]) > 0) else None # opt

                    ## Basic error checking.
                    for required_entry in required_columns:
                        if not data_object[required_entry] is str and not len(data_object[required_entry]) > 0:
                            die_screaming('malformed line with "'+required_entry+'" at '+ str(i) +': '+ '\t'.join(line))

                    ## Try and get the read/write section changover
                    ## counts.
                    if not data_object["read-write"] == str(last_read_write_token):
                        changed_read_write_count = 0
                    changed_read_write_count = changed_read_write_count + 1 # inc
                    last_read_write_token = data_object["read-write"]
                    data_object["read-write-changed-count"] = changed_read_write_count

                    ## Convert the W/R into what will appear in that
                    ## case for mustache.
                    data_object["read-write-header"] = "読めなければいけない漢字"
                    if data_object["read-write"] == "W":
                        data_object["read-write-header"] = "書けなければいけない漢字"

                    ## Onto the pile.
                    data_list.append(data_object)

    ## Dump to given file.
    #LOGGER.info(json.dumps(data_list, indent = 4))
    with open(args.output, 'w') as output:
            output.write(json.dumps(data_list, indent = 4))

## You saw it coming...
if __name__ == '__main__':
    main()
