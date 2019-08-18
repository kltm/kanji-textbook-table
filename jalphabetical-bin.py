####
#### Pull in a JSON blob produced by parse-vocab-list.py and re-blob it into
#### (japanese) alphabetically ordered sections.
####
#### Example usage to analyze the usual suspects:
####  python3 jalphabetical-bin.py --help
####
#### Get report of current problems and/or bin:
####  python3 jalphabetical-bin.py --pattern vocab-list --input /tmp/input.json --output /tmp/output.json
####

import sys
import argparse
import logging
import json
import functools

## Logger basic setup.
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('jalphabetical-bin')
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
    parser.add_argument('-p', '--pattern',
                        help='The input-specific pattern that we need to use to bin the output')
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
    if not args.pattern:
        die_screaming('need a pattern argument')
    if args.pattern not in ["vocab-list"]:
        die_screaming('pattern argument unknown')
    LOGGER.info('Will input from: ' + args.input)
    if not args.output:
        die_screaming('need an output argument')
    LOGGER.info('Will output to: ' + args.output)

    ## Define the upper and lower sorting criteria.
    if args.pattern == "vocab-list":
        upper_set_field = "chapter"
        section_field = "section"
        jalphabetical_order = [
            "あ", "い", "う", "え", "お",
            "か", "が", "き", "ぎ", "く", "ぐ", "け", "げ", "こ", "ご",
            "さ", "ざ", "し", "じ", "す", "ず", "せ", "ぜ", "そ", "ぞ",
            "た", "だ", "ち", "ぢ", "つ", "っ", "づ", "て", "で", "と", "ど",
            "な", "に", "ぬ", "ね", "の",
            "は", "ば", "ぱ", "ひ", "び", "ぴ", "ふ", "ぶ", "ぷ", "へ", "べ", "ぺ", "ほ", "ぼ", "ぽ",
            "ま", "み", "む", "め", "も",
            "や", "ゆ", "よ",
            "ら", "り", "る", "れ", "ろ",
            "わ", "を",
            "ん"]
        section_field_order = [
            "あ", "い", "う", "え", "お",
            "か", "き", "く", "け", "こ",
            "さ", "し", "す", "せ", "そ",
            "た", "ち", "つ", "て", "と",
            "な", "に", "ぬ", "ね", "の",
            "は", "ひ", "ふ", "へ", "ほ",
            "ま", "み", "む", "め", "も",
            "や", "ゆ", "よ",
            "ら", "り", "る", "れ", "ろ",
            "わ", "を",
            "ん"]
        section_field_membership = {
            "あ": "あ",
            "い": "い",
            "う": "う",
            "え": "え",
            "お": "お",
            "か": "か",
            "が": "か",
            "き": "き",
            "ぎ": "き",
            "く": "く",
            "ぐ": "く",
            "け": "け",
            "げ": "け",
            "こ": "こ",
            "ご": "こ",
            "さ": "さ",
            "ざ": "さ",
            "し": "し",
            "じ": "し",
            "す": "す",
            "ず": "す",
            "せ": "せ",
            "ぜ": "せ",
            "そ": "そ",
            "ぞ": "そ",
            "た": "た",
            "だ": "た",
            "ち": "ち",
            "ぢ": "ち",
            "つ": "つ",
            "っ": "つ",
            "づ": "つ",
            "て": "て",
            "で": "て",
            "と": "と",
            "ど": "と",
            "な": "な",
            "に": "に",
            "ぬ": "ぬ",
            "ね": "ね",
            "の": "の",
            "は": "は",
            "ば": "は",
            "ぱ": "は",
            "ひ": "ひ",
            "び": "ひ",
            "ぴ": "ひ",
            "ふ": "ふ",
            "ぶ": "ふ",
            "ぷ": "ふ",
            "へ": "へ",
            "べ": "へ",
            "ぺ": "へ",
            "ほ": "ほ",
            "ぼ": "ほ",
            "ぽ": "ほ",
            "ま": "ま",
            "み": "み",
            "む": "む",
            "め": "め",
            "も": "も",
            "や": "や",
            "ゆ": "ゆ",
            "よ": "よ",
            "ら": "ら",
            "り": "り",
            "る": "る",
            "れ": "れ",
            "ろ": "ろ",
            "わ": "わ",
            "を": "を",
            "ん": "ん"}
    else:
        die_screaming('unknown ordering pattern')

    ## Bring data in.
    data_list = []
    with open(args.input, 'r') as json_in_f:
        data_list = json.load(json_in_f)

    ## Sort the data into the different chapter sets.
    upper_set_field = "level"
    upper_sets = {}
    for item in data_list:
        #print(item)
        #print(item[upper_set_field])
        upper = str(item[upper_set_field])
        #print(upper + ".")
        if not upper in upper_sets:
            upper_sets[upper] = []
        upper_sets[upper].append(item)
    print(", ".join(sorted(upper_sets.keys(), key=int)))

    ## Loop over the different chapters to create the output.
    sectioned_upper_sets = []
    for chi in sorted(upper_sets.keys(), key=int):
        data_list = upper_sets[chi]

        ## Sort the upper/chapter sets into sections sets.
        sections = {}
        for item in data_list:
            section = item[section_field]
            if not section in sections:
                sections[section] = []
            sections[section].append(item)

        ## Manually add the sections in the order we want them to
        ## appear in the chapter.
        ## Cross-check against what we have.
        print(", ".join(sorted([str(x) for x in section_field_order])))
        print(", ".join(sorted([str(x) for x in sections.keys()])))
        if not set(sections.keys()).issubset(set(section_field_order)):
            die_screaming('unorderable section header')

        ## Prepare sections with(out) headers for final rendering as
        ## separate tables in the chapter docs.
        sectioned_data_list = []
        for s in section_field_order:
            if s in sections:
                sectioned_data_list.append({"header": s, "sections": sections[s]})

        sectioned_upper_sets.append({upper_set_field: str(chi), "data": sectioned_data_list})

        ## Write everything out.
        print(json.dumps(sectioned_data_list, indent = 4))
        with open(args.output, 'w') as output:
            output.write(json.dumps(sectioned_upper_sets, indent = 4))

    # ## First, jalphabetically sort the whole thing.
    # ## Order the points list using a custom comparison
    # def jsort(b, a):
    #     b_reading = b["reading"]
    #     a_reading = a["reading"]
    #     if a["point"] > b["point"]:
    #         return 1
    #     elif a["point"] < b["point"]:
    #         return -1
    #     else:
    # sorted_data_list = sorted(data_list, key=functools.cmp_to_key(jsort))


    # ## Sort the data into the different chapter sets.
    # upper_sets = {}
    # for item in data_list:
    #     chapter = str(item[upper_set_field])
    #     #print(chapter)
    #     if not chapter in upper_sets:
    #         upper_sets[chapter] = []
    #     upper_sets[chapter].append(item)
    # #print(", ".join(sorted(upper_sets.keys(), key=int)))

    # ## Loop over the different chapters to create the output.
    # sectioned_upper_sets = []
    # for chi in sorted(upper_sets.keys(), key=int):
    #     data_list = upper_sets[chi]

    #     ## Sort the upper/chapter sets into sections sets.
    #     sections = {}
    #     for item in data_list:
    #         section = item[section_field]
    #         if not section in sections:
    #             sections[section] = []
    #         sections[section].append(item)

    #     ## Manually add the sections in the order we want them to
    #     ## appear in the chapter.
    #     ## Cross-check against what we have.
    #     print(", ".join(sorted([str(x) for x in section_field_order])))
    #     print(", ".join(sorted([str(x) for x in sections.keys()])))
    #     if not set(sections.keys()).issubset(set(section_field_order)):
    #         die_screaming('unorderable section header')

    #     ## Prepare sections with(out) headers for final rendering as
    #     ## separate tables in the chapter docs.
    #     sectioned_data_list = []
    #     for s in section_field_order:
    #         if s in sections:
    #             sectioned_data_list.append({"header": s, "sections": sections[s]})

    #     sectioned_upper_sets.append({upper_set_field: str(chi), "data": sectioned_data_list})

    ## Write everything out.
#    print(json.dumps(sectioned_data_list, indent = 4))
    #     with open(args.output, 'w') as output:
    #         output.write(json.dumps(sectioned_upper_sets, indent = 4))

## You saw it coming...
if __name__ == '__main__':
    main()
