#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

FILENAME = 'Pos_12-54-2020.01.20.csv'

def main():
    df = pd.read_csv(FILENAME, skiprows=2)
    print(df)
    plt.scatter(df["posX[mm]"], df["posY[mm]"])
    plt.axis('square')
    plt.xlabel('X (mm)')
    plt.ylabel('Y (mm)')
    false_x = 394500
    false_y = 4990800
    plt.scatter(int((394541.63780-false_x)*1000), int((4990886.425448-false_y)*1000), label='0x617e')
    plt.scatter(int((394535.87380-false_x)*1000), int((4990875.13956-false_y)*1000), label='0x6119')
    plt.scatter(int((394546.46551-false_x)*1000), int((4990883.86831-false_y)*1000), label='0x6735')
    plt.scatter(int((394541.79053-false_x)*1000), int((4990871.96470-false_y)*1000), label='0x6726')
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == '__main__':
    main()
