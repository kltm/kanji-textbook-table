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
        for line in tsv_in:
            count = len(line)
            if count != 10:
                die_screaming('malformed line: ' + '\t'.join(line))
            else:

                ## TODO: Transform the comma/pipe-separated data
                ## section into something usable.

                ## TODO: Now that we have that parsed, create a new version
                ## of the previous column with mustache renderable
                ## data hints.

                data_list.append(line)

    ## Write everything out in our given format.
    rendered = pystache.render(output_template, data_list)
    with open(args.output, 'w') as output:
        output.write(rendered)

## You saw it coming...
if __name__ == '__main__':
    main()
