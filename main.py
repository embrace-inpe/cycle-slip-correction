import argparse
import logging
import sys

from logging import handlers

import cycle_slip as cs


def main(rinex_folder, rinex_output):
    """
    :param rinex_folder: rinex folder: formats 3.01 to 3.03 are accept for while
    :param rinex_output: rinex output folder, in order to save possibles corrections
    :return: Analyse and detect cycle-slip per PRN, if so, save new files at the output folder declared
    """
    object_cs = cs.CycleSlip(rinex_folder, rinex_output)
    object_cs.initialize()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyse and detect cycle-slip effects over rinex\'s '
                                                 '(GNSS receiver files)')
    parser.add_argument('-rinex_folder', action="store", dest='rinex_folder',
                        help='Rinex folder: formats 3.01 to 3.03 are accept for while.')
    parser.add_argument('-rinex_output', action="store", dest='rinex_output',
                        help='Rinex output folder, in order to save possibles corrections.')
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
