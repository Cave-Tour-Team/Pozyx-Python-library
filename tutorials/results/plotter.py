#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plot graphs."""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

P = Path(__file__).parent.absolute()
FILENAME = P / "tests_3.json"
STD_FACTOR = 3
HOW_MANY = 19


class MyData:
    """Database."""

    def __init__(self, filename, std_factor, how_many):
        """Initialise database."""
        self.load_data(filename)
        self.filter_zeros()
        self.filter_first(how_many)
        self.compute_std()
        self.filter_std(std_factor)
        self.recompute_mean()

    def load_data(self, filename):
        """Load data from file."""
        with open(filename, "r") as f:
            self.data = json.loads(f.read())

    def compute_std(self):
        """Compute std and add to data."""
        for item in self.data["data"]:
            list = [m["mm"] for m in item["measurements"]]
            sdd = np.std(list)
            item["std"] = sdd

    def filter_zeros(self):
        """Remove null measurements."""
        for item in self.data["data"]:
            item["measurements"] = [m for m in item["measurements"]
                                    if m["mm"] != 0]

    def filter_std(self, factor):
        """Remove measurements outside std range."""
        for item in self.data["data"]:
            lim_high = item["mm_mean"] + factor*item["std"]
            lim_low = item["mm_mean"] - factor*item["std"]
            item["measurements"] = [m for m in item["measurements"]
                                    if ((lim_low <= m["mm"]) and
                                        (m["mm"] <= lim_high))]

    def filter_first(self, how_many):
        """Filter first values."""
        for item in self.data["data"]:
            item["measurements"] = [m for c, m in
                                    enumerate(item["measurements"])
                                    if c > how_many]

    def recompute_mean(self):
        """Update mean distances."""
        for item in self.data["data"]:
            item["mm_mean"] = np.mean([m["mm"] for m in item["measurements"]])
        for item in self.data["data"]:
            item["mm_error_mean"] = (item["mm_real"] -
                                     np.mean([m["mm"] for m
                                             in item["measurements"]]))

    def plot_scatter(self, channels, field, title, ylab):
        """Get specific data."""
        plt.figure(figsize=(16, 6))
        for c in channels:
            x_distances = []
            y_list = []
            for item in self.data["data"]:
                if item["channel"] == c:
                    y_list.append(item[field])
                    if item["mm_real"] not in x_distances:
                        x_distances.append(item["mm_real"])
            y_list = [y/1000 for y in y_list]
            y_list = [y for _, y in sorted(zip(x_distances, y_list))]
            x_distances.sort()
            x_distances = [x/1000 for x in x_distances]
            plt.plot(x_distances, y_list, '.-', linewidth=2)
        plt.legend(["Channel 1", "Channel 2", "Channel 3", "Channel 4",
                    "Channel 5", "Channel 7"], loc="best")
        plt.xticks(x_distances, labels=x_distances)
        plt.xlabel("Real distance [m]")
        plt.ylabel(ylab)
        plt.grid()
        plt.title(title)

    def print_info(self):
        """Print info about database."""
        for item in self.data["data"]:
            length = len(item["measurements"])
            std = item["std"]
            mean = item["mm_mean"]
            channel = item["channel"]
            print("SD: %.2f\tNum of measurements. %d\tMean: %.2f\tChannel: %d"
                  % (std, length, mean, channel))


def main():
    """Plot different kinds of data."""
    md = MyData(FILENAME, STD_FACTOR, HOW_MANY)
    md.print_info()
    md.plot_scatter(channels=[1, 2, 3, 4, 5, 7], field="mm_mean",
                    title="Mean distance", ylab="Measured distance [m]")
    md.plot_scatter(channels=[1, 2, 3, 4, 5, 7], field="mm_err_mean",
                    title="Mean error", ylab="Mean error [m]")
    md.plot_scatter(channels=[1, 2, 3, 4, 5, 7], field="std",
                    title="std", ylab="std")
    plt.show()
    print("--- END ---")


if __name__ == '__main__':
    main()
