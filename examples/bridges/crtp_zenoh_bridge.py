# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2014 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
Simple example that connects to the first Crazyflie found, logs the 
roll pitch yaw and sends it over as a zenoh publication. 
"""
import logging
import time
from threading import Timer

import cflib.crtp  # noqa
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.utils import uri_helper

import zenoh

uri = uri_helper.uri_from_env(default='usb://0')

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

class CrtpZenohBridge:

    def __init__(self, link_uri):

        # initialize Zenoh session
        zenoh.init_logger()
        self._zenoh_session = zenoh.open(zenoh.Config())
        self.pub = self._zenoh_session.declare_publisher("cf/logging")

        # Initialization Crazyflie connection callbacks
        self._cf = Crazyflie(rw_cache='./cache')
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)
        print('Connecting to %s' % link_uri)
        self._cf.open_link(link_uri)
        self.is_connected = True

    def _zenoh_cb_start_logging(self, query):
        print(f">> [Queryable ] Received Query '{query.selector}'" + (f" with value: {query.value.payload}" if query.value is not None else ""))
        query.reply(zenoh.Sample("cf/start_logging", 'Success!'))
        self._lg_bat.start()

    def _zenoh_cb_stop_logging(self, query):
        print(f">> [Queryable ] Received Query '{query.selector}'" + (f" with value: {query.value.payload}" if query.value is not None else ""))
        query.reply(zenoh.Sample("cf/stop_logging", 'Success!'))
        self._lg_bat.stop()

    def _connected(self, link_uri):
        print('Connected to %s' % link_uri)
        self._lg_bat= LogConfig(name='battery', period_in_ms=100)
        self._lg_bat.add_variable('pm.vbat', 'FP16')

        try:
            self._cf.log.add_config(self._lg_bat)
            self._lg_bat.data_received_cb.add_callback(self._stab_log_data)
            self._lg_bat.error_cb.add_callback(self._stab_log_error)
            self.quaryable_start_logging = self._zenoh_session.declare_queryable("cf/start_logging", self._zenoh_cb_start_logging, False)
            self.quaryable_stop_logging = self._zenoh_session.declare_queryable("cf/stop_logging", self._zenoh_cb_stop_logging, False)

        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')

    def _stab_log_error(self, logconf, msg):
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        buf = f'[{timestamp}][{logconf.name}]: '
        for name, value in data.items():
            buf += f'{name}: {value:3.3f} '
        print(buf)

        # Publish to zenoh
        self.pub.put(buf)

    def _connection_failed(self, link_uri, msg):
        print('Connection to %s failed: %s' % (link_uri, msg))
        self.is_connected = False

    def _connection_lost(self, link_uri, msg):
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        print('Disconnected from %s' % link_uri)
        self.is_connected = False
        self.pub.undeclare()
        self.quaryable_start_logging.undeclare()
        self.quaryable_stop_logging.undeclare()
        self._zenoh_session.close()


if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    le = CrtpZenohBridge(uri)

    print("Enter 'q' to quit...")

    try:
        while le.is_connected:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        le._cf.close_link()

    
