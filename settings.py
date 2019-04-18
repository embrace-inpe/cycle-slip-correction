"""
Commom settings to all applications
"""

A = 40.3
TECU = 1.0e16
C = 299792458
F1 = 1.57542e9
F2 = 1.22760e9
factor_1 = (F1 - F2) / (F1 + F2) / C
factor_2 = (F1 * F2) / (F2 - F1) / C
DIFF_TEC_MAX = 0.05
LIMIT_STD = 7.5

plot_it = True

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
