####
#### Pull in a parsed blob and apply it to chapters.
####
#### Example usage to analyze the usual suspects:
####  python3 apply-to-chapters.py --help
####
#### Get report of current problems:
####  python3 apply-to-chapters.py --input /tmp/chapters.json --template ./word-html-frame.template.html --output /tmp/chapter
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
    parser.add_argument('-i', '--input',
                        help='The file to use as input')
    parser.add_argument('-t', '--template',
                        help='The output template to use')
    parser.add_argument('-o', '--output',
                        help='The file pattern to output to (*-1.html, etc.)')
    args = parser.parse_args()

    ## Up the verbosity level if we want.
    if args.verbose:
        LOGGER.setLevel(logging.INFO)
        LOGGER.info('Verbose: on')

    ## Ensure arguments and read in what is necessary.
    if not args.input:
        die_screaming('need an input argument')
    LOGGER.info('Will input from: ' + args.input)

    if not args.template:
        die_screaming('need a template argument for the output')
    output_template = None
    with open(args.template) as fhandle:
        output_template = fhandle.read()
    LOGGER.info('Will use: ' + args.template + ' as the output formatter')

    output_extension = os.path.splitext(args.template)[1]
    if not output_extension:
        die_screaming('need a template with an output extension')
    LOGGER.info('Will use: ' + output_extension + ' as the output extension')

    if not args.output:
        die_screaming('need an output pattern argument')
    LOGGER.info('Will output with pattern to: ' + args.output)

    ## Bring data in.
    data_list = []
    with open(args.input, 'r') as json_in_f:
        data_list = json.load(json_in_f)

    ## Dump out
    for item in data_list:
        chapter = str(item["chapter"])
        data = item["data"]

        ## Write everything out in our given format.
        LOGGER.info(json.dumps(data, indent = 4))
        rendered = pystache.render(output_template, {"data": data})
        with open(args.output + "-" + str(chapter) + output_extension, 'w') as output:
            output.write(rendered)

## You saw it coming...
if __name__ == '__main__':
    main()
