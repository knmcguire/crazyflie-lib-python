# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2016 Bitcraze AB
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
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.
"""
Simple example that connects to the first Crazyflie found, logs the Stabilizer
and prints it to the console. After 10s the application disconnects and exits.

This example utilizes the SyncCrazyflie and SyncLogger classes.
"""
import logging
import time
import math

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.motion_commander import MotionCommander

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)
URI = 'radio://0/40/250K'


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # Scan for Crazyflies and use the first one found

    '''
    lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')
    '''    
    lg_states = LogConfig(name='kalman_states', period_in_ms=10)
    lg_states.add_variable('kalman_states.vx')
    lg_states.add_variable('kalman_states.vy')
    lg_states.add_variable('stereoboard.velocity x')
    lg_states.add_variable('stereoboard.velocity z')
    lg_states.add_variable('motion.deltaX')
    lg_states.add_variable('motion.deltaY')
    lg_states.add_variable('range.zrange')

    fh = open("log_test.txt", "w")


    cf = Crazyflie(rw_cache='./cache')
    with SyncCrazyflie(URI, cf=cf) as scf:
        with SyncLogger(scf, lg_states) as logger_states:
      #  with MotionCommander(scf) as mc:
            time.sleep(1)



            #mc.start_left(velocity=0.)
            
            endTime = time.time() + 2


            for log_entry_1 in logger_states:
            #while 1:
                timestamp = log_entry_1[0]
                data = log_entry_1[1]
                logconf_name = log_entry_1[2]
                
                vx = float(data["motion.deltaX"])/100#float(data["range.zrange"])*math.tan(float(data["motion.deltaX"])*2.10/30.0)/0.01
                vy = float(data["motion.deltaX"])/100#float(data["range.zrange"])*math.tan(float(data["motion.deltaY"])*2.10/30.0)/0.01


                fh.write("%f, %f,  %f, %f, %f, %f, %f \n"% (time.time(),float(data["stereoboard.velocity x"])/100,  float(data["stereoboard.velocity z"])/100, vx,vy,  float(data["kalman_states.vx"]),float(data["kalman_states.vy"])  ))
                
                if time.time() > endTime:
                    break

        
           # mc.stop()

