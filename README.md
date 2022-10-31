# ema8314

This repository provides a Python library to communicate with the EMA8314R ethernet I/O module for temperature measurement applications.

Most of the functionality provided by the device is implemented in theory though the Watch Dog Timer is untested and there may be some bugs or unwanted/unintended behavior in some of the functions, though the main temperature measurement functions and the limits should all work.

Along with the library itself, an example logging script (logging.py) is provided as a means to showcase what can be done. This but scratches the surface of the functionality of the device and grew out of a need to log temperatures myself, so perhaps there are better ways to do things.
