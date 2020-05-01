#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analysis of UWB and total station."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from tabulate import tabulate


P = Path(__file__).parent.absolute()  # File folder
PL = Path(__file__).parent.absolute() / 'plots'  # Plots folder

# false_x = 0*394500
# false_y = 0*4990800
# false_z = 0*300


def hist(data, xlabel, title):
    """Plot histogram."""
    plt.figure(constrained_layout=True)
    sns.distplot(data, color="#001427", label='2D',
                 bins=50, hist_kws=dict(alpha=0.7))
    plt.title(title)
    plt.ylabel('Density (kde)')
    plt.xlabel(xlabel)
    plt.tight_layout()
    plt.grid(which='both')
    plt.legend()
    plt.savefig(PL / (title + '.png'))


def trajectory(data, title, c):
    """Plot trajectory."""
    tag = data.dropna(subset=['x', 'y'])
    sta = data.dropna(subset=['x0', 'y0'])
    fig, ax = plt.subplots(constrained_layout=True, figsize=(6, 6))
    plt.plot(sta.x0, sta.y0, '.')
    plt.plot(tag.x, tag.y, '.')
    ax.annotate('Start', (sta.x0[0], sta.y0[0]))
    ax.annotate('End', (sta.x0[-1], sta.y0[-1]))
    plt.xlabel('East')
    plt.ylabel('North')
    plt.title(title)
    plt.legend(['Total station', 'UWB tag'])
    plt.grid(which='both')
    plt.axis('square')
    plt.savefig(PL / (title + str(c) + '.png'))


def error_vs_time(data, title):
    """Plot error vs time."""
    plt.figure(constrained_layout=True)
    data['2D'].plot()
    # data['3D'].plot()
    plt.title(title)
    plt.hlines(0.5, data.index[0], data.index[-1], colors='r',
               linestyles='dashed')
    plt.legend(['2D positioning'])
    plt.grid(which='both')
    plt.savefig(PL / (title + '.png'))


# Main code.
uwb_df = pd.read_csv(P / 'uwb.csv', index_col=0)
sta_df = pd.read_csv(P / 'sta.csv', index_col=0)

sta_df.columns = ['x0', 'y0', 'z0']

uwb_df.index = pd.to_datetime(uwb_df.index)
sta_df.index = pd.to_datetime(sta_df.index)

uwb_df['t'] = uwb_df.index
sta_df['t'] = sta_df.index

# uwb_df['x'] = uwb_df['x'] - false_x
# uwb_df['y'] = uwb_df['y'] - false_y
# uwb_df['z'] = uwb_df['z'] - false_z
# sta_df['x0'] = sta_df['x0'] - false_x
# sta_df['y0'] = sta_df['y0'] - false_y
# sta_df['z0'] = sta_df['z0'] - false_z

sta_new = sta_df.resample('S').first()
uwb_new = uwb_df.copy()
uwb_new['t'] = uwb_df['t'].values.astype(np.int64) / 10**9
sta_new['t'] = sta_new['t'].values.astype(np.int64) / 10**9


df = sta_new.copy()
df['uwb_t'] = [min(uwb_new['t'], key=lambda x:abs(x-y))
               for y in df['t']]

uwb_new.index = uwb_new.index.values.astype(np.int64) / 10**9

df['x'] = list(uwb_new.loc[df['uwb_t'].values, 'x'])
df['y'] = list(uwb_new.loc[df['uwb_t'].values, 'y'])
df['z'] = list(uwb_new.loc[df['uwb_t'].values, 'z'])

# sta_new = sta_df.resample('0.5S').mean()
# uwb_new = uwb_df.resample('0.5S').mean()
# df = pd.merge(uwb_new, sta_new, how='inner', on=['Time'])

df['2D'] = np.sqrt((df.x-df.x0)**2 + (df.y-df.y0)**2)
df['3D'] = np.sqrt((df.x-df.x0)**2 + (df.y-df.y0)**2 + (df.z-df.z0)**2)

exp_list = [df.loc[pd.to_datetime('2020-01-31 11:18:06.0'):
                   pd.to_datetime('2020-01-31 11:25:47.0')],
            df.loc[pd.to_datetime('2020-01-31 11:52:00.0'):
                   pd.to_datetime('2020-01-31 12:02:00.0')],
            df.loc[pd.to_datetime('2020-01-31 14:15:50.0'):
                   pd.to_datetime('2020-01-31 14:25:00.0')],
            df.loc[pd.to_datetime('2020-01-31 15:08:00.0'):
                   pd.to_datetime('2020-01-31 15:25:50.0')]]


stats = pd.DataFrame()
stats3 = pd.DataFrame()
for cnt, exp in enumerate(exp_list):
    # Plots.
    hist(exp['2D'].dropna(), '2D difference', '2D Hist - Exp' + str(cnt))
    hist(exp['3D'].dropna(), '3D difference', '3D Hist - Exp' + str(cnt))
    no_out_2D = exp.where(exp['2D'] < 1.5).dropna()
    no_out_3D = exp.where(exp['3D'] < 2).dropna()
    hist(no_out_2D['2D'], '2D difference', '2D Hist_out - Exp' + str(cnt))
    hist(no_out_3D['3D'], '3D difference', '3D Hist_out - Exp' + str(cnt))
    z_error = exp['z'] - np.mean(exp['z'])
    z_error = z_error.dropna()
    hist(list(z_error), 'Z oscillation', 'z_hist - Exp' + str(cnt))

    # trajectory(exp, 'Trajectory - Exp' + str(cnt))
    trajectory(exp, 'Trajectory comparison', cnt)

    error_vs_time(exp, 'Error vs Time - Exp' + str(cnt))

    # Save statistics for the current experiment.
    stats['Exp' + str(cnt)] = exp['2D'].describe()
    stats3['Exp' + str(cnt)] = exp['3D'].describe()

# Print statistics.
stats['Mean'] = stats.mean(axis=1)
print(tabulate(stats, headers='keys', tablefmt='pretty'))
stats3['Mean'] = stats3.mean(axis=1)
print(tabulate(stats3, headers='keys', tablefmt='pretty'))
# print(stats)


# Corridor analysis.
# exp = exp_list[0]
# corridor = exp.where(exp['x'] < 42 + 394500)
# corridor = corridor.where(corridor['y'] > 77+4990800)
# corridor = corridor.dropna(subset=['x', 'y'])
#
# model = sm.OLS(corridor.y, sm.add_constant(corridor.x))
# results = model.fit()
# print(results.summary())
#
# plt.figure(constrained_layout=True)
# plt.plot(corridor.x, results.predict(), 'r', linewidth=1,
#          label='Regression line')
# plt.scatter(corridor.x, corridor.y, label='Measurements')
# plt.xlabel('East')
# plt.ylabel('North')
# plt.grid(which='both')
# plt.legend()
# plt.title("Corridor")
# plt.savefig(PL / 'corridor.png')
#
#
# dist = []
# m = results.params['x']
# q = results.params['const']
# for point in range(0, len(corridor)):
#     xp = corridor.x[point]
#     yp = corridor.y[point]
#     dist.append(np.abs(yp - (m*xp + q))/np.sqrt(1 + m**2))
#
# corridor_dev = np.mean(dist)

# plt.show()
