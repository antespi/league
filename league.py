#! /usr/bin/env python

# League schedule
# Generate the schedule in CVS for a sport league
#
# Copyright (C) 2014  Antonio Espinosa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
League schedule
"""

######################################################################
# import the next four no matter what
######################################################################
import os
import sys
import textwrap
import traceback
from optparse import OptionParser


######################################################################
# for config file parsing, if needed
######################################################################
import yaml

######################################################################
# import other libraries and modules that do stuff
######################################################################
import random

######################################################################
# edit next two to your liking
######################################################################
__program__ = 'league'
__version__ = '1.0'

######################################################################
# the defaults for the config
######################################################################
DEFAULTS = {
    'mode' : 'random', # random | normal
    'people' : [],
}

def usage(parser, msg=None, width=70, pad=4, errno=0):
    lead_space = ' ' * (pad)
    w = width - pad
    err = ' ERROR '.center(w, '#').center(width)
    errbar = '#' * w
    errbar = errbar.center(width)
    hline = '=' * width
    if msg is not None:
        msg_list = str(msg).splitlines()
        msg = []
        for aline in msg_list:
            aline = lead_space + aline.rstrip()
            msg.append(aline)
        msg = '\n'.join(msg)
        print '\n'.join(('', err, msg, errbar, ''))
        print hline
    print
    print parser.format_help()
    sys.exit(errno)

######################################################################
# set up the options parser from the optparse module
#   - see http://docs.python.org/library/optparse.html
######################################################################
def doopts():

    program = os.path.basename(sys.argv[0])

    usg = """\
                usage: %s -h | [-c CONFIG]

                """
    usg = textwrap.dedent(usg) % program
    parser = OptionParser(usage=usg)

    parser.add_option('-c', '--config', dest='config',
                                        metavar='CONFIG', default=None,
                                        help='config file with people names')

    return parser



######################################################################
# auxiliar functions
######################################################################
# http://stackoverflow.com/questions/5913616/generating-natural-schedule-for-a-sports-league
def round_robin(units, sets = None):
    """ Generates a schedule of "fair" pairings from a list of units """
    count = len(units)
    sets = sets or (count - 1)
    half = count / 2
    for turn in range(sets):
        left = units[:half]
        right = units[count - half - 1 + 1:][::-1]
        pairings = zip(left, right)
        if turn % 2 == 1:
            pairings = [(y, x) for (x, y) in pairings]
        units.insert(1, units.pop())
        yield pairings

def encode(text):
    """
    For printing unicode characters to the console.
    """
    return text.encode('utf-8')

######################################################################
# process the command line logic, parse the config, etc.
######################################################################
def main():

    parser = doopts()
    (options, args) = parser.parse_args()

    ####################################################################
    # create the configuration that will be used within the program
    #     - first make a copy of DEFAULTS
    #     - then, update the copy with the user_config of
    #         the config file
    #     - this allows the user to specify only a subset of the config
    #     - try to catch problems with the config file and
    #         report them in usage()
    ####################################################################
    config = DEFAULTS.copy()
    if options.config:
        if os.path.exists(options.config):
            f = open(options.config)
            user_config = yaml.load(f.read())
            config.update(user_config)
        else:
            msg = "Config file '%s' does not exist." % options.config
            usage(parser, msg, errno=1)

    try:
        people = config['people']
        number = len(config['people'])
        if (number % 2) == 1:
            number += 1
            people.append('-')
        already = {}
        for p in people:
            already[p] = []
        if config['mode'] == 'random':
            random.shuffle(people)

        rounds = list(round_robin(people))
        n = 0
        for r in rounds:
            n += 1
            print '"Round %d",""' % n
            for t in r:
                p1 = t[0]
                p2 = t[1]
                # Just in case round robin is not doing for good
                if p1 in already[p2]: print "ERROR: %s has been already played with %s" % (p1, p2)
                if p2 in already[p1]: print "ERROR: %s has been already played with %s" % (p1, p2)
                already[p1].append(p2)
                already[p2].append(p1)
                print '"%s","%s"' % (encode(p1), encode(p2))

    except Exception, e:
        print traceback.format_exc()
        usage(parser, e, errno=255)

if __name__ == '__main__':
    main()




