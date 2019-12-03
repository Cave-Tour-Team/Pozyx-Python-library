#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Database script."""
# import pandas as pd
import json
import numpy as np
import datetime


class DataBase:
    """Manage test database."""

    def __init__(self):
        """Open database from file."""
        with open("tests.json", "r") as f:
            self.data = json.loads(f.read())

    def print_database(self):
        """Print database."""
        print(json.dumps(self.data, indent=2))

    def add_data_old(self, channel, bitrate, PRF, PLEN, real_distance,
                     ms_list, mm_list, dBm_list, notes, datetime):
        """Add data to database."""
        avg_mm = np.mean(mm_list)
        errors = [real_distance - x for x in mm_list]
        total_time = max(ms_list) - min(ms_list)
        new_data = {
            "channel": channel,
            "bitrate": bitrate,
            "PRF": PRF,
            "PLEN": PLEN,
            "ms": mm_list,
            "mm": ms_list,
            "dBm": dBm_list,
            "real_distance": real_distance,
            "errors": errors,
            "avg_distance": avg_mm,
            "mm_error": np.mean(errors),
            "total_time": total_time,
            "notes": notes,
            "datetime": datetime
            }
        self.data["data"].append(new_data)

    def add_data(self, channel, bitrate, PRF, PLEN, real_distance,
                 ms_list, mm_list, dBm_list, notes, datetime):
        """Add data to database."""
        avg_mm = np.mean(mm_list)
        errors = [x - real_distance for x in mm_list]
        measurements = [{
            "mm": mm,
            "ms": ms,
            "dBm": dBm,
            "mm_err": mm - real_distance
        } for mm, ms, dBm in zip(mm_list, ms_list, dBm_list)]
        total_time = max(ms_list) - min(ms_list)
        new_data = {
            "channel": channel,
            "bitrate": bitrate,
            "PRF": PRF,
            "PLEN": PLEN,
            "mm_real": real_distance,
            "mm_mean": avg_mm,
            "mm_err_mean": np.mean(errors),
            "ms_total": total_time,
            "notes": notes,
            "datetime": datetime,
            "measurements": measurements
            }
        self.data["data"].append(new_data)

    def save_data(self):
        """Save data to file."""
        with open("tests.json", "w") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def clear_database(self):
        """Empty database."""
        self.data = {
            "data": []
        }

    def delete_data(self, channel, bitrate, PRF, PLEN):
        """Delete entry based on parameters."""
        cnt = 0
        for el in self.data["data"]:
            if ((el["channel"] == channel) and (el["bitrate"] == bitrate) and
               (el["PRF"] == PRF) and (el["PLEN"] == PLEN)):
                del self.data["data"][cnt]
                print("Deleted entry %d!" % cnt)
                return 1
            cnt += 1
        print("No entry deleted!")
        return -1


def main():
    """Run some examples."""
    db = DataBase()
    # db.print_database()
    # db.clear_database()
    date = datetime.datetime.now()
    mm_list = [np.random.randint(950, 1150) for x in range(100)]
    ms_list = [x for x in range(100)]
    dBm_list = [np.random.randint(-83, -78) for x in range(100)]
    db.add_data(channel=4, bitrate=210, PRF=0, PLEN=0, real_distance=1000,
                ms_list=ms_list, mm_list=mm_list, dBm_list=dBm_list,
                notes="Fake data.", datetime=date.isoformat())
    # db.print_database()
    # db.delete_data(7, 210, 0, 0)
    db.clear_database()
    db.save_data()


if __name__ == '__main__':
    main()
    print("""---END---""")
