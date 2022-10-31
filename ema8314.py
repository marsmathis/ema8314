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
Library for EMA-8314 ethernet I/O module.
"""

import struct
import socket

__author__ = "Mathis Reuß-Hennschen"
__copyright__ = "Copyright 2022 Mathis Reuß-Hennschen"
__license__ = "GPL"
__version__ = "1.0"


# =========================================================================== #
# Example file structure:
# --------------------------------------------------------------------------- #
# import ema8314 as e
#
# e.setup("12345678")
# e.init("xxx.xxx.xxx.xxx", xxxxx,      "xxx.xxx.xxx.xxx",  xxxxx         )
#        own IP             own socket  remote IP           remote socket
# 
# [various EMA functions to measure temperatures etc.]
# e.close_socket()
# 
# =========================================================================== #
# Note
# --------------------------------------------------------------------------- #
# Sometimes the UDP socket or the Python implementation appears to be choking
# up when trying to receive a reply to a request in SOCK.recvfrom(). A solu-
# tion that appears to be stable is:
#
# import ema8314 as e
# import time
# 
# e.init(...)
# connected = True
# 
# try:
#     [EMA function]
# except:
#     connected = False
#     try:
#         e.firmware_version_read()
#         connected = True
#     except:
#         print("waiting...")
#         time.sleep(2)
# 
# for some reason this works
# =========================================================================== #

# initializing variables

_CARDID = "EMA8314"
HOSTIP = 0
HOSTPORT = 0
TARGETIP = 0
TARGETPORT = 0
PASSWORD = "12345678"
SOCK = 0


# =========================================================================== #
# starting and closing functions
# =========================================================================== #

def init(host_ip,
         host_port,
         target_ip,
         target_port,
         password=PASSWORD):
    """
    Create the socket. [MANDATORY]

    Parameters
    ----------
    host_ip : str
        Normal IPv4 format – four groups of digits divided with a dot.
    host_port : int
        From 0 to 65535.
    target_ip : str
        Normal IPv4 format – four groups of digits divided with a dot.
    target_port : int
        From 1024 to 65535.
    password : str [optional; if empty: default password "12345678"]
        Up to 8 ASCII bytes.

    Returns
    -------
    None.

    """
    global SOCK

    # socket creation
    SOCK = socket.socket(family=socket.AF_INET,
                         type=socket.SOCK_DGRAM)
    SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    SOCK.settimeout(5)

    # socket bind
    SOCK.bind((host_ip, host_port))

    global HOSTIP
    global HOSTPORT
    global TARGETIP
    global TARGETPORT
    global PASSWORD

    HOSTIP = host_ip
    HOSTPORT = host_port
    TARGETIP = target_ip
    TARGETPORT = target_port
    PASSWORD = password


def close_socket():
    """
    Close the socket.

    Returns
    -------
    None.

    """
    SOCK.close()


# =========================================================================== #
# configuration functions
# =========================================================================== #

def reboot_device():
    """
    Reboot the device.

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x02

    bytes_to_send = struct.pack("7s8sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x02", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def change_socket_port(new_socket_port):
    """
    Change the socket port.

    Parameters
    ----------
    new_socket_port : int
        From 0 to 65535.

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x03

    bytes_to_send = struct.pack("7s8sc2s",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x03", "utf8"),
                                new_socket_port.to_bytes(2, "little"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def password_change(new_password):
    """
    Change the password.

    Parameters
    ----------
    new_password : str
        Up to 8 ASCII bytes.

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x04

    bytes_to_send = struct.pack("7s8sc8s",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x04", "utf8"),
                                bytes(new_password, "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def password_set_default():
    """
    Set the password back to default.

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x05

    bytes_to_send = struct.pack("7s8sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x05", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def change_ip(new_ip):
    """
    Change the IP.

    Parameters
    ----------
    new_ip : str
        Normal IPv4 format – four groups of digits divided with a dot.

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x06

    split_ip = [0, 0, 0, 0]

    for i in range(0, 4):
        split_ip[i] = int(new_ip.split(".")[i]).to_bytes(1, "big")

    bytes_to_send = struct.pack("7s8sccccc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x06", "utf8"),
                                split_ip[0], split_ip[1], split_ip[2], split_ip[3])

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def firmware_version_read():
    """
    Read the firmware version.

    Returns
    -------
    result : tuple
        str | 'x.y' (x is the main version number, y is the subversion number. Example: 1.0)
    flag : char
        99 (0x63) when successful.

    """
    # 0x07

    bytes_to_send = struct.pack("7s8sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x07", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xccxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = (str(ord(parsed[0])) + "." + str(ord(parsed[1])),)
    flag = msg[0][-2]

    return (result, flag)


# =========================================================================== #
# output functions
# =========================================================================== #

def output_set(output0,
               output1,
               output2,
               output3):
    """
    Set output status; only for general purpose output, not for control.

    Parameters
    ----------
    output0 : int
        Output status OUT0 (0 [inactive] / 1 [active]).
    output1 : int
        Output status OUT1 (0 [inactive] / 1 [active]).
    output2 : int
        Output status OUT2 (0 [inactive] / 1 [active]).
    output3 : int
        Output status OUT3 (0 [inactive] / 1 [active]).

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x30

    output = (1 * output0) | (2 * output1) | (4 * output2) | (8 * output3)

    bytes_to_send = struct.pack("7s8sccc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x30", "utf8"),
                                bytes("\x00", "utf8"),
                                output.to_bytes(1, "big"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def output_read():
    """
    Read the output status.

    Returns
    -------
    result : tuple
        int | Output status OUT0 (0 [inactive] / 1 [active]). \n
        int | Output status OUT1 (0 [inactive] / 1 [active]). \n
        int | Output status OUT2 (0 [inactive] / 1 [active]). \n
        int | Output status OUT3 (0 [inactive] / 1 [active]).
    flag : char
        99 (0x63) when successful.

    """
    # 0x31

    bytes_to_send = struct.pack("7s8sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x31", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xcxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = (ord(parsed[0]) & 1,
              (ord(parsed[0]) & 2) >> 1,
              (ord(parsed[0]) & 4) >> 2,
              (ord(parsed[0]) & 8) >> 3)

    flag = msg[0][-2]

    return (result, flag)


def output_mode_set(output_mode0,
                    output_mode1,
                    output_mode2,
                    output_mode3):
    """
    Set the output mode.

    Parameters
    ----------
    output_mode0 : int
        Output mode OUT0 (0 [general purpose] / 1 [temperature control]).
    output_mode1 : int
        Output mode OUT1 (0 [general purpose] / 1 [temperature control]).
    output_mode2 : int
        Output mode OUT2 (0 [general purpose] / 1 [temperature control]).
    output_mode3 : int
        Output mode OUT3 (0 [general purpose] / 1 [temperature control]).

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x32

    output = (1 * output_mode0) | (2 * output_mode1) | \
             (4 * output_mode2) | (8 * output_mode3)

    bytes_to_send = struct.pack("7s8sccc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x30", "utf8"),
                                bytes("\x00", "utf8"),
                                output.to_bytes(1, "big"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def output_mode_read():
    """
    Read the output mode.

    Returns
    -------
    result : tuple
        int | Output mode OUT0 (0 [general purpose] / 1 [temperature control]). \n
        int | Output mode OUT1 (0 [general purpose] / 1 [temperature control]). \n
        int | Output mode OUT2 (0 [general purpose] / 1 [temperature control]). \n
        int | Output mode OUT3 (0 [general purpose] / 1 [temperature control]).
    flag : char
        99 (0x63) when successful.

    """
    # 0x33

    bytes_to_send = struct.pack("7s8sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x33", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xcxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = (ord(parsed[0]) & 1,
              (ord(parsed[0]) & 2) >> 1,
              (ord(parsed[0]) & 4) >> 2,
              (ord(parsed[0]) & 8) >> 3)

    flag = msg[0][-2]

    return (result, flag)


# =========================================================================== #
# Analog measurement functions
# =========================================================================== #

def channel_temperature_read(channel):
    """
    Read the temperature and unit from one channel.

    Parameters
    ----------
    channel : int
        Channel to read from (0 / 1 / 2 / 3).

    Returns
    -------
    result : tuple
        float | Measured temperature. \n
        str | Temperature unit ('C' / 'F').
    flag : char
        99 (0x63) when successful.

    """
    # 0x50

    bytes_to_send = struct.pack("7s8sccccc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x50", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                channel.to_bytes(1, "big"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxfxxxxxxxxxxxxcxxxxxxxxxxxxx", msg[0])

    if parsed[1] == b'\x01':
        unit = "C"

    if parsed[1] == b'\x02':
        unit = "F"

    result = (parsed[0], unit)

    flag = msg[0][-2]

    return (result, flag)


def all_temperature_read():
    """
    Read the temperature and unit from all channels.

    Returns
    -------
    result : tuple
        float | Measured temperature channel 0. \n
        str | Temperature unit channel 0 ('C' / 'F'). \n
        float | Measured temperature channel 1. \n
        str | Temperature unit channel 1 ('C' / 'F'). \n
        float | Measured temperature channel 2. \n
        str | Temperature unit channel 2 ('C' / 'F'). \n
        float | Measured temperature channel 3. \n
        str | Temperature unit channel 3 ('C' / 'F').
    flag : char
        99 (0x63) when successful.

    """
    # 0x51

    bytes_to_send = struct.pack("7s8sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x51", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    unit = [0, 0, 0, 0]

    parsed = struct.unpack("xxxxffffccccxxxxxxxxxx", msg[0])
    for i in range(4, 8):
        if parsed[i] == b'\x01':
            unit[i-4] = "C"

        if parsed[i] == b'\x02':
            unit[i-4] = "F"

    result = (parsed[0], unit[0],
              parsed[1], unit[1],
              parsed[2], unit[2],
              parsed[3], unit[3])

    flag = msg[0][-2]

    return (result, flag)


# =========================================================================== #
# parameter functions
# =========================================================================== #

def channel_temperature_limit_set(channel,
                                  temperature_low,
                                  temperature_high,
                                  temperature_unit):
    """
    Set temperature limits for one channel.

    Parameters
    ----------
    channel : int
        Channel to set (0 / 1 / 2 / 3).
    temperature_low : float
        Low temperature threshold.
    temperature_high : float
        High temperature threshold.
    temperature_unit : str
        Temperature unit ('C' / 'F').

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x52

    if temperature_unit == "C":
        unit = b'\x01'

    if temperature_unit == "F":
        unit = b'\x02'

    bytes_to_send = struct.pack("7s8scccccffccccccccc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x52", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                channel.to_bytes(1, "big"),
                                temperature_low,
                                temperature_high,
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                unit)

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def channel_temperature_limit_read(channel):
    """
    Read temperature limits from one channel.

    Parameters
    ----------
    channel : int
        Channel to read from (0 / 1 / 2 / 3).

    Returns
    -------
    result : tuple
        float | Low temperature threshold. \n
        float | High temperature threshold. \n
        str | Temperature unit ('C' / 'F').
    flag : char
        99 (0x63) when successful.

    """
    # 0x53

    bytes_to_send = struct.pack("7s8sccccc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x53", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                channel.to_bytes(1, "big"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxffxxxxxxxxcxxxxxxxxxxxxx", msg[0])

    if parsed[2] == b'\x01':
        unit = "C"

    if parsed[2] == b'\x02':
        unit = "F"

    result = (parsed[0], parsed[1], unit)

    flag = msg[0][-2]

    return (result, flag)


def all_temperature_limit_set(temperature_low0,
                              temperature_high0,
                              temperature_unit0,
                              temperature_low1,
                              temperature_high1,
                              temperature_unit1,
                              temperature_low2,
                              temperature_high2,
                              temperature_unit2,
                              temperature_low3,
                              temperature_high3,
                              temperature_unit3):
    """
    Set temperature limits for all channels.

    Parameters
    ----------
    temperature_low0 : float
        Low temperature threshold channel 0.
    temperature_high0 : float
        High temperature threshold channel 0.
    temperature_unit0 : str
        Temperature unit channel 0 ('C' / 'F').
    temperature_low1 : float
        Low temperature threshold channel 1.
    temperature_high1 : float
        High temperature threshold channel 1.
    temperature_unit1 : str
        Temperature unit channel 1 ('C' / 'F').
    temperature_low2 : float
        Low temperature threshold channel 2.
    temperature_high2 : float
        High temperature threshold channel 2.
    temperature_unit2 : str
        Temperature unit channel 2 ('C' / 'F').
    temperature_low3 : float
        Low temperature threshold channel 3.
    temperature_high3 : float
        High temperature threshold channel 3.
    temperature_unit3 : str
        Temperature unit channel 3 ('C' / 'F').

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x54

    temp_units = (temperature_unit0,
                  temperature_unit1,
                  temperature_unit2,
                  temperature_unit3)

    temps_low = (temperature_low0,
                 temperature_low1,
                 temperature_low2,
                 temperature_low3)

    temps_high = (temperature_high0,
                 temperature_high1,
                 temperature_high2,
                 temperature_high3)

    unit = [0, 0, 0, 0]
    for i in range(4):
        if temp_units[i] == "C":
            unit[i] = b'\x01'

        if temp_units[i] == "F":
            unit[i] = b'\x02'

    parsed = [0, 0]

    for i in range(2):

        bytes_to_send = struct.pack("7s8scccccffffcc",
                                    bytes(_CARDID, "utf8"),
                                    bytes(PASSWORD, "utf8"),
                                    bytes("\x54", "utf8"),
                                    bytes("\x00", "utf8"),
                                    i.to_bytes(1, "big"),
                                    bytes("\x00", "utf8"),
                                    i.to_bytes(1, "big"),
                                    temps_low[2*i],
                                    temps_high[2*i],
                                    temps_low[2*i+1],
                                    temps_high[2*i+1],
                                    unit[2*i],
                                    unit[2*i+1])

        SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

        msg = SOCK.recvfrom(34)

        parsed.append(struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0]))

    result = (parsed[0] + parsed[1])

    flag = msg[0][-2]

    return (result, flag)


def all_temperature_limit_read():
    """
    Read temperature limits from all channels.

    Returns
    -------
    result : tuple
        float | Low temperature threshold channel 0. \n
        float | High temperature threshold channel 0. \n
        str | Temperature unit channel 0 ('C' / 'F'). \n
        float | Low temperature threshold channel 1. \n
        float | High temperature threshold channel 1. \n
        str | Temperature unit channel 1 ('C' / 'F'). \n
        float | Low temperature threshold channel 2. \n
        float | High temperature threshold channel 2. \n
        str | Temperature unit channel 2 ('C' / 'F'). \n
        float | Low temperature threshold channel 3. \n
        float | High temperature threshold channel 3. \n
        str | Temperature unit channel 3 ('C' / 'F').
    flag : char
        99 (0x63) when successful.

    """
    # 0x55

    bytes_to_send = struct.pack("7s8sccccc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x55", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed1 = struct.unpack("xxxxffffccxxxxxxxxxxxx", msg[0])

    bytes_to_send = struct.pack("7s8sccccc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x55", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x01", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x01", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed2 = struct.unpack("xxxxffffccxxxxxxxxxxxx", msg[0])

    temp_units = (
        parsed1[4],
        parsed1[5],
        parsed2[4],
        parsed2[5])

    unit = [0, 0, 0, 0]
    for i in range(0, 4):
        if temp_units[i] == b'\x01':
            unit[i] = "C"

        if temp_units[i] == b'\x02':
            unit[i] = "F"

    result = (parsed1[0], parsed1[1], unit[0],
              parsed1[2], parsed1[3], unit[1],
              parsed2[0], parsed2[1], unit[2],
              parsed2[2], parsed2[3], unit[3])

    flag = msg[0][-2]

    return (result, flag)


def channel_sensor_type_set(channel,
                            sensor_type):
    """
    Set sensor type for one channel.

    Parameters
    ----------
    channel : int
        Channel to set (0 / 1 / 2 / 3).
    sensor_type : str
        Sensor type ('Pt-1000' / 'Pt-100').

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x56

    if sensor_type == "Pt-1000":
        sensor = b'\x01'

    if sensor_type == "Pt-100":
        sensor = b'\x02'

    bytes_to_send = struct.pack("7s8sccccc16sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x56", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                channel.to_bytes(1, "big"),
                                bytes("\x00\x00\x00\x00 \
                                     \x00\x00\x00\x00 \
                                     \x00\x00\x00\x00 \
                                     \x00\x00\x00\x00", "utf-8"),
                                sensor)

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def channel_sensor_type_read(channel):
    """
    Read sensor type from one channel.

    Parameters
    ----------
    channel : int
        Channel to read from (0 / 1 / 2 / 3).

    Returns
    -------
    result : tuple
        str | Sensor type ('Pt-1000' / 'Pt-100').
    flag : char
        99 (0x63) when successful.

    """
    # 0x57

    bytes_to_send = struct.pack("7s8sccccc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x57", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                bytes("\x00", "utf8"),
                                channel.to_bytes(1, "big"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxcxxxxxxxxxxxxx", msg[0])

    sensor = 0

    print(msg[0])

    if parsed[0] == b'\x01':
        sensor = "Pt-1000"

    if parsed[0] == b'\x02':
        sensor = "Pt-100"

    result = (sensor,)

    flag = msg[0][-2]

    return (result, flag)


def all_sensor_type_set(sensor_type0,
                        sensor_type1,
                        sensor_type2,
                        sensor_type3):
    """
    Set sensor type for all channels.

    Parameters
    ----------
    sensor_type0 : str
        Sensor type channel 0 ('Pt-1000' / 'Pt-100').
    sensor_type1 : str
        Sensor type channel 1 ('Pt-1000' / 'Pt-100').
    sensor_type2 : str
        Sensor type channel 2 ('Pt-1000' / 'Pt-100').
    sensor_type3 : str
        Sensor type channel 3 ('Pt-1000' / 'Pt-100').

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x58

    sensor_types = (sensor_type0,
                    sensor_type1,
                    sensor_type2,
                    sensor_type3)

    sensor = [0, 0, 0, 0]

    for i in range(0, 4):
        if sensor_types[i] == "Pt-1000":
            sensor[i] = b'\x01'

        if sensor_types[i] == "Pt-100":
            sensor[i] = b'\x02'

    bytes_to_send = struct.pack("7s8sccccc16scccc",
                              bytes(_CARDID, "utf8"),
                              bytes(PASSWORD, "utf8"),
                              bytes("\x58", "utf8"),
                              bytes("\x00", "utf8"),
                              bytes("\x00", "utf8"),
                              bytes("\x00", "utf8"),
                              bytes("\x00", "utf8"),
                              bytes("\x00\x00\x00\x00 \
                                     \x00\x00\x00\x00 \
                                     \x00\x00\x00\x00 \
                                     \x00\x00\x00\x00", "utf-8"),
                              sensor[0],
                              sensor[1],
                              sensor[2],
                              sensor[3])

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def all_sensor_type_read():
    """
    Read sensor type from all channels.

    Returns
    -------
    result : tuple
        str | Sensor type channel 0 ('Pt-1000' / 'Pt-100'). \n
        str | Sensor type channel 1 ('Pt-1000' / 'Pt-100'). \n
        str | Sensor type channel 2 ('Pt-1000' / 'Pt-100'). \n
        str | Sensor type channel 3 ('Pt-1000' / 'Pt-100').
    flag : char
        99 (0x63) when successful.

    """
    # 0x59

    bytes_to_send = struct.pack("7s8sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x59", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxccccxxxxxxxxxx", msg[0])

    sensor = [0, 0, 0, 0]

    for i in range(0, 4):
        if parsed[i] == b'\x01':
            sensor[i] = "Pt-1000"

        if parsed[i] == b'\x02':
            sensor[i] = "Pt-100"

    result = (sensor[0],
              sensor[1],
              sensor[2],
              sensor[3])

    flag = msg[0][-2]

    return (result, flag)


def all_sensor_status_read():
    """
    Read sensor status from all channels.

    Returns
    -------
    result : tuple
        int | Sensor status channel 0 (0 [normal] / 1 [broken]). \n
        int | Sensor status channel 1 (0 [normal] / 1 [broken]). \n
        int | Sensor status channel 2 (0 [normal] / 1 [broken]). \n
        int | Sensor status channel 3 (0 [normal] / 1 [broken]). \n
    flag : char
        99 (0x63) when successful.

    """
    # 0x5A

    bytes_to_send = struct.pack("7s8sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x5A", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxcxxxxxxxxx", msg[0])

    result = (ord(parsed[0]) & 1,
              (ord(parsed[0]) & 2) >> 1,
              (ord(parsed[0]) & 4) >> 2,
              (ord(parsed[0]) & 8) >> 3)

    flag = msg[0][-2]

    return (result, flag)


# =========================================================================== #
# comparison functions
# =========================================================================== #


def control_status_read():
    """
    Read the temperature comparison status.

    Returns
    -------
    result : tuple
        int | Temperature comparison status (0 [disabled] / 1 [enabled]).
    flag : char
        99 (0x63) when successful.

    """
    # 0x5B

    bytes_to_send = struct.pack("7s8sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x5B", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxcxxxxxxxxx", msg[0])

    result = (ord(parsed[0]) - 1,)

    flag = msg[0][-2]

    return (result, flag)


def control_enable():
    """
    Enable temperature comparison.

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x5C

    bytes_to_send = struct.pack("7s8sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x5C", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def control_disable():
    """
    Disable temperature comparison.

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x5D

    bytes_to_send = struct.pack("7s8sc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x5D", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def control_mask_set(control_mask0,
                     control_mask1,
                     control_mask2,
                     control_mask3):
    """
    Set the control mask. (?)

    Parameters
    ----------
    control_mask0 : int
        Control mask channel 0 (0 [unmask] / 1 [masked]).
    control_mask1 : int
        Control mask channel 1 (0 [unmask] / 1 [masked]).
    control_mask2 : int
        Control mask channel 2 (0 [unmask] / 1 [masked]).
    control_mask3 : int
        Control mask channel 3 (0 [unmask] / 1 [masked]).

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x5E

    control_mask = (1 * control_mask0) | (2 * control_mask1) | \
                   (4 * control_mask2) | (8 * control_mask3)

    bytes_to_send = struct.pack("7s8sccc",
                              bytes(_CARDID, "utf8"),
                              bytes(PASSWORD, "utf8"),
                              bytes("\x5E", "utf8"),
                              bytes("\x00", "utf8"),
                              control_mask.to_bytes(1, "big"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def control_mask_read():
    """
    Read the control mask. (?)

    Returns
    -------
    result : tuple
        int | Control mask channel 0 (0 [unmask] / 1 [masked]). \n
        int | Control mask channel 1 (0 [unmask] / 1 [masked]). \n
        int | Control mask channel 2 (0 [unmask] / 1 [masked]). \n
        int | Control mask channel 3 (0 [unmask] / 1 [masked]).
    flag : char
        99 (0x63) when successful.

    """
    # 0x5F

    bytes_to_send = struct.pack("7s8sc",
                              bytes(_CARDID, "utf8"),
                              bytes(PASSWORD, "utf8"),
                              bytes("\x5F", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xcxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = (ord(parsed[0]) & 1,
              (ord(parsed[0]) & 2) >> 1,
              (ord(parsed[0]) & 4) >> 2,
              (ord(parsed[0]) & 8) >> 3)

    flag = msg[0][-2]

    return (result, flag)


def wdt_enable():
    """
    Enable the watch dog timer.

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x60

    bytes_to_send = struct.pack("7s8sc",
                              bytes(_CARDID, "utf8"),
                              bytes(PASSWORD, "utf8"),
                              bytes("\x60", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def wdt_disable():
    """
    Disable the watch dog timer.

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x61

    bytes_to_send = struct.pack("7s8sc",
                              bytes(_CARDID, "utf8"),
                              bytes(PASSWORD, "utf8"),
                              bytes("\x61", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def wdt_set(output_status0,
            output_status1,
            output_status2,
            output_status3,
            wait_time):
    """
    Set the watch dog timer configuration.

    Parameters
    ----------
    outputStatus0 : int
        Output status channel 0 (0 [disabled] / 1 [enabled]).
    outputStatus1 : int
        Output status channel 1 (0 [disabled] / 1 [enabled]).
    outputStatus2 : int
        Output status channel 2 (0 [disabled] / 1 [enabled]).
    outputStatus3 : int
        Output status channel 3 (0 [disabled] / 1 [enabled]).
    waitTime : float
        Wait time (10 - 10000 [time in 0.1 s]).

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x62

    output_status = (1 * output_status0) | (2 * output_status1) | \
                   (4 * output_status2) | (8 * output_status3)

    bytes_to_send = struct.pack("7s8schc",
                              bytes(_CARDID, "utf8"),
                              bytes(PASSWORD, "utf8"),
                              bytes("\x62", "utf8"),
                              wait_time,
                              output_status.to_bytes(1, "big"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def wdt_read():
    """
    Read watch dog timer configuration.

    Returns
    -------
    result : tuple
        int | Output status channel 0 (0 [disabled] / 1 [enabled]). \n
        int | Output status channel 1 (0 [disabled] / 1 [enabled]). \n
        int | Output status channel 2 (0 [disabled] / 1 [enabled]). \n
        int | Output status channel 3 (0 [disabled] / 1 [enabled]). \n
        float | Wait time (10 - 10000 [time in 0.1 s]). \n
        int | Watch dog status (0 [disabled] / 1 [enabled]).
    flag : char
        99 (0x63) when successful.

    """
    # 0x63

    bytes_to_send = struct.pack("7s8sc",
                              bytes(_CARDID, "utf8"),
                              bytes(PASSWORD, "utf8"),
                              bytes("\x63", "utf8"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("hccxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    outputs = (ord(parsed[1]) & 1,
               (ord(parsed[1]) & 2) >> 1,
               (ord(parsed[1]) & 4) >> 2,
               (ord(parsed[1]) & 8) >> 3)

    result = (outputs[0],
              outputs[1],
              outputs[2],
              outputs[3],
              parsed[0],
              ord(parsed[2]) - 1)

    flag = msg[0][-2]

    return (result, flag)


def control_mode_set(channel, mode):
    """
    Set the control mode for one channel; channel 0 controls OUT0, channel 1 controls OUT1, channel 2 controls OUT2, channel 3 controls OUT3.

    Parameters
    ----------
    channel : int
        Channel to read from (0 / 1 / 2 / 3).
    mode : int
        Control mode \n
            (0 [Over high temperature threshold ON, under low temperature theshold OFF] \n
            1 [Over high temperature threshold OFF, under low temperature threshold ON] \n
            2 [Within high temperature threshold and low temperature threshold ON else OFF] \n
            3 [Within high temperature threshold and low temperature threshold OFF else ON]).

    Returns
    -------
    result : tuple
        Empty.
    flag : char
        99 (0x63) when successful.

    """
    # 0x64

    bytes_to_send = struct.pack("7s8scccc",
                              bytes(_CARDID, "utf8"),
                              bytes(PASSWORD, "utf8"),
                              bytes("\x64", "utf8"),
                              bytes("\x00", "utf8"),
                              channel.to_bytes(1, "big"),
                              mode.to_bytes(1, "big"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = parsed

    flag = msg[0][-2]

    return (result, flag)


def control_mode_read(channel):
    """
    Read the control mode for one channel.

    Parameters
    ----------
    channel : int
        Channel to read from (0 / 1 / 2 / 3).

    Returns
    -------
    result : tuple
        int | Control mode \n
            (0 [Over high temperature threshold ON, under low temperature theshold OFF] \n
            1 [Over high temperature threshold OFF, under low temperature threshold ON] \n
            2 [Within high temperature threshold and low temperature threshold ON else OFF] \n
            3 [Within high temperature threshold and low temperature threshold OFF else ON]).
    flag : char
        99 (0x63) when successful.

    """
    # 0x65

    bytes_to_send = struct.pack("7s8sccc",
                                bytes(_CARDID, "utf8"),
                                bytes(PASSWORD, "utf8"),
                                bytes("\x65", "utf8"),
                                bytes("\x00", "utf8"),
                                channel.to_bytes(1, "big"))

    SOCK.sendto(bytes_to_send, (TARGETIP, TARGETPORT))

    msg = SOCK.recvfrom(34)

    parsed = struct.unpack("xxcxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", msg[0])

    result = (ord(parsed[0]),)

    flag = msg[0][-2]

    return (result, flag)

if __name__ == "__main__":
    print("This is not a standalone program; import it as a module!")
