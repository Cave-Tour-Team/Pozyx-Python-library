#!/usr/bin/env python3
"""Plot data from csv."""
import pandas as pd
import matplotlib.pyplot as plt

FILENAME = 'Pos_12-54-2020.01.20.csv'


def plot_path(df):
    """Plot X vs Y with anchor labels."""
    fig, ax = plt.subplots()
    print(df.describe())
    ax.scatter(df["posX[mm]"], df["posY[mm]"], marker='.')
    plt.xlabel('X (mm)')
    plt.ylabel('Y (mm)')
    false_x = 394500
    false_y = 4990800

    x_anchors = [int((394541.63780-false_x)*1000),
                 int((394535.87380-false_x)*1000),
                 int((394546.46551-false_x)*1000),
                 int((394541.79053-false_x)*1000),
                 int((394554.71364-false_x)*1000),
                 int((394551.31736-false_x)*1000)]

    y_anchors = [int((4990886.425448-false_y)*1000),
                 int((4990875.13956-false_y)*1000),
                 int((4990883.86831-false_y)*1000),
                 int((4990871.96470-false_y)*1000),
                 int((4990875.21233-false_y)*1000),
                 int((4990868.81968-false_y)*1000)]

    labels_anchors = [' 0x617e', ' 0x6119', ' 0x6735', ' 0x6726',
                      ' 0x6726 (P9)', ' 0x6726 (P10)']

    # Print anchor positions
    ax.scatter(x_anchors, y_anchors, marker="s", color='red')

    # Add labels on scatterplot
    for i, s in enumerate(labels_anchors):
        ax.annotate(s, (x_anchors[i], y_anchors[i]))
    ax.annotate("Start", (df["posX[mm]"].iloc[0], df["posY[mm]"].iloc[0]))
    ax.annotate("End", (df["posX[mm]"].iloc[-1], df["posY[mm]"].iloc[-1]))

    plt.axis('square')
    plt.legend(["Tag position", "Anchors"])
    plt.grid(which='both')
    plt.title("Tag path")


def read_file(filename):
    """Read csv and save to dataframe."""
    df = pd.read_csv(filename, skiprows=2)
    return df


def main():
    """Plot data."""
    df = read_file(FILENAME)
    plot_path(df)
    plt.show()


if __name__ == '__main__':
    main()
