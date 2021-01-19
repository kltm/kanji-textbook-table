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
#### More complete:
####  python3 parse-vocab-list.py --tsv /tmp/list.tsv --output /tmp/parsed-vocab-list.json && python3 jalphabetical-bin.py --input /tmp/parsed-vocab-list.json --pattern vocab-list --output /tmp/blob-vocab-list-out.json && python3 apply-globally.py --input /tmp/blob-vocab-list-out.json --template word-glossary.template.html --output /tmp/glossary.html
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
            ## NOTE: useful:
            ##  for i in range(0, len(k)): print('"' + str(k[i]) + 'ー": "' + str(h[i]) + '",')
            # "ア", "ァ", "イ", "ィ", "ウ", "ゥ", "エ", "ェ", "オ", "ォ",
            # "カ", "ガ", "キ", "ギ", "ク", "グ", "ケ", "ゲ", "コ", "ゴ",
            # "サ", "ザ", "シ", "ジ", "ス", "ズ", "セ", "ゼ", "ソ", "ゾ",
            # "タ", "ダ", "チ", "ヂ", "ツ", "ッ", "ヅ", "テ", "デ", "ト", "ド",
            # "ナ", "ニ", "ヌ", "ネ", "ノ",
            # "ハ", "バ", "パ", "ヒ", "ビ", "ピ", "フ", "ブ", "プ", "ヘ", "ベ", "ペ", "ホ", "ボ", "ポ",
            # "マ", "ミ", "ム", "メ", "モ",
            # "ヤ", "ャ", "ユ", "ュ", "ヨ", "ョ",
            # "ラ", "リ", "ル", "レ", "ロ",
            # "ワ", "ヲ",
            # "ン",
            # "あ", "ぁ", "い", "ぃ", "う", "ぅ", "え", "ぇ", "お", "ぉ",
            # "か", "が", "き", "ぎ", "く", "ぐ", "け", "げ", "こ", "ご",
            # "さ", "ざ", "し", "じ", "す", "ず", "せ", "ぜ", "そ", "ぞ",
            # "た", "だ", "ち", "ぢ", "つ", "っ", "づ", "て", "で", "と", "ど",
            # "な", "に", "ぬ", "ね", "の",
            # "は", "ば", "ぱ", "ひ", "び", "ぴ", "ふ", "ぶ", "ぷ", "へ", "べ", "ぺ", "ほ", "ぼ", "ぽ",
            # "ま", "み", "む", "め", "も",
            # "や", "ゃ", "ゆ", "ゅ", "よ", "ょ",
            # "ら", "り", "る", "れ", "ろ",
            # "わ", "を",
            # "ん"]
            "あ", "ア", "ぁ", "ァ",
            "い", "イ", "ぃ", "ィ",
            "う", "ウ", "ぅ", "ゥ",
            "え", "エ", "ぇ", "ェ",
            "お", "オ", "ぉ", "ォ",
            "か", "カ", "が", "ガ",
            "き", "キ", "ぎ", "ギ",
            "く", "ク", "ぐ", "グ",
            "け", "ケ", "げ", "ゲ",
            "こ", "コ", "ご", "ゴ",
            "さ", "サ", "ざ", "ザ",
            "し", "シ", "じ", "ジ",
            "す", "ス", "ず", "ズ",
            "せ", "セ", "ぜ", "ゼ",
            "そ", "ソ", "ぞ", "ゾ",
            "た", "タ", "だ", "ダ",
            "ち", "チ", "ぢ", "ヂ",
            "つ", "ツ", "っ", "ッ", "づ", "ヅ",
            "て", "テ", "で", "デ",
            "と", "ト", "ど", "ド",
            "な", "ナ",
            "に", "ニ",
            "ぬ", "ヌ",
            "ね", "ネ",
            "の", "ノ",
            "は", "ハ", "ば", "バ", "ぱ", "パ",
            "ひ", "ヒ", "び", "ビ", "ぴ", "ピ",
            "ふ", "フ", "ぶ", "ブ", "ぷ", "プ",
            "へ", "ヘ", "べ", "ベ", "ぺ", "ペ",
            "ほ", "ホ", "ぼ", "ボ", "ぽ", "ポ",
            "ま", "マ",
            "み", "ミ",
            "む", "ム",
            "め", "メ",
            "も", "モ",
            "や", "ヤ", "ゃ", "ャ",
            "ゆ", "ユ", "ゅ", "ュ",
            "よ", "ヨ", "ょ", "ョ",
            "ら", "ラ",
            "り", "リ",
            "る", "ル",
            "れ", "レ",
            "ろ", "ロ",
            "わ", "ワ",
            "を", "ヲ",
            "ん", "ン"]
        jalphabetical_xform = {
            "アー": "アア",
            "ァー": "ァァ",
            "イー": "イイ",
            "ィー": "ィィ",
            "ウー": "ウウ",
            "ゥー": "ゥゥ",
            "エー": "エエ",
            "ェー": "ェェ",
            "オー": "オオ",
            "ォー": "ォォ",
            "カー": "カア",
            "ガー": "ガア",
            "キー": "キイ",
            "ギー": "ギイ",
            "クー": "クウ",
            "グー": "グウ",
            "ケー": "ケエ",
            "ゲー": "ゲエ",
            "コー": "コオ",
            "ゴー": "ゴオ",
            "サー": "サア",
            "ザー": "ザア",
            "シー": "シイ",
            "ジー": "ジイ",
            "スー": "スウ",
            "ズー": "ズウ",
            "セー": "セエ",
            "ゼー": "ゼエ",
            "ソー": "ソオ",
            "ゾー": "ゾオ",
            "ター": "タア",
            "ダー": "ダア",
            "チー": "チイ",
            "ヂー": "ヂイ",
            "ツー": "ツウ",
            "ッー": "ッウ",
            "ヅー": "ヅウ",
            "テー": "テエ",
            "デー": "デエ",
            "トー": "トオ",
            "ドー": "ドオ",
            "ナー": "ナア",
            "ニー": "ニイ",
            "ヌー": "ヌウ",
            "ネー": "ネエ",
            "ノー": "ノオ",
            "ハー": "ハア",
            "バー": "バア",
            "パー": "パア",
            "ヒー": "ヒイ",
            "ビー": "ビイ",
            "ピー": "ピイ",
            "フー": "フウ",
            "ブー": "ブウ",
            "プー": "プウ",
            "ヘー": "ヘエ",
            "ベー": "ベエ",
            "ペー": "ペエ",
            "ホー": "ホオ",
            "ボー": "ボオ",
            "ポー": "ポオ",
            "マー": "マア",
            "ミー": "ミイ",
            "ムー": "ムウ",
            "メー": "メエ",
            "モー": "モオ",
            "ヤー": "ヤア",
            "ャー": "ャァ",
            "ユー": "ユウ",
            "ュー": "ュィ",
            "ヨー": "ヨオ",
            "ョー": "ョォ",
            "ラー": "ラア",
            "リー": "リイ",
            "ルー": "ルウ",
            "レー": "レエ",
            "ロー": "ロオ",
            "ワー": "ワア",
            "ヲー": "ヲオ",
            # ## Remove voicing for sorting.
            # "ガ": "カ",
            # "ギ": "キ",
            # "グ": "ク",
            # "ゲ": "ケ",
            # "ゴ": "コ",
            # "ザ": "サ",
            # "ジ": "シ",
            # "ズ": "ス",
            # "ゼ": "セ",
            # "ゾ": "ソ",
            # "ダ": "タ",
            # "ヂ": "チ",
            # "ヅ": "ツ",
            # "デ": "テ",
            # "ド": "ト",
            # "バ": "ハ",
            # "パ": "ハ",
            # "ビ": "ヒ",
            # "ピ": "ヒ",
            # "ブ": "フ",
            # "プ": "フ",
            # "ベ": "ヘ",
            # "ペ": "ヘ",
            # "ボ": "ホ",
            # "ポ": "ホ",
            # "が": "か",
            # "ぎ": "き",
            # "ぐ": "く",
            # "げ": "け",
            # "ご": "こ",
            # "ざ": "さ",
            # "じ": "し",
            # "ず": "す",
            # "ぜ": "せ",
            # "ぞ": "そ",
            # "だ": "た",
            # "ぢ": "ち",
            # "づ": "つ",
            # "で": "て",
            # "ど": "と",
            # "ば": "は",
            # "ぱ": "は",
            # "び": "ひ",
            # "ぴ": "ひ",
            # "ぶ": "ふ",
            # "ぷ": "ふ",
            # "べ": "へ",
            # "ぺ": "へ",
            # "ぼ": "ほ",
            # "ぽ": "ほ"
        }
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
            "ぁ": "あ",
            "い": "い",
            "ぃ": "い",
            "う": "う",
            "ぅ": "う",
            "え": "え",
            "ぇ": "え",
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
            "ん": "ん",
            "ア": "あ",
            "ァ": "あ",
            "イ": "い",
            "ィ": "い",
            "ウ": "う",
            "ゥ": "う",
            "エ": "え",
            "ェ": "え",
            "オ": "お",
            "ォ": "お",
            "カ": "か",
            "ガ": "か",
            "キ": "き",
            "ギ": "き",
            "ク": "く",
            "グ": "く",
            "ケ": "け",
            "ゲ": "け",
            "コ": "こ",
            "ゴ": "こ",
            "サ": "さ",
            "ザ": "さ",
            "シ": "し",
            "ジ": "し",
            "ス": "す",
            "ズ": "す",
            "セ": "せ",
            "ゼ": "せ",
            "ソ": "そ",
            "ゾ": "そ",
            "タ": "た",
            "ダ": "た",
            "チ": "ち",
            "ヂ": "ち",
            "ツ": "つ",
            "ッ": "つ",
            "ヅ": "つ",
            "テ": "て",
            "デ": "て",
            "ト": "と",
            "ド": "と",
            "ナ": "な",
            "ニ": "に",
            "ヌ": "ぬ",
            "ネ": "ね",
            "ノ": "の",
            "ハ": "は",
            "バ": "は",
            "パ": "は",
            "ヒ": "ひ",
            "ビ": "ひ",
            "ピ": "ひ",
            "フ": "ふ",
            "ブ": "ふ",
            "プ": "ふ",
            "ヘ": "へ",
            "ベ": "へ",
            "ペ": "へ",
            "ホ": "ほ",
            "ボ": "ほ",
            "ポ": "ほ",
            "マ": "ま",
            "ミ": "み",
            "ム": "む",
            "メ": "め",
            "モ": "も",
            "ヤ": "や",
            "ャ": "や",
            "ユ": "ゆ",
            "ュ": "ゆ",
            "ヨ": "よ",
            "ョ": "よ",
            "ラ": "ら",
            "リ": "り",
            "ル": "る",
            "レ": "れ",
            "ロ": "ろ",
            "ワ": "わ",
            "ヲ": "を",
            "ン": "ん"}
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

            ## Transform the readings a bit according to our transform
            ## table.
            for original, target in jalphabetical_xform.items():
                a_reading = a_reading.replace(original, target)
                b_reading = b_reading.replace(original, target)

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
