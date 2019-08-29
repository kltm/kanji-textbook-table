####
#### Convert a TSV into a fully parsed JSON list blob that could be
#### used by a mustache (or other logicless) template.
####
#### Example usage to analyze the usual suspects:
####  python3 parse-kanji-details.py --help
####
#### Get report of current problems:
####  python3 parse-kanji-details.py --tsv ~/Downloads/UCSC中上級教科書_漢字・単語リスト\ -\ 漢字表\(1\).tsv --output /tmp/parsed-kanji-details.json
####
#### As part of a pipeline:
####  python3 parse-kanji-details.py --tsv ~/Downloads/UCSC中上級教科書_漢字・単語リスト\ -\ 漢字表\(8\).tsv --output /tmp/parsed-kanji-details.json && python3 chapter-bin.py --input /tmp/parsed-kanji-details.json --pattern kanji-details --output /tmp/binned-kanji.json && python3 apply-to-chapters.py --input /tmp/binned-kanji.json --template manual-html-kanji-details.template.html --output /tmp/kh-ch
####
#### As part of a pipeline, with repo specified:
####  python3 parse-kanji-details.py --tsv ~/Downloads/UCSC中上級教科書_漢字・単語リスト\ -\ 漢字表\(8\).tsv --repo /home/sjcarbon/local/src/git/textbook-project-data --output /tmp/parsed-kanji-details.json && python3 chapter-bin.py --input /tmp/parsed-kanji-details.json --pattern kanji-details --output /tmp/binned-kanji.json && python3 apply-to-chapters.py --input /tmp/binned-kanji.json --template manual-html-kanji-details.template.html --output /tmp/kh-ch
####

import sys
import argparse
import logging
import csv
import pystache
import json
import functools
import os
import glob

## Logger basic setup.
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('parse-kanji-details')
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
    parser.add_argument('-r', '--repo',
                        help='[optional] The path to this repo')
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

    if not args.repo:
        args.repo = os.getcwd()
    LOGGER.info('Will output to: ' + args.output)

    if not args.output:
        die_screaming('need an output file argument')
    LOGGER.info('Will output to: ' + args.output)

    ## Setup some general metadata checking for the different formats.
    required_total_columns = 14
    required_columns = ["level", "chapter", "read-write", "kanji-raw", "reading-raw", "meaning-raw", "radical-raw", "radical-example-raw", "example-word-raw", "example-word-highlighted-raw"]

    ##
    kanjialive_lookup = {}
    with open(args.repo + '/kanjialive/ka_data.csv', 'r') as ka_in:
        ka_in = csv.reader(ka_in, delimiter=',')

        for line in ka_in:
            kanjialive_lookup[line[0]] = line[1]

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
                    data_object["kanji-raw"] = str(line[3]) # req
                    data_object["reading-raw"] = str(line[4]) # req
                    data_object["reading-highlighted-raw"] = line[5] if (type(line[5]) is str and len(line[5]) > 0) else None # opt
                    data_object["meaning-raw"] = line[6] # req
                    data_object["radical-raw"] = line[7] # req
                    data_object["radical-meaning-raw"] = line[8] if (type(line[8]) is str and len(line[8]) > 0) else None # opt
                    data_object["radical-example-raw"] = line[9] # req
                    data_object["radical-example-notes"] = line[10] if (type(line[10]) is str and len(line[10]) > 0) else None # opt
                    data_object["example-word-raw"] = line[11] # req
                    data_object["example-word-highlighted-raw"] = line[12] # req
                    data_object["stroke-order"] = line[13] if (type(line[13]) is str and len(line[13]) > 0) else None # opt

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

                    ## Break down the reading field csvs to get
                    ## highlighting, etc.
                    if data_object["reading-highlighted-raw"]:
                        reading_hi_list = [ x.strip() for x in data_object["reading-highlighted-raw"].split(",")]
                    else:
                        reading_hi_list = []
                    data_object["reading-highlighted-list"] = reading_hi_list
                    reading_list = [ x.strip() for x in data_object["reading-raw"].split(",")]
                    reading_enriched = []
                    for reading_item in reading_list:
                        if reading_item in reading_hi_list:
                            reading_enriched.append({"highlighted-p": True,
                                                     "reading": reading_item})
                        else:
                            reading_enriched.append({"highlighted-p": False,
                                                     "reading": reading_item})
                    data_object["reading-list-enriched"] = reading_enriched


                    ## Break down the meaning field
                    meaning_list = [ {"reading": x.strip()} for x in data_object["meaning-raw"].split("+") ]
                    data_object["meaning-list"] = meaning_list

                    ## Break down the somewhat complicated example
                    ## fields.
                    exwrd_enriched = []
                    ## highlighted-example-word hightlight list to use
                    ## as key to identify for highlighting.
                    exwrd_hi_list = "^".join([ x.strip() for x in data_object["example-word-highlighted-raw"].split("+")])
                    data_object["example-word-highlighted-list"] = exwrd_hi_list
                    ## example-word
                    exwrd_pre_list = [ x.strip() for x in data_object["example-word-raw"].split("|") ]
                    for exwrd_pre in exwrd_pre_list:
                        ex_triple = [ x.strip() for x in exwrd_pre.split("+") ]
                        if not len(ex_triple) == 3:
                            die_screaming('ERROR: malformed example word with "'+exwrd_pre+'" at '+ str(i) +': '+ '\t'.join(line))
                        else:
                            exwrd_enriched.append({"japanese":
                                                   {"word": ex_triple[0],
                                                    "highlighted-p": False if "^".join(ex_triple) not in exwrd_hi_list else True},
                                                   "hiragana":
                                                   {"word": ex_triple[1],
                                                    "highlighted-p": False if "^".join(ex_triple) not in exwrd_hi_list else True},
                                                   "english":
                                                   {"word": ex_triple[2],
                                                    "highlighted-p": False if "^".join(ex_triple) not in exwrd_hi_list else True}})
                    data_object["example-word-list-enriched"] = exwrd_enriched

                    ## Radicals.
                    radical_list = [ {"character": x.strip()} for x in data_object["radical-raw"].split(",") ]
                    data_object["radical-list"] = radical_list
                    radical_meaning_list = [] if not data_object["radical-meaning-raw"] else [ {"meaning": x.strip()} for x in data_object["radical-meaning-raw"].split(",") ]
                    data_object["radical-meaning-list"] = radical_meaning_list
                    radical_example_list = [ {"kanji": x.strip()} for x in data_object["radical-example-raw"].split(",") ]
                    data_object["radical-example-list"] = radical_example_list

                    ## Manipulate our objects to make sure that we
                    ## have the correct mapping in place.
                    manual_list = ['井', '阪', '俺', '扱', '酔']
                    kanjialive_lookup['井'] = 'shou(i)'
                    kanjialive_lookup['阪'] = 'han(saka)'
                    kanjialive_lookup['俺'] = 'en(ore)'
                    kanjialive_lookup['扱'] = 'sou(atsukau)'
                    kanjialive_lookup['酔'] = 'sui(yo)'

                    ## Okay, let's experiment with image output.
                    ## TODO: Check that our directory is in place.

                    if not data_object["kanji-raw"] in kanjialive_lookup and not data_object["kanji-raw"] in manual_list:
                        die_screaming("Unknown kanji: "+data_object["kanji-raw"])
                    else:
                        file_stem = kanjialive_lookup[data_object["kanji-raw"]]
                        files = glob.glob(args.repo + '/kanjialive/kanji_strokes/' + file_stem + '_*')
                        data_object["kanji-strokes-list-manual"] = []
                        data_object["kanji-strokes-list"] = []
                        data_object["kanji-strokes-base"] = args.repo + '/kanjialive/kanji_strokes/'
                        for i, file in enumerate(files):
                            if data_object["kanji-raw"] in manual_list:
                                data_object["kanji-strokes-list-manual"].append(file_stem + '_' + str(i+1) + '.png')
                            else:
                                data_object["kanji-strokes-list"].append(file_stem + '_' + str(i+1) + '.svg')

                    ## Onto the pile.
                    data_list.append(data_object)

    ## Dump to given file.
    #LOGGER.info(json.dumps(data_list, indent = 4))
    with open(args.output, 'w') as output:
            output.write(json.dumps(data_list, indent = 4))

## You saw it coming...
if __name__ == '__main__':
    main()
