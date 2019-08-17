####
#### Pull in a JSON blob produced by parse.py and re-blob it into
#### chapters and ordered sections.
####
#### Example usage to analyze the usual suspects:
####  python3 chapter-bin.py --help
####
#### Get report of current problems and/or bin:
####  python3 chapter-bin.py --input /tmp/input.json --output /tmp/output.json
####

import sys
import argparse
import logging
import json

## Logger basic setup.
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('chapter-bin')
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
    parser.add_argument('-i', '--input',
                        help='The file to use as input')
    parser.add_argument('-o', '--output',
                        help='The file to output')
    args = parser.parse_args()

    ## Up the verbosity level if we want.
    if args.verbose:
        LOGGER.setLevel(logging.INFO)
        LOGGER.info('Verbose: on')

    ## Ensure arguments and read in what is necessary.
    if not args.input:
        die_screaming('need an input argument')
    LOGGER.info('Will input from: ' + args.input)
    if not args.output:
        die_screaming('need an output argument')
    LOGGER.info('Will output to: ' + args.output)

    ## Bring data in.
    data_list = []
    with open(args.input, 'r') as json_in_f:
        data_list = json.load(json_in_f)

    ## Sort the data into the different chapter sets.
    chapter_sets = {}
    for item in data_list:
        chapter = str(item["chapter"])
        #print(chapter)
        if not chapter in chapter_sets:
            chapter_sets[chapter] = []
        chapter_sets[chapter].append(item)
    #print(", ".join(sorted(chapter_sets.keys(), key=int)))

    ## Loop over the different chapters to create the output.
    sectioned_chapter_sets = []
    for chi in sorted(chapter_sets.keys(), key=int):
        data_list = chapter_sets[chi]

        ## Sort the chapter sets into sections sets.
        sections = {}
        for item in data_list:
            section = item["section"]
            if not section in sections:
                sections[section] = []
            sections[section].append(item)

        ## Manually add the sections in the order we want them to
        ## appear in the chapter.
        section_order = [None, "読み物　一", "会話　一", "読み物　二", "会話　二", "読み物　三", "会話　三", "読み物　四", "会話　四"]
        ## Cross-check against what we have.
        print(", ".join(sorted([str(x) for x in section_order])))
        print(", ".join(sorted([str(x) for x in sections.keys()])))
        if not set(sections.keys()).issubset(set(section_order)):
            die_screaming('unorderable section header')

        ## Prepare sections with(out) headers for final rendering as
        ## separate tables in the chapter docs.
        sectioned_data_list = []
        for s in section_order:
            if s in sections:
                sectioned_data_list.append({"header": s, "words": sections[s]})

        sectioned_chapter_sets.append({"chapter": str(chi), "data": sectioned_data_list})

        ## Write everything out.
        print(json.dumps(sectioned_data_list, indent = 4))
        with open(args.output, 'w') as output:
            output.write(json.dumps(sectioned_chapter_sets, indent = 4))

## You saw it coming...
if __name__ == '__main__':
    main()
