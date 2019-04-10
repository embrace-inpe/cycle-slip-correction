import numpy as np
import collections

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

from scipy.signal import find_peaks


array_inteiro = np.array([0, 1, 2, 3, np.nan, np.nan, np.nan, np.nan, 23, 24, 25, np.nan, np.nan, 26, 27, np.nan, np.nan, np.nan, np.nan, 57, 58])
array_inteiro_not_nan = array_inteiro[~np.isnan(array_inteiro)]

print(array_inteiro)

valid_pos = np.where(~np.isnan(array_inteiro))
valid_pos = np.array(valid_pos).flatten().tolist()

nan_pos = np.where(np.isnan(array_inteiro))
nan_pos = np.array(nan_pos).flatten().tolist()

# fourth_der_array_inteiro_not_nan = np.diff(array_inteiro_not_nan, n=1)
# indexes_not_nan = find_peaks(abs(fourth_der_array_inteiro_not_nan))[0]
# indexes_not_nan = np.array(indexes_not_nan)
#
# indexes_before = []
#
# for index in indexes_not_nan:
#     element = array_inteiro_not_nan.item(index)
#     pos_before = np.where(array_inteiro == element)
#     pos_before = np.array(pos_before).flatten().tolist()
#     indexes_before.append(pos_before[0])

np_zeros = np.zeros(len(nan_pos))
array_inteiro_not_nan = np.concatenate((array_inteiro_not_nan, np_zeros), axis=0)


array_inteiro_not_nan[nan_pos] = np.nan
print(nan_pos, array_inteiro_not_nan)

# fig, axs = plt.subplots(3, 1)
#
# axs[0].plot(array_inteiro)
# axs[0].set_title('Teste')
# axs[0].set_ylabel('array')
# axs[0].grid(True)
#
# axs[1].plot(array_inteiro_not_nan)
# axs[1].set_ylabel('array_not_nan')
# axs[1].grid(True)
#
# axs[2].plot(fourth_der_array_inteiro_not_nan)
# axs[2].set_xlabel('Time')
# axs[2].set_ylabel('4th derivative')
# axs[2].grid(True)
#
# axs[1].scatter(indexes_not_nan, array_inteiro_not_nan[indexes_not_nan], marker='x', color='red', label='Cycle-slip')
# axs[2].scatter(indexes_not_nan, fourth_der_array_inteiro_not_nan[indexes_not_nan], marker='x', color='red', label='Cycle-slip')
#
# plt.savefig("Teste.pdf")
#
#
