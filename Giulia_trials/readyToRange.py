# from pypozyx import PozyxSerial
# port = 'COM1' # on UNIX systems this will be '/dev/ttyACMX'
# p = PozyxSerial(port)
#
import csv

from pypozyx import (PozyxSerial, PozyxConstants, version,
                     SingleRegister, DeviceRange, POZYX_SUCCESS, POZYX_FAILURE, get_first_pozyx_serial_port)

from pypozyx.tools.version_check import perform_latest_version_check

result_file= open('results.csv', mode='w')


class ReadyToRange(object):
    """Continuously performs ranging between the Pozyx and a destination and sets their LEDs"""

    def __init__(self, pozyx, destination_id, range_step_mm=1000, protocol=PozyxConstants.RANGE_PROTOCOL_PRECISION,
                 remote_id=None):
        self.pozyx = pozyx
        self.destination_id = destination_id
        self.range_step_mm = range_step_mm
        self.remote_id = remote_id
        self.protocol = protocol

    def setup(self):
        """Sets up both the ranging and destination Pozyx's LED configuration"""
        print("------------POZYX RANGING V{} -------------".format(version))
        print("NOTES: ")
        print(" - Change the parameters: ")
        print("\tdestination_id(target device)")
        print("\trange_step(mm)")
        print("")
        print("- Approach target device to see range and")
        print("led control")
        print("")
        if self.remote_id is None:
            for device_id in [self.remote_id, self.destination_id]:
                self.pozyx.printDeviceInfo(device_id)
        else:
            for device_id in [None, self.remote_id, self.destination_id]:
                self.pozyx.printDeviceInfo(device_id)
        print("")
        print("- -----------POZYX RANGING V{} -------------".format(version))
        print("")
        print("START Ranging: ")

        # make sure the local/remote pozyx system has no control over the LEDs.
        led_config = 0x0
        self.pozyx.setLedConfig(led_config, self.remote_id)
        # do the same for the destination.
        self.pozyx.setLedConfig(led_config, self.destination_id)
        # set the ranging protocol
        self.pozyx.setRangingProtocol(self.protocol, self.remote_id)

    def loop(self):
        """Performs ranging and sets the LEDs accordingly"""
        device_range = DeviceRange()
        status = self.pozyx.doRanging(
            self.destination_id, device_range, self.remote_id)
        if status == POZYX_SUCCESS:
            print(device_range)
            t = str(device_range)
            #print("Giulia: ", t)
            t =t.replace("ms", "")
            t= t.replace("mm", "")
            t= t.replace("dBm","")
            t= t.replace(" ", "")
            #print(t)
            result_writer = csv.writer(result_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            result_writer.writerow([t])
            #result_file.close()

            if self.ledControl(device_range.distance) == POZYX_FAILURE:
                print("ERROR: setting (remote) leds")
        else:
            error_code = SingleRegister()
            status = self.pozyx.getErrorCode(error_code)
            if status == POZYX_SUCCESS:
                print("ERROR Ranging, local %s" %
                      self.pozyx.getErrorMessage(error_code))
            else:
                print("ERROR Ranging, couldn't retrieve local error")

    def ledControl(self, distance):
        """Sets LEDs according to the distance between two devices"""
        status = POZYX_SUCCESS
        ids = [self.remote_id, self.destination_id]
        # set the leds of both local/remote and destination pozyx device
        for id in ids:
            status &= self.pozyx.setLed(4, (distance < range_step_mm), id)
            status &= self.pozyx.setLed(3, (distance < 2 * range_step_mm), id)
            status &= self.pozyx.setLed(2, (distance < 3 * range_step_mm), id)
            status &= self.pozyx.setLed(1, (distance < 4 * range_step_mm), id)
        return status


if __name__ == "__main__":
    # Check for the latest PyPozyx version. Skip if this takes too long or is not needed by setting to False.
    check_pypozyx_version = True
    if check_pypozyx_version:
        perform_latest_version_check()



    # hardcoded way to assign a serial port of the Pozyx
    serial_port = 'COM11'

    # # the easier way: or "from pypozyx import *;list_serial_ports()" in terminal cdm
    #serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()

    remote_id = 0x6744 # tag  # the network ID of the remote device
    remote = True               # whether to use the given remote device for ranging l mio dispositivo
                                # in porta comunica cin il remot_id per ricevere info di sistanza tra dest_id e remote_id

    if not remote:
        remote_id = None
    destination_id = 0x6855 # network ID of the ranging destination
    # distance that separates the amount of LEDs lighting up.
    range_step_mm = 1000

    # the ranging protocol, other one is PozyxConstants.RANGE_PROTOCOL_PRECISION
    ranging_protocol = PozyxConstants.RANGE_PROTOCOL_PRECISION

    pozyx = PozyxSerial(serial_port)
    r = ReadyToRange(pozyx, destination_id, range_step_mm,
                     ranging_protocol, remote_id)
    r.setup()
    i = 0
    while i<300 :
        r.loop()
        i+=1


    # creating xls file
    print("CONVERTING IN .xlsx ...")
    from xlwt import Workbook
    import xlsxwriter

    wb = xlsxwriter.Workbook('results.xlsx')
    worksheet = wb.add_worksheet()
    old = open('results.csv', mode='r')  # csv file with results

    worksheet.write('A1', 'ms')
    worksheet.write('B1', 'mm')
    worksheet.write('C1', 'dBm')

    j = 1
    for row in old:
        row = row.replace('"', '')
        lista = row.split(",")
        i = 0
        for word in lista:
            worksheet.write(j, i, word)
            i += 1
        j += 1

    wb.close()
    old.close()


    print("PLEASE, ENTER THE CALCULATED RANGE or press D to continue with the default one (1810 mm).")
    resulted_range = input()
    if resulted_range == 'D':
        resulted_range = 1810

    # plotting the error
    print("PLOTTING THE ERROR")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    df = pd.read_excel('results.xlsx')
    range = df['mm'].tolist()

    abs_error_list = []
    error_list = []

    for element in range:
        cent = (element - resulted_range) / 10
        abs_error_list.append(abs(cent))
        error_list.append(cent)

    step = 200
    a = min(0.3, min(abs_error_list) )
    error_list = sorted(error_list)
    abs_error_list = sorted(abs_error_list)
    mean= np.mean(error_list)

    fig = plt.figure()
    plt.hist(abs_error_list, histtype='bar', label='abs values', rwidth=a+0.1,orientation='vertical', alpha=0.5)
    plt.hist(error_list, histtype='bar', color ='red', label='real values',rwidth=a+0.1, orientation='vertical', alpha=0.5)
    plt.xlabel('error (cm)')
    plt.axvline(mean, color='black', linestyle='-.', linewidth=2, label='mean error')

    plt.legend()
    # plt.xticks(np.arange(min(error_list), max(error_list), step))
    plt.ylabel('# occurrences')
    plt.grid(True, which='both')
    plt.title('error for range '+str(resulted_range/10)+' cm')
    plt.show()
    fig.savefig('./error.png')
