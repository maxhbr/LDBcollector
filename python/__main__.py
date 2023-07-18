#!/usr/bin/env python3

import logging 

from setup import init_license_db
from setup import license_info

logging.basicConfig(level=logging.DEBUG)
init_license_db(check=True)

gpl2 = license_info()

