import logging
import os
import time
import sys
import re
import datetime
import dateparser

import georinex as gr
import numpy as np

import downloads as dw
import parser as pr

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

from scipy.signal import find_peaks

REQUIRED_VERSION = 3.01
CONSTELLATIONS = ['G', 'R']
COLUMNS_IN_RINEX = {'3.03': {'G': {'L1': 'L1C', 'L2': 'L2W', 'C1': 'C1C', 'P1': 'C1W', 'P2': 'C2W'},
                             'R': {'L1': 'L1C', 'L2': 'L2C', 'C1': 'C1C', 'P1': 'C1P', 'P2': 'C2P'}
                             },
                    '3.02': {'G': {'L1': 'L1', 'L2': 'L2', 'C1': 'C1C', 'P1': 'C1W', 'P2': 'C2W'},
                             'R': {'L1': 'L1', 'L2': 'L2', 'C1': 'C1C', 'P1': 'C1P', 'P2': 'C2P'}
                             },
                    '3.01': {'G': {'L1': 'L1', 'L2': 'L2', 'C1': 'C1C', 'P1': 'C1W', 'P2': 'C2W'},
                             'R': {'L1': 'L1', 'L2': 'L2', 'C1': 'C1C', 'P1': 'C1P', 'P2': 'C2P'}
                             }
                    }


class Utils:
    """
    Useful methods for Cycle-Slip correcting
    """

    @staticmethod
    def array_timestamp_to_datetime(array_timestamp):
        """
        Convert an array with string timestamp to an array of datetimes

        :param array_timestamp: Array with string date in timestamp format
        :return: Array with datetime format elements
        """
        array = []

        for item in array_timestamp.values:
            array.append(dateparser.parse(str(item)))

        return array

    @staticmethod
    def plot_graphs_2(array_original, array, diff_, prn):
        fig, axs = plt.subplots(3, 1)

        axs[0].plot(array_original)
        axs[0].set_title(prn)
        axs[0].set_ylabel('rTEC-orig')
        axs[0].grid(True)

        axs[1].plot(array)
        axs[1].set_title(prn)
        axs[1].set_ylabel('rTEC-corr')
        axs[1].grid(True)

        axs[2].plot(diff_)
        axs[2].set_title("diff")
        axs[2].set_ylabel('diff')
        axs[2].grid(True)

        fig.savefig(prn + "_corrected.pdf")

    @staticmethod
    def plot_graphs(array, limit, fourth_der, indexes, prn):
        fig, axs = plt.subplots(2, 1)

        axs[0].plot(array, label='rTEC')
        axs[0].set_title(prn)
        axs[0].set_ylabel('[rTEC]')
        axs[0].legend(loc='best')
        axs[0].grid(True)

        axs[1].plot(fourth_der, label='4th der')
        axs[1].plot([0, len(fourth_der) - 1], [limit, limit], lw=0.5, ls='--', color='green')
        axs[1].plot([0, len(fourth_der) - 1], [-limit, -limit], lw=0.5, ls='--', color='green')
        axs[1].set_xlabel('Time')
        axs[1].set_ylabel('4th derivative')
        axs[1].legend(loc='best')
        axs[1].grid(True)

        axs[0].scatter(indexes, array[indexes], marker='x', color='red', label='Cycle-slip')
        # axs[1].scatter(indexes, fourth_der[indexes], marker='x', color='red', label='Cycle-slip')

        plt.savefig(prn + ".pdf")

    @staticmethod
    def setup_rinex_name(rinex_name):
        """
        Test if rinex name is in the old fashion way or in another formats. In case the format is newer or older, the
        method will always return the values needed
            Example of formats name accept:
                2.11: ALMA1520.18O
                3.03: ALMA00BRA_R_20181520000_01D_30S_MO.rnx

        :param rinex_name: String rinex filename
        :return: Returns the String rinex absolute path, and the year, month and doy related
        """
        if rinex_name.endswith(".rnx"):
            day_i, day_f = 16, 19
            year_i, year_f, year_type = 12, 16, "%Y"
            extens = "[rR][nN][xX]$"
        elif bool(re.match("[oO]$", rinex_name[-1:])):
            day_i, day_f = 4, 7
            year_i, year_f, year_type = -3, -1, "%y"
            extens = "[\\d]{2}[oO]$"
        else:
            logging.error(">>>> Error during rinex file reading. Check it and try again!")
            sys.exit()

        if len(rinex_name) == 0:
            logging.error('>> Something wrong with parameter \'rinex_name\'!. Empty name!')
            sys.exit()
        elif not rinex_name[0:4].isalpha():
            logging.error('>> Something wrong with parameter \'rinex_name\'!. IAGA code not well format!')
            sys.exit()
        elif not rinex_name[day_i:day_f].isdigit() or int(rinex_name[day_i:day_f]) > 366:
            logging.error('>> Something wrong with parameter \'rinex_name\'!. Invalid day of the year!')
            sys.exit()
        elif not bool(re.match(extens, rinex_name[-3:])):
            logging.error('>> Something wrong with parameter \'rinex_name\'!. Wrong extension or not well format!')
            sys.exit()

        doy = rinex_name[day_i:day_f]
        year = datetime.datetime.strptime(rinex_name[year_i:year_f], year_type).strftime('%Y')
        month = datetime.datetime.strptime(doy, '%j').strftime('%m')

        return year, month, doy

    @staticmethod
    def which_cols_to_load():
        """
        The rinex file is an extensive file, sometimes, with a lot of measures that are not interesting for this present
        work. Said that, in this method is selected only the columns used during the EMBRACE TEC and Bias estimation

        :return: The columns to load in rinex
        """
        columns_to_be_load = []
        requiried_version = str(REQUIRED_VERSION)
        dict_list_cols = list(COLUMNS_IN_RINEX[requiried_version].values())

        for constellation in dict_list_cols:
            for item in constellation.values():
                if item not in columns_to_be_load:
                    columns_to_be_load.append(item)

        return columns_to_be_load


class CycleSlip:
    """
    [Blewitt, 1990] Blewitt, G., 1990. An automatic editing Algorithms for GPS data. Geophysical
        Research Letters. 17(3), pp. 199-202.
            For each epoch ()
                For each tracked satellite ()
                    Declare cycle-slip when data hole greater than
                    If no data hole larger than 15 min, thence:
                        Update an array with the previous values (after the last cycle-slip)
                        Fit a n-degree polynomial to the previous values [footnotes 3].
                    Declare cycle-slip when:
                        Reset algorithm after cycle slip.
                End
            End
    """
    A = 40.3
    TECU = 1.0e16
    C = 299792458
    F1 = 1.57542e9
    F2 = 1.22760e9
    factor_1 = (F1 - F2) / (F1 + F2) / C
    factor_2 = (F1 * F2) / (F2 - F1) / C
    DIFF_TEC_MAX = 0.05
    LIMIT_STD = 2
    plot_it = False

    def __init__(self, folder, output_folder):
        self.folder = folder
        self.output_folder = output_folder

    def _prepare_factor(self, hdr, year, day, month):
        """
        The factors is used as a weight during the first estimate (relative TEC). For the GLONASS constellation, the
        factors are selective, per PRN, then, this values can be download from the own rinex or a URL

        :param hdr: The current rinex header, which brings the information of GLONASS channels
        :param year: Year of the current rinex
        :param month: Month of the current rinex
        :param day: Day of the current rinex
        :return: The GLONASS factors, already multiply by the frequencies F1 and F2
            GLONASS factor Python object. Format example:
                    factor_glonass = {
                                '01': VALUE_1, VALUE_2, VALUE_3
                                '02': VALUE_1, VALUE_2, VALUE_3
                                '03': VALUE_1, VALUE_2, VALUE_3
                                '04': VALUE_1, VALUE_2, VALUE_3
                                '05': ...
                        }
        """
        if "GLONASS SLOT / FRQ #" not in hdr:
            glonnas_channel = dw.DownloadGlonassChannel(year, day, month)
            glonnas_channel.download()

            glonass_channels_parser = pr.ParserChannels(glonnas_channel.file_uncompressed)
            glonass_channels_parser.parser()
        else:
            glonass_channels_parser = pr.ParserRinexChannels(hdr['GLONASS SLOT / FRQ #'])
            glonass_channels_parser.parser()

        return glonass_channels_parser.parsed

    def _detect(self, rtec, rtec_not_nan, prn):
        """
        The method precisely detect the variations over relative TEC (by the L1 and L2 differences). When a "degree"
        effect is present, a peak on the fourth derivative occurs. The index of this peak is store on "indexes"
        variable and then returned

        :param rtec: The relative TEC (with NaN)
        :param rtec_not_nan: The relative TEC (no NaN)
        :return: The rtec indexes where the "degree" effect is presented
        """
        fourth_der_not_nan = np.diff(rtec_not_nan, n=4)
        std_fourth_der_not_nan = np.nanstd(fourth_der_not_nan) * self.LIMIT_STD
        indexes = find_peaks(abs(fourth_der_not_nan), height=std_fourth_der_not_nan)[0]
        indexes = np.array(indexes)

        if len(indexes) == 0:
            logging.info(">>>>>> No discontinuities detected (by final differences) for PRN {}".format(prn))
        else:
            logging.info(">>>>>> Discontinuities detected in {} (not NaN) for PRN {}".format(indexes, prn))

        indexes_before = []
        for index in indexes:
            element = rtec_not_nan.item(index)
            pos_before = np.where(rtec == element)
            pos_before = np.array(pos_before).flatten().tolist()
            indexes_before.append(pos_before[0])

        if self.plot_it:
            if len(indexes) != 0:
                Utils.plot_graphs(rtec, std_fourth_der_not_nan, fourth_der_not_nan, indexes_before, prn)

        return indexes_before

    def _correct(self, l1, l2, rtec, mwlc, f1, factor_2, index, index_nan):
        """
        As a result of the detection of inconsistencies, this method compensate the irregularities on L1 and L2
        observations, directly at the rinex (obs variable)

        :param rtec: Not NaN relative TEC
        :param prn: The respective PRN
        :param mlwc: Not NaN MLWC factor
        :param f1:
        :param factor_2:
        :param index: The point of inconsistence (array with no NaN values)
        :param index_nan: The point of inconsistence (array with NaN values)
        :return: The corrected observation file and the respective relative TEC
        """
        diff_rtec = rtec[index] - rtec[index-1]
        diff_mwlc = mwlc[index] - mwlc[index-1]

        var_1 = diff_mwlc * self.C
        var_2 = var_1 / f1
        diff_2 = round((diff_rtec - var_2) * factor_2)
        diff_1 = diff_2 + round(diff_mwlc)

        l1[index_nan:len(l1)] -= diff_1
        l2[index_nan:len(l2)] -= diff_2

        return rtec, l1, l2

    def _which_not_nan_pos(self, array1, array2, i):
        """

        :param array1:
        :param array2:
        :param i:
        :return:
        """
        element = array2.item(i)
        i_nan = np.where(array1 == element)
        i_nan = np.array(i_nan).flatten().tolist()[0]

        return i_nan

    def _detect_and_correct_cycle_slip(self, obs_time, f1, f2, factor_1, factor_2, l1, l2, c1, p2, prn):
        """

        :param obs:
        :param hdr:
        :param prn:
        :param year:
        :param month:
        :param doy:
        :return:
        """
        j_start = 0

        rtec = ((l1 / f1) - (l2 / f2)) * self.C
        mwlc = (l1 - l2) - (f1 * c1 + f2 * p2) * factor_1

        not_nan_pos = np.where(~np.isnan(rtec))
        not_nan_pos = np.array(not_nan_pos).flatten().tolist()
        not_nan_time = [obs_time[x] for x in not_nan_pos]

        rtec_not_nan = rtec.copy()
        mwlc_not_nan = mwlc.copy()
        rtec_not_nan = rtec_not_nan[~np.isnan(rtec_not_nan)]
        mwlc_not_nan = mwlc_not_nan[~np.isnan(mwlc_not_nan)]

        logging.info(">>>> Detecting peaks on the 4th order final differences in rTEC...")
        indexes = self._detect(rtec, rtec_not_nan, prn)

        logging.info(">>>> Finding discontinuities and correcting cycle-slips (PRN {})...".format(prn))
        for i in range(1, len(not_nan_time)):
            t1 = not_nan_time[i-1]
            t2 = not_nan_time[i]

            if t2 - t1 > datetime.timedelta(minutes=15):
                j_start = i
                continue

            if i in indexes:
                logging.info(">>>>>> Indexes match ({}): correcting cycle-slips...".format(i, prn))
                i_nan = self._which_not_nan_pos(rtec, rtec_not_nan, i)
                l1, l2 = self._correct(l1, l2, rtec_not_nan, mwlc_not_nan, f1, factor_2, i, i_nan)

            if i - j_start + 1 >= 12:
                add_tec = 0
                add_tec_2 = 0

                for jj in range(1, 9):
                    add_tec = add_tec + rtec_not_nan[i-jj] - rtec_not_nan[i-jj-1]
                    add_tec_2 = add_tec_2 + pow(rtec_not_nan[i-jj] - rtec_not_nan[i-jj-1], 2)

                p_mean = add_tec / 10
                p_dev = np.maximum(np.sqrt(add_tec_2 / 10 - pow(p_mean, 2)), self.DIFF_TEC_MAX)
            else:
                p_mean = 0
                p_dev = self.DIFF_TEC_MAX * 2.5

            pmin_tec = p_mean - p_dev * 2.75
            pmax_tec = p_mean + p_dev * 2.75
            diff_rtec = rtec_not_nan[i] - rtec_not_nan[i-1]

            if not pmin_tec < diff_rtec and diff_rtec <= pmax_tec:
                i_nan = self._which_not_nan_pos(rtec, rtec_not_nan, i)
                l1, l2 = self._correct(l1, l2, rtec_not_nan, mwlc_not_nan, f1, factor_2, i, i_nan)

        return l1, l2

    def _cycle_slip_analysis(self, hdr, obs, year, month, doy):
        """

        :param hdr:
        :param obs:
        :param year:
        :param month:
        :param doy:
        :return:
        """
        prns = obs.sv.values
        obs_time = Utils.array_timestamp_to_datetime(obs.time)

        requiried_version = str(hdr.get('version'))
        cols_var = COLUMNS_IN_RINEX[requiried_version]

        for prn in prns:
            l1 = np.array(obs[cols_var[prn[0:1]]['L1']].sel(sv=prn).values)
            l2 = np.array(obs[cols_var[prn[0:1]]['L2']].sel(sv=prn).values)
            c1 = np.array(obs[cols_var[prn[0:1]]['C1']].sel(sv=prn).values)
            p2 = np.array(obs[cols_var[prn[0:1]]['P2']].sel(sv=prn).values)

            if prn[0:1] == 'R':
                factor_glonass = self._prepare_factor(hdr, year, month, doy)
                f1 = factor_glonass[prn[1:]][0]
                f2 = factor_glonass[prn[1:]][1]
                factor_1 = factor_glonass[prn[1:]][2]
                factor_2 = factor_glonass[prn[1:]][3]
            elif prn[0:1] == 'G':
                f1 = self.F1
                f2 = self.F2
                factor_1 = self.factor_1
                factor_2 = self.factor_2

            l1_new, l2_new = self._detect_and_correct_cycle_slip(obs_time, f1, f2, factor_1, factor_2, l1, l2, c1, p2, prn)

            rtec = ((l1 / f1) - (l2 / f2)) * self.C
            rtec_new = ((l1_new / f1) - (l2_new / f2)) * self.C

            diff_ = rtec - rtec_new

            Utils.plot_graphs_2(rtec, rtec_new, diff_, prn)

        return obs

    def initialize(self):
        """

        :return:
        """
        files = sorted(os.listdir(self.folder))
        logging.info(">> Found " + str(len(files)) + " file(s)")
        start_general = time.perf_counter()

        for file in files:
            start = time.perf_counter()

            complete_path = os.path.join(self.folder, file)
            complete_path_out = os.path.join(self.output_folder, file)

            logging.info(">>>> Reading rinex: " + file)
            hdr = gr.rinexheader(complete_path)

            version = hdr.get('version')
            columns_to_be_load = Utils.which_cols_to_load()

            if version >= REQUIRED_VERSION:
                obs = gr.load(complete_path, meas=columns_to_be_load, use=CONSTELLATIONS)

                year, month, doy = Utils.setup_rinex_name(file)
                obs = self._cycle_slip_analysis(hdr, obs, year, month, doy)

                # TODO: SAVE NEW obs RINEX ?
            else:
                logging.info(">>>>>> Rinex version {}. This code comprises the 3.01+ rinex version.".format(version))
                continue

            stop = time.process_time()
            logging.info(">> File " + file + " checked! Time: %.4f minutes" % float((start - stop) / 60))

        stop_general = time.process_time()
        logging.info(">> Processing done for " + str(len(files)) + " files in %.4f minutes"
                     % float((stop_general - start_general) / 60))
