# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2017 Bitcraze AB
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
from crazyflie_driver.msg._Position import Position
"""
This script shows the basic use of the MotionCommander class.

Simple example that connects to the crazyflie at `URI` and runs a
sequence. This script requires some kind of location system, it has been
tested with (and designed for) the flow deck.

Change the URI variable to your Crazyflie configuration.
"""
import logging
import time
import readchar


import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from NatNetClient import NatNetClient
from cflib.crazyflie.log import LogConfig

from cflib.crazyflie.syncLogger import SyncLogger

pos = []
check = 0
def receiveNewFrame( frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
                    labeledMarkerCount, latency, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
    check = 1
    #print( "Received frame", frameNumber )

def receiveRigidBodyFrame( id, position, rotation ):
    global pos
    if id == 1:
        pos = position
        #print( "Received frame for rigid body", id )

print(pos)

streamingClient = NatNetClient()

streamingClient.newFrameListener = receiveNewFrame

streamingClient.rigidBodyListener = receiveRigidBodyFrame

streamingClient.run()

    
URI = 'radio://0/80/250K'

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    cf = Crazyflie(rw_cache='./cache')
    
    
    lg_states = LogConfig(name='kalman_states', period_in_ms=10)
    lg_states.add_variable('kalman_states.ox')
    lg_states.add_variable('kalman_states.oy')

    with SyncCrazyflie(URI, cf=cf) as scf:
        with SyncLogger(scf, lg_states) as logger_states:
            with MotionCommander(scf) as motion_commander:
                keep_flying = True
                char = readchar.readchar()
                motion_commander.up(0.5)
                time.sleep(1)

    
                while(keep_flying):
                    if len(pos)>0:
                        cf.extpos.send_extpos(pos[0],pos[1],pos[2])
                        #print("external",pos[1])
                    time.sleep(0.1)
                    for log_entry_1 in logger_states:
                        data = log_entry_1[1]
                        #print("estimate", float(data["kalman_states.oy"]))
                        break
                    if char == "q":
                        keep_flying = False


                motion_commander.stop()

    
                print('Demo terminated!')      
       