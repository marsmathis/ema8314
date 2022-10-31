#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# This file is part of the EMA8314 repository (https://github.com/marsmathis/ema8314).
# Copyright 2022 Mathis Reuß-Hennschen.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Logging script for EMA-8314R ethernet I/O module.
"""

import ema8314 as e
import time
import signal
import sys
from loguru import logger


# =========================================================================== #
# User-changeable variables
# --------------------------------------------------------------------------- #
# IP addresses and ports
OWN_IP = "192.168.1.x"
OWN_PORT = 17120
REMOTE_IP = "192.168.1.y"
REMOTE_PORT = 6936
# --------------------------------------------------------------------------- #
# set logging time interval (in seconds)
INTERVAL = 1
# --------------------------------------------------------------------------- #
# set the separator symbol for the log file
SEPARATOR = "\t"
# --------------------------------------------------------------------------- #
# change every line to True that should get included in the log file
# temperature measurement per channel
ALL_TEMP = True
TEMP_0 = True
TEMP_1 = True
TEMP_2 = True
TEMP_3 = True

# sensor status per channel (sensor present or not)
ALL_SENSOR = False
SENSOR_0 = False
SENSOR_1 = False
SENSOR_2 = False
SENSOR_3 = False

# output status per channel (output on or off)
ALL_OUTPUT = False
OUTPUT_0 = False
OUTPUT_1 = False
OUTPUT_2 = False
OUTPUT_3 = False
# =========================================================================== #

_INCLUDE_ARRAY = ( (TEMP_0,
                    TEMP_1,
                    TEMP_2,
                    TEMP_3),
                   (SENSOR_0,
                    SENSOR_1,
                    SENSOR_2,
                    SENSOR_3),
                   (OUTPUT_0,
                    OUTPUT_1,
                    OUTPUT_2,
                    OUTPUT_3) )
# =========================================================================== #

e.init(OWN_IP, OWN_PORT, REMOTE_IP, REMOTE_PORT)
connected = True

logger.add("log_{time:YYYY-MM-DD}.log",rotation="0:00",format="{time:YYYY-MM-DDTHH:mm:ssZ}{message}")

def string():
    """
    Build the string that gets written to the log file.

    Returns
    -------
    string : str
        String that gets written to the log file.

    """
    string = ""
    sensors = e.all_sensor_status_read()
    for sensor in range(len(sensors[0])):
        if _INCLUDE_ARRAY[0][sensor] == True or ALL_TEMP == True:
            if sensors[0][sensor] == 0:
                string = string + SEPARATOR + str(e.channel_temperature_read(sensor)[0][0])
            else:
                string = string + SEPARATOR + "NaN"

        if _INCLUDE_ARRAY[1][sensor] == True or ALL_SENSOR == True:
            sensor_status = "connected" if e.all_sensor_status_read()[0][sensor] == 0 else "disconnected"
            string = string + SEPARATOR + sensor_status

        if _INCLUDE_ARRAY[2][sensor] == True or ALL_OUTPUT == True:
            output_status = "on" if e.output_read()[0][sensor] == 0 else "off"
            string = string + SEPARATOR + output_status
    
    return string

def run():
    """
    Main loop that only gets interrupted by SIGINT (keyboard interrupt/CTRL+C).

    Returns
    -------
    None.

    """
    while True:
        try:
            log_string = string()
            time.sleep(INTERVAL)
            logger.info(log_string)
        except :
            connected = False
            while not connected:
                try:
                    e.firmware_version_read()
                    connected = True
                except:
                    print("waiting...")
                    time.sleep(2)

def signal_handler(signal, frame):
    """
    Handle SIGINT (keyboard interrupt) and exit cleanly by closing open socket
    and killing the logger so the open file gets released.

    Parameters
    ----------
    signal : int
        Signal number.
    frame : int
        Interrupted stack frame.

    Returns
    -------
    None.

    """
    e.close_socket()
    print("socket closed")
    logger.remove()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    run()
