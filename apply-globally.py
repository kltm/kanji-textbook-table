####
#### Pull in a parsed blob and apply it to a template.
####
#### Example usage to analyze the usual suspects:
####  python3 apply-globally.py --help
####
#### Get report of current problems:
####  python3 apply-globally.py --input /tmp/jalphed-vocab-list.json  --template ./manual-glossary.template.html --output /tmp/glossary.html
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
LOGGER = logging.getLogger('apply-globally')
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
                        help='The file to output to')
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

    if not args.output:
        die_screaming('need an output file argument')
    LOGGER.info('Will output to file: ' + args.output)

    ## Bring data in.
    data_list = []
    with open(args.input, 'r') as json_in_f:
        data_list = json.load(json_in_f)

    ## Dump out
    LOGGER.info(json.dumps(data_list, indent = 4))
    rendered = pystache.render(output_template, {"all": data_list})
    with open(args.output, 'w') as output:
        output.write(rendered)

## You saw it coming...
if __name__ == '__main__':
    main()
