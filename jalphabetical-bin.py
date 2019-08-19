####
#### Pull in a JSON blob produced by parse-vocab-list.py and re-blob it into
#### (japanese) alphabetically ordered sections.
####
#### Example usage to analyze the usual suspects:
####  python3 jalphabetical-bin.py --help
####
#### Get report of current problems and/or bin:
####  jalphabetical-bin.py --pattern vocab-list --input /tmp/parsed-vocab-list.json --output /tmp/jalphed-vocab-list.json
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
            "あ", "い", "う", "え", "お", "ぉ",
            "か", "が", "き", "ぎ", "く", "ぐ", "け", "げ", "こ", "ご",
            "さ", "ざ", "し", "じ", "す", "ず", "せ", "ぜ", "そ", "ぞ",
            "た", "だ", "ち", "ぢ", "つ", "っ", "づ", "て", "で", "と", "ど",
            "な", "に", "ぬ", "ね", "の",
            "は", "ば", "ぱ", "ひ", "び", "ぴ", "ふ", "ぶ", "ぷ", "へ", "べ", "ぺ", "ほ", "ぼ", "ぽ",
            "ま", "み", "む", "め", "も",
            "や", "ゃ", "ゆ", "ゅ", "よ", "ょ",
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
            "ぉ": "お",
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
            "ゃ": "や",
            "ゆ": "ゆ",
            "ゅ": "ゆ",
            "よ": "よ",
            "ょ": "よ",
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

    ## Sort the items into the different letter sets.
    letter_sets = {}
    for item in data_list:
        #print(item)
        #print(item[upper_set_field])
        reading = str(item["reading"])
        pre_letter = reading[0]
        letter = section_field_membership[pre_letter] if section_field_membership[pre_letter] else "?"
        if not letter in letter_sets:
            letter_sets[letter] = []
        letter_sets[letter].append(item)
    print(", ".join(sorted(letter_sets.keys())))

    ## Loop over the different chapters to create the output.
    ordered_letter_sets = []
    for l in sorted(letter_sets.keys()): # actually seems to sort the japanese correctly
        ## Grab a letter set.
        data_list = letter_sets[l]

        ## Order the data list of the letter set.
        ## First, jalphabetically sort the whole thing.
        ## Order the points list using a custom comparison
        def jsort(b, a):

            b_reading = b["reading"]
            a_reading = a["reading"]

            print("---")

            ## Remove annoying crap.
            for bad in ["（", "）", "(", ")", "～", "~", " ", "・", "…", "."]:
                b_reading = b_reading.replace(bad, "")
                a_reading = a_reading.replace(bad, "")

            ## Find the shorter word; remember which is which.
            shorter_word = None
            longer_word = None
            shorter_word_is_a_p = None
            if len(b_reading) <  len(a_reading):
                shorter_word = b_reading
                longer_word = a_reading
                shorter_word_is_a_p = False
            else:
                shorter_word = a_reading
                longer_word = b_reading
                shorter_word_is_a_p = True

            ## Pick the letter at position and compare.
            shorter_word_is_first_p = True
            for i, swl in enumerate(shorter_word):
                lwl = longer_word[i]
                print(swl, lwl)
                if swl == lwl:
                    pass
                if jalphabetical_order.index(swl) < jalphabetical_order.index(lwl):
                    shorter_word_is_first_p = True
                    break
                if jalphabetical_order.index(swl) > jalphabetical_order.index(lwl):
                    shorter_word_is_first_p = False
                    break

            if shorter_word_is_first_p and shorter_word_is_a_p:
                return 1
            elif shorter_word_is_first_p and not shorter_word_is_a_p:
                return -1
            elif not shorter_word_is_first_p and shorter_word_is_a_p:
                return -1
            elif not shorter_word_is_first_p and not shorter_word_is_a_p:
                return 1
            else:
                return 0
        sorted_data_list = sorted(data_list, key=functools.cmp_to_key(jsort))

        ordered_letter_sets.append({"letter": l,
                                    "data": sorted_data_list})

    ## Write everything out.
    print(json.dumps(ordered_letter_sets, indent = 4))
    with open(args.output, 'w') as output:
        output.write(json.dumps(ordered_letter_sets, indent = 4))

## You saw it coming...
if __name__ == '__main__':
    main()
