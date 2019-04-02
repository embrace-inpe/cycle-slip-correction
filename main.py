import argparse
import logging
import sys

from logging import handlers

import cycle_slip as cs


def main(rinex_folder, rinex_output):
    """

    :param rinex_folder:
    :param rinex_output:
    :return:
    """
    object_cs = cs.CycleSlip(rinex_folder, rinex_output)
    object_cs.initialize()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Correct Rinexes (GNSS receiver files) when cycle slip detect ')
    parser.add_argument('-rinex_folder', action="store", dest='rinex_folder',
                        help='Rinex folder: formats 2.11, 3.03 and Hatanaka are accept.')
    parser.add_argument('-rinex_output', action="store", dest='rinex_output',
                        help='Rinex output folder.')
    parser.add_argument('-verbose', action="store", dest='verbose', help='Print log of processing.')
    args = parser.parse_args()

    if args.verbose:
        log = logging.getLogger('')
        log.setLevel(logging.INFO)
        format = logging.Formatter("[%(asctime)s] {%(filename)-15s:%(lineno)-4s} %(levelname)-5s: %(message)s ",
                                   datefmt='%Y.%m.%d %H:%M:%S')

        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(format)

        fh = logging.handlers.RotatingFileHandler(filename='cycle_slip.log', maxBytes=(1048576 * 5), backupCount=7)
        fh.setFormatter(format)

        log.addHandler(ch)
        log.addHandler(fh)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")

    main(args.rinex_folder, args.rinex_output)
