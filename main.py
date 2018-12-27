import argparse
import logging
import os
import sys
import time
from logging import handlers

import georinex as gr
import matplotlib.pyplot as plt
import numpy as np
import peakutils
from matplotlib import gridspec

plt.style.use("ggplot")

CONSTELLATIONS = ['G', 'R']
PERMITTED = ['L1', 'L1C']


def _plot_graphs(times, array, first_der, second_der, indexes):
    gs = gridspec.GridSpec(3, 1)
    ax0 = plt.subplot(gs[0])
    ax0.set_title('L1')
    ax0.plot(times, array)

    ax1 = plt.subplot(gs[1])
    ax1.set_title('1st derivative')
    ax1.plot(times, first_der)

    ax2 = plt.subplot(gs[2])
    ax2.set_title('2nd derivative')
    ax2.plot(times, second_der)

    if len(indexes) != 0:
        ax0.scatter(indexes, np.array(array)[indexes.astype(int)], marker='o', color='red')
        ax1.scatter(indexes, np.array(first_der)[indexes.astype(int)], marker='o', color='red')
        ax2.scatter(indexes, np.array(first_der)[indexes.astype(int)], marker='o', color='red')

    plt.tight_layout()
    plt.show()


def _check_variation(times, array, plot_it):
    first_der = np.diff(array)
    first_der = np.concatenate(([0], first_der))

    second_der = np.diff(first_der)
    second_der = np.concatenate(([0], second_der))

    indexes = peakutils.indexes(first_der, thres=0.02 / max(first_der), min_dist=1)

    if plot_it:
        _plot_graphs(times, array, first_der, second_der, indexes)


def _complete_data(times, obs):
    pass


def detect_l1_discontinuity(obs, column):
    flag = []
    times = obs.time.values
    prns = obs.sv.values

    # array = [0, -1, -2, -3, -4, -5, -6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    # _check_variation(list(range(0, len(array))), array, True)

    for prn in prns:
        _check_variation(times, obs[column].sel(sv=prn).values, True)

        # if variacao > limiar
        #     flag.append(True)
        # else:
        #     flag.append(False)

    return flag


def correct_cycle_slip(obs):
    """
    [Blewitt, 1990] Blewitt, G., 1990. An automatic editing Algorithms for GPS data. Geophysical
    Research Letters. 17(3), pp. 199-202.

    For each epoch ()
        For each tracked satellite ()
            Declare cycle-slip when data hole greater than  [footnotes 2].
            If no data hole larger than , thence:
            Update an array with the previous  values (after the last cycle-slip)
            Fit a n-degree polynomial to the previous values [footnotes 3].
            Declare cycle-slip when:
                Reset algorithm after cycle slip.
        End
    End

    :param obs: 
    :return: 
    """


def main(rinex_folder):
    files = sorted(os.listdir(rinex_folder))
    logging.info(">> Found " + str(len(files)) + " file(s)")
    tic_general = time.clock()

    for file in files:
        tic = time.clock()

        complete_path = os.path.join(rinex_folder, file)

        logging.info(">>>> Reading rinex: " + file)
        hdr = gr.rinexheader(complete_path)

        fields = hdr.get('fields')
        if hdr.get('version') == 2.11:
            result = np.isin(fields, PERMITTED)
            ind = [i for i, true in enumerate(result) if true][0]
            obs = gr.load(complete_path, use=CONSTELLATIONS)
            is_discontinuous = detect_l1_discontinuity(obs, fields[ind])

        elif hdr.get('version') == 3.03:
            for key, constellation in fields.items():
                if key in CONSTELLATIONS:
                    result = np.isin(constellation, PERMITTED)
                    ind = [i for i, true in enumerate(result) if true][0]
                    obs = gr.load(complete_path, use=key)
                    is_discontinuous = detect_l1_discontinuity(obs, constellation[ind])
        else:
            logging.info(">>>> Unknown rinex version for Cycle-Slip correction: " + hdr.get('version'))

        if is_discontinuous:
            logging.info(">>>>>> L1 discontinuous! Correcting cycle slip for file " + file)
            # correct_cycle_slip(obs)
        else:
            logging.info(">>>>>> No discontinuity detected for file " + file)

        toc = time.clock()
        logging.info(">> File " + file + " checked! Time: %.4f minutes" % float((toc - tic) / 60))

    toc_general = time.clock()
    logging.info(">> Processing done for " + str(len(files)) + " files in %.4f minutes"
                 % float((toc_general - tic_general) / 60))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Correct Rinexes (GNSS receiver files) when cycle slip detect ')

    parser.add_argument('-rinex_folder', action="store", dest='rinex_folder',
                        help='Rinex folder: formats 2.11, 3.03 and Hatanaka are accept.')
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

    main(args.rinex_folder)
