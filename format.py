####
#### Convert a TSV into a publishable table.
####
#### Example usage to analyze the usual suspects:
####  python3 format.py --help
####
#### Get report of current problems:
####  python3 format.py --tsv ~/tmp/kanji-list.tsv --template ./word-html-frame.template.html --output /tmp/out.html
####

import sys
import argparse
import logging
import csv
import pystache
import json

## Logger basic setup.
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('format')
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
    parser.add_argument('-d', '--tsv',
                        help='The TSV data file to read in')
    parser.add_argument('-t', '--template',
                        help='The output template to use')
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
    if not args.template:
        die_screaming('need a template argument for the output')
    output_template = None
    with open(args.template) as fhandle:
        output_template = fhandle.read()
    LOGGER.info('Will use: ' + args.template + ' as the output formatter')
    if not args.output:
        die_screaming('need an output argument')
    LOGGER.info('Will output to: ' + args.output)

    ## Bring on all data in one sweep, formatting and adding
    ## appropriate parts to internal format so that we can simply
    ## output in any mustache template.
    data_list = []
    with open(args.tsv, 'r') as tsv_in:
        tsv_in = csv.reader(tsv_in, delimiter='\t')

        ## Process data.
        first_line_p = True
        i = 0
        for line in tsv_in:
            i = i + 1
            if first_line_p:
                first_line_p = False
                continue
            else:
                count = len(line)
                if count != 10:
                    die_screaming('malformed line: '+ str(i) +' '+ '\t'.join(line))
                else:

                    # print("-------")
                    # print(type(line[3]))
                    # print(len(line[3]))
                    # print(line[3])

                    ## Base parsing everything into a common object.
                    data_object = {}
                    data_object["level"] = str(line[0]) # req
                    data_object["chapter"] = str(line[1]) # req
                    data_object["raw-japanese"] = str(line[2]) # req
                    data_object["raw-ruby"] = line[3] if (type(line[3]) is str and len(line[3]) > 0) else None # opt
                    data_object["reading"] = str(line[4]) # req
                    data_object["meaning"] = line[5] # req
                    data_object["section"] = line[6] if (type(line[6]) is str and len(line[6]) > 0) else None # opt
                    data_object["extra"] = True if (type(line[7]) is str and line[7] == '*') else None # opt
                    data_object["grammar-point"] = line[8] if (type(line[8]) is str and len(line[8]) > 0) else None # opt
                    data_object["notes"] = line[9] if (type(line[9]) is str and len(line[9]) > 0) else None # opt

                    ## Basic error checking.
                    for required_entry in ["level", "chapter", "raw-japanese", "reading", "meaning"]:
                        if not data_object[required_entry] is str and not len(data_object[required_entry]) > 0:
                            die_screaming('malformed line with "'+required_entry+'" at '+ str(i) +': '+ '\t'.join(line))

                    ## Additional metadata that we'll want.
                    data_object["row"] = str(i) # inserted

                    # print(data_object["raw-ruby"])

                    ## Transform the comma/pipe-separated data raw "Ruby"
                    ## object into something usable, if extant.
                    ruby = []
                    if data_object["raw-ruby"]:
                        try:
                            ruby_set_list_raw = data_object["raw-ruby"].split(",")
                            for ruby_set_raw in ruby_set_list_raw:
                                ruby_set_pre = ruby_set_raw.strip()
                                print("ruby_set_pre: " + ruby_set_pre)
                                ruby_set = ruby_set_pre.split("|")
                                ruby_kanji = ruby_set[0].strip()
                                ruby_reading = ruby_set[1].strip()
                                ruby.append({"kanji": ruby_kanji,
                                             "reading": ruby_reading})
                        except:
                            die_screaming('error parsing ruby at '+ str(i) +': '+ '\t'.join(line))
                    data_object["ruby"] = ruby

                    ## Now that we have that parsed, create a new
                    ## version of the "Japanese" ("raw-japanese")
                    ## column with mustache renderable data hints.
                    print('^^^')
                    j = data_object["raw-japanese"]
                    remaining_rubys = len(ruby)
                    ruby_parse_data = []
                    for r in ruby:
                        ## Case when kanji not found in remaining
                        ## japanese.
                        print("japanese: " + j)
                        print("kanji: " + r["kanji"])
                        print("reading: " + r["reading"])
                        if j.find(r["kanji"]) == -1:
                            print('malformed line at '+ str(i) +': '+ '\t'.join(line))
                            die_screaming('bad japanese/ruby at line '+ str(i))
                        else:

                            ## Some numbers we'll want on hand.
                            jl = len(j) # the remaining length of the japanese
                            rl = len(r["kanji"]) # the length of the ruby
                            offset = j.find(r["kanji"]) # the offset of the kanji
                            print(str(jl))
                            print(str(rl))
                            print(str(offset))

                            ## Get the pre-ruby string added, if
                            ## extant.
                            if offset == 0:
                                pass
                            else:
                                pre_string = j[0:(offset)]
                                print('pre_string: ' + pre_string)
                                ruby_parse_data.append({"string": pre_string,
                                                        "has-ruby": False})

                            ## Add the ruby string section.
                            ruby_string = j[offset:(offset+rl)]
                            print('ruby_string: ' + ruby_string)
                            ruby_parse_data.append({"string": ruby_string,
                                                    "reading":r["reading"],
                                                    "has-ruby": True})

                            ## If this is the last ruby we're dealing
                            ## with, we're done and add the rest of
                            ## the string. Otherwise, "soft loop" on
                            ## the shorter string and next ruby.
                            remaining_rubys = remaining_rubys - 1
                            if remaining_rubys == 0:
                                ## Last one, add any remaining string.
                                if (offset+rl) < jl:
                                    post_string = j[(offset+rl):jl]
                                    print('post_string: ' + post_string)
                                    ruby_parse_data.append({"string": post_string,
                                                            "has-ruby": False})
                            else:
                                j = j[(offset+rl):jl]

                    data_object["rich-japanese"] = ruby_parse_data

                    ## Onto the pile.
                    data_list.append(data_object)

    print(json.dumps(data_list, indent = 4))

    ## Write everything out in our given format.
    rendered = pystache.render(output_template, {"data": data_list})
    with open(args.output, 'w') as output:
        output.write(rendered)

## You saw it coming...
if __name__ == '__main__':
    main()
