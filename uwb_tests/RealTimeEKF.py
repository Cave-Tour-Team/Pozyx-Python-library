#!/usr/bin/env python3
"""
The Pozyx ready to localize tutorial (c) Pozyx Labs
Please read the tutorial that accompanies this sketch:
https://www.pozyx.io/Documentation/Tutorials/ready_to_localize/Python

This tutorial requires at least the contents of the Pozyx Ready to Localize
kit. It demonstrates the positioning capabilities of the Pozyx device both
locally and remotely. Follow the steps to correctly set up your environment in
the link, change the parameters and upload this sketch. Watch the coordinates
change as you move your device around!
"""
# from time import sleep
from time import time
# import math
from pypozyx import *
from pypozyx.definitions.bitmasks import POZYX_INT_MASK_IMU
from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.udp_client import SimpleUDPClient
import csv
import datetime
# import numpy as np
from numpy import *
# from numpy.linalg import inv, det
# import pylab
# import matplotlib.pyplot as plt
# import serial

# devices = []


class PosRangeOrientation(object):
    """Call Pozyx positioning function.

    Continuously call the Pozyx positioning function and prints its
    position.
    """

    def __init__(self, pozyx, osc_udp_client, anchors, algorithm, protocol,
                 dimension, height, remote_id):
        """Initialise."""
        self.pozyx = pozyx
        self.height = height
        self.anchors = anchors
        self.protocol = protocol
        self.dimension = dimension
        self.algorithm = algorithm
        self.remote_id = remote_id
        self.osc_udp_client = osc_udp_client

    def setup(self):
        """Sets up the Pozyx for positioning by calibrating its anchor list."""
        print("------------POZYX POSITIONING V1.0 --------------")
        print()
        print("START Ranging: ")
        self.pozyx.clearDevices(self.remote_id)
        self.setAnchorsManual()
        self.printPublishConfigurationResult()
        self.pozyx.setRangingProtocol(self.protocol, self.remote_id)

        """There is no specific setup functionality"""
        self.current_time = time()

    def loop(self):
        """Get new IMU sensor data."""

        sensor_data = SensorData()
        calibration_status = SingleRegister()
        """Performs positioning and displays/exports the results."""
        position = Coordinates()  # Initialize variable
        init_time = time()
        RanData = self.Ranging()
        status = self.pozyx.doPositioning(position, self.dimension,
                                          self.height, self.algorithm,
                                          remote_id=self.remote_id)

        if (self.remote_id is not None) or (self.pozyx.checkForFlag(POZYX_INT_MASK_IMU, 0.01) == POZYX_SUCCESS):
            status = self.pozyx.getAllSensorData(sensor_data, self.remote_id)
            status &= self.pozyx.getCalibrationStatus(calibration_status, self.remote_id)

        if status == POZYX_SUCCESS:
            self.publishSensorData(sensor_data, calibration_status)
            status = self.pozyx.doPositioning(position, self.dimension,
                                              self.height, self.algorithm,
                                              remote_id=self.remote_id)
            timestamp = time()
            acq_time = timestamp - init_time

        if status == POZYX_SUCCESS:
            RanPosIMUData = self.printPosRanIMUData(position, RanData,
                                                    sensor_data, round(acq_time, 6),
                                                    round(timestamp, 6))
            return RanPosIMUData
        else:
            self.printPublishErrorCode("positioning")



    def Ranging(self):
        """Perform ranging."""
        RanData = []
        for index in range(len(devices)):
            device_range = DeviceRange()
            destination_id = devices[index]
            status = self.pozyx.doRanging(destination_id, device_range,
                                          self.remote_id)
            if status == POZYX_SUCCESS:
                RanData.append(float(device_range.distance))
                RanData.append(float(device_range.RSS))
            else:
                print("ERROR: ranging")
                RanData.append(0)
                RanData.append(0)
        return RanData

    def publishSensorData(self, sensor_data, calibration_status):
        """Makes the OSC sensor data package and publishes it"""
        self.msg_builder = OscMessageBuilder("/sensordata")
        self.msg_builder.add_arg(int(1000 * (time() - self.current_time)))
        current_time = time()
        self.addSensorData(sensor_data)
        self.addCalibrationStatus(calibration_status)

    def printPosRanIMUData(self, position, RanData, sensor_data, acq_time, timestamp):
        """Print the Pozyx's position and possibly send it as a OSC packet."""
        network_id = self.remote_id
        RanPosData = []
        pos = position
        acc = sensor_data.acceleration
        MF = sensor_data.magnetic
        EA = sensor_data.euler_angles
        # P = sensor_data.pressure
        # Temp = sensor_data.temperature
        gyro = sensor_data.angular_vel

        if network_id is None:
            network_id = 0
        print("POS ID {}, x(mm): {pos.x} y(mm): {pos.y} z(mm): {pos.z}".format(
            "0x%0.4x" % network_id, pos=position))
        if self.osc_udp_client is not None:
            self.osc_udp_client.send_message("/position", [network_id,
                                                           int(position.x),
                                                           int(position.y),
                                                           int(position.z)])
        global PosData
        TimeData = [timestamp, acq_time]
        PosData = [pos.x, pos.y, pos.z]
        SenData = [acc.x/1000, acc.y/1000, acc.z/1000,
                   gyro.x, gyro.y, gyro.z,
                   MF.x/100, MF.y/100, MF.z/100,
                   # P,
                   EA.roll, EA.pitch, EA.heading]
                   # Temp]
        RanPosIMUData = TimeData + PosData + RanData + SenData
        return RanPosIMUData

    def printPublishErrorCode(self, operation):
        """Prints the Pozyx's error and possibly sends it as a OSC packet"""
        error_code = SingleRegister()
        network_id = self.remote_id
        if network_id is None:
            self.pozyx.getErrorCode(error_code)
            print("ERROR %s, local error code %s" % (operation,
                                                     str(error_code)))
            if self.osc_udp_client is not None:
                self.osc_udp_client.send_message("/error", [operation, 0,
                                                            error_code[0]])
            return
        status = self.pozyx.getErrorCode(error_code, self.remote_id)
        if status == POZYX_SUCCESS:
            print("ERROR %s on ID %s, error code %s" %
                  (operation, "0x%0.4x" % network_id, str(error_code)))
            if self.osc_udp_client is not None:
                self.osc_udp_client.send_message(
                    "/error", [operation, network_id, error_code[0]])
        else:
            self.pozyx.getErrorCode(error_code)
            print("ERROR %s, couldn't retrieve remote error code, local error code %s" %
                  (operation, str(error_code)))
            if self.osc_udp_client is not None:
                self.osc_udp_client.send_message("/error", [operation, 0, -1])
            # should only happen when not being able to communicate with a remote Pozyx.

    def addSensorData(self, sensor_data):
        """Adds the sensor data to the OSC message"""
        # self.msg_builder.add_arg(sensor_data.pressure)


        self.addComponentsOSC(sensor_data.acceleration)
        self.addComponentsOSC(sensor_data.magnetic)
        self.addComponentsOSC(sensor_data.angular_vel)
        self.addComponentsOSC(sensor_data.euler_angles)

        # self.addComponentsOSC(sensor_data.quaternion)

        self.addComponentsOSC(sensor_data.linear_acceleration)
        self.addComponentsOSC(sensor_data.gravity_vector)
        # self.addComponentsOSC(sensor_data.pressure)

    def addComponentsOSC(self, component):
        """Adds a sensor data component to the OSC message"""
        for data in component.data:
            self.msg_builder.add_arg(float(data))

    def addCalibrationStatus(self, calibration_status):
        """Adds the calibration status data to the OSC message"""
        self.msg_builder.add_arg(calibration_status[0] & 0x03)
        self.msg_builder.add_arg((calibration_status[0] & 0x0C) >> 2)
        self.msg_builder.add_arg((calibration_status[0] & 0x30) >> 4)
        self.msg_builder.add_arg((calibration_status[0] & 0xC0) >> 6)

    def setAnchorsManual(self):
        """Adds the manually measured anchors to the Pozyx's device list one for one."""
        status = self.pozyx.clearDevices(self.remote_id)
        for anchor in self.anchors:
            status &= self.pozyx.addDevice(anchor, self.remote_id)
        if len(anchors) > 1:
            status &= self.pozyx.setSelectionOfAnchors(POZYX_ANCHOR_SEL_AUTO,
                                                       len(anchors))
        return status

    def printPublishConfigurationResult(self):
        """Prints and potentially publishes the anchor configuration result in a human-readable way."""
        list_size = SingleRegister()

        status = self.pozyx.getDeviceListSize(list_size, self.remote_id)
        print("List size: {0}".format(list_size[0]))
        if list_size[0] != len(self.anchors):
            self.printPublishErrorCode("configuration")
            return

        device_list = DeviceList(list_size=list_size[0])
        status = self.pozyx.getDeviceIds(device_list, self.remote_id)
        print("Calibration result:")
        print("Anchors found: {0}".format(list_size[0]))
        print("Anchor IDs: ", device_list)
        global devices
        devices = device_list

        for i in range(list_size[0]):
            anchor_coordinates = Coordinates()
            status = self.pozyx.getDeviceCoordinates(
                device_list[i], anchor_coordinates, self.remote_id)
            print("ANCHOR,0x%0.4x, %s" % (device_list[i],
                                          str(anchor_coordinates)))
            if self.osc_udp_client is not None:
                self.osc_udp_client.send_message(
                    "/anchor", [device_list[i], int(anchor_coordinates.x),
                                int(anchor_coordinates.y),
                                int(anchor_coordinates.z)])
                sleep(0.025)

    def printPublishAnchorConfiguration(self):
        """Prints and potentially publishes the anchor configuration"""
        for anchor in self.anchors:
            print("ANCHOR,0x%0.4x,%s" % (anchor.network_id,
                                         str(anchor.coordinates)))
            if self.osc_udp_client is not None:
                self.osc_udp_client.send_message("/anchor", [anchor.network_id,
                                                 int(anchor_coordinates.x),
                                                 int(anchor_coordinates.y),
                                                 int(anchor_coordinates.z)])
                sleep(0.025)


if __name__ == "__main__":
    # shortcut to not have to find out the port yourself
    serial_port = get_serial_ports()[0].device

    remote_id = 0x6741                # remote device network ID
    remote = True             # whether to use a remote device
    if not remote:
        remote_id = None

    print()
    use_processing = False          # enable to send position data through OSC
    ip = "127.0.0.1"                # IP for the OSC UDP
    network_port = 8888             # network port for the OSC UDP
    osc_udp_client = None
    dt = datetime.datetime.now()
    ranging_protocol = POZYX_RANGE_PROTOCOL_PRECISION  # the ranging protocol

    if use_processing:
        osc_udp_client = SimpleUDPClient(ip, network_port)
    # necessary data for calibration, change the IDs and coordinates yourself
    false_x = 394500
    false_y = 4990800
    false_z = 300
    anchors = [DeviceCoordinates(0x617e, 1, Coordinates(int((394541.63780-false_x)*1000), int((4990886.425448-false_y)*1000), int((306.11862-false_z)*1000))),
               DeviceCoordinates(0x6119, 1, Coordinates(int((394535.87380-false_x)*1000), int((4990875.13956-false_y)*1000), int((305.94624-false_z)*1000))),
               DeviceCoordinates(0x6735, 1, Coordinates(int((394546.46551-false_x)*1000), int((4990883.86831-false_y)*1000), int((305.78802-false_z)*1000))),
               DeviceCoordinates(0x6726, 1, Coordinates(int((394541.79053-false_x)*1000), int((4990871.96470-false_y)*1000), int((305.84900-false_z)*1000))),

               # DeviceCoordinates(0x672d, 1, Coordinates()),
               # DeviceCoordinates(0x686a, 1, Coordinates()),
               # DeviceCoordinates(0x6765, 1, Coordinates()),
               # DeviceCoordinates(0x616c, 1, Coordinates()),

               # P9
               DeviceCoordinates(0x6840, 1, Coordinates(int((394554.71364-false_x)*1000), int((4990875.21233-false_y)*1000), int((303.81908-false_z)*1000))),

               # P 10
               DeviceCoordinates(0x617c, 1, Coordinates(int((394551.31736-false_x)*1000), int((4990868.81968-false_y)*1000), int((303.80426-false_z)*1000)))]

    # algorithm = POZYX_POS_ALG_UWB_ONLY  # positioning algorithm to use
    algorithm = POZYX_POS_ALG_TRACKING  # positioning algorithm to use IMU + UWB

    dimension = POZYX_3D                # positioning dimension
    height = 1000            # height of device, required in 2.5D positioning

    pozyx = PozyxSerial(serial_port)
    r = PosRangeOrientation(pozyx, osc_udp_client, anchors, algorithm,
                            ranging_protocol, dimension, height, remote_id)
    r.setup()
    with open(dt.strftime('Pos_%H-%M-%Y.%m.%d.csv'), "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
#       Start_Time = ['Start Time of session :', r.UTC_IT(chck=1)]
        Start_Time = ['Start Time of session :',
                      dt.strftime("%H-%M-%S. %f - %Y.%m.%d")]

        header = ['Timestamp', 'DT', 'posX[mm]', 'posY[mm]', 'posZ[mm]', 'RangeA[mm]',
                  'PowerA[dbm]', 'RangeB[mm]', 'PowerB[dbm]', 'RangeC[mm]',
                  'PowerC[dbm]', 'RangeD[mm]', 'PowerD[dbm]', 'RangeE[mm]',
                  'PowerE[dbm]', 'RangeF[mm]', 'PowerF[dbm]', 'AccX[g]',
                  'AccY[g]', 'AccZ[g]', 'GyroX[deg/sec]', 'GyroY[deg/sec]',
                  'GyroZ[deg/sec]', 'MagX[G]', 'MagY[G]', 'MagZ[G]',
                  'Roll', 'Pitch', 'Heading']

        writer.writerow(Start_Time)
        writer.writerow(" ")
        writer.writerow(header)
        while True:
            try:
                Sen = r.loop()
                print(Sen)
                if Sen is not None:
                    # pass
                    writer.writerow(Sen)
                else:
                    pass
            except KeyboardInterrupt:
                break
