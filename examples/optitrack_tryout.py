from NatNetClient import NatNetClient

# This is a callback function that gets connected to the NatNet client and called once per mocap frame.
def receiveNewFrame( frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
                    labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
    print( "Received frame", frameNumber )

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receiveRigidBodyFrame( id, position, rotation ):
    print( "Received frame for rigid body", id )

# This will create a new NatNet client
streamingClient = NatNetClient()

# Configure the streaming client to call our rigid body handler on the emulator to send data out.
streamingClient.newFrameListener = receiveNewFrame
streamingClient.rigidBodyListener = receiveRigidBodyFrame

# Start up the streaming client now that the callbacks are set up.
# This will run perpetually, and operate on a separate thread.
streamingClient.run()


'''import NatNet

# create unicast client
client = NatNet.NatNetClient(1)
# connect to localhost
client.Initialize("", "")

# create and register a callback function
def onData(dataFrame):
    body = dataFrame.RigidBodies[0]
    print("x %.2f  y %.2f  z %.2f" % (body.x, body.y, body.z))

client.SetDataCallback(onData)

# wait while data frames come in
while True:
    pass

'''
'''
import optirx as rx

dsock = rx.mkdatasock()
version = (3, 0, 0, 0)  # NatNet version to use

while True:
    
    data = dsock.recv(100000)
    packet = rx.unpack(data, version=version)
    if type(packet) is rx.SenderData:
        version = packet.natnet_version
    print(packet)
    
'''
'''
import natnetclient as natnet
import time
time.sleep(2)
client = natnet.NatClient(client_ip='127.0.0.1', data_port=1511, comm_port=1510)


hand = client.rigid_bodies['rigidbody'] # Assuming a Motive Rigid Body is available that you named "Hand"
print(hand.position)
print(hand.rotation)

hand_markers = hand.markers  # returns a list of markers, each with their own properties
print(hand_markers[0].position)
'''

'''
from NatNetClient import NatNetClient
from time import time, sleep

def receiveRigidBodyList( rigidBodyList, stamp ):
    for (ac_id, pos, quat) in rigidBodyList:
        i = str(ac_id)
        if i not in id_dict.keys():
            continue

        store_track(i, pos, stamp)
        if timestamp[i] is None or abs(stamp - timestamp[i]) < period:
            if timestamp[i] is None:
                timestamp[i] = stamp
            continue # too early for next message
        timestamp[i] = stamp

        msg = PprzMessage("datalink", "REMOTE_GPS_LOCAL")
        msg['ac_id'] = id_dict[i]
        msg['pad'] = 0
        msg['enu_x'] = pos[0]
        msg['enu_y'] = pos[1]
        msg['enu_z'] = pos[2]
        vel = compute_velocity(i)
        msg['enu_xd'] = vel[0]
        msg['enu_yd'] = vel[1]
        msg['enu_zd'] = vel[2]
        msg['tow'] = int(stamp) # TODO convert to GPS itow ?
        # convert quaternion to psi euler angle
        dcm_0_0 = 1.0 - 2.0 * (quat[1] * quat[1] + quat[2] * quat[2])
        dcm_1_0 = 2.0 * (quat[0] * quat[1] - quat[3] * quat[2])
        msg['course'] = 180. * np.arctan2(dcm_1_0, dcm_0_0) / 3.14
        ivy.send(msg)

natnet = NatNetClient(
        server="127.0.0.1",
        rigidBodyListListener=receiveRigidBodyList,
        dataPort=1511,
        commandPort=1510,
        verbose=False)

print("Starting Natnet3.x to Ivy interface at 127.0.0.1")
try:
    # Start up the streaming client.
    # This will run perpetually, and operate on a separate thread.
    natnet.run()
    while True:
        sleep(1)
except (KeyboardInterrupt, SystemExit):
    print("Shutting down ivy and natnet interfaces...")
    natnet.stop()
    ivy.shutdown()
except OSError:
    print("Natnet connection error")
    natnet.stop()
    ivy.stop()
    exit(-1)
    '''
#!/usr/bin/env python3
#
# Copyright (C) 2017 Gautier Hattenberger <gautier.hattenberger@enac.fr>
#
# This file is part of paparazzi.
#
# paparazzi is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# paparazzi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with paparazzi; see the file COPYING.  If not, see
# <http://www.gnu.org/licenses/>.
#

'''
Forward rigid body position from NatNet (Optitrack positioning system)
to the IVY bus as a REMOTE_GPS_LOCAL message

As the NatNetClient is only compatible with Python 3.x, the Ivy python
should be installed for this version, eventually by hand as paparazzi
packages are only providing an install for Python 2.x (although the
source code itself is compatile for both version)

Manual installation of Ivy:
    1. git clone https://gitlab.com/ivybus/ivy-python.git
    2. cd ivy-python
    3. sudo python3 setup.py install
Otherwise, you can use PYTHONPATH if you don't want to install the code
in your system

'''

'''

import sys
from os import path, getenv
from time import time, sleep
import numpy as np
from collections import deque
import argparse

# import NatNet client
from NatNetClient import NatNetClient



# store track function
def store_track(ac_id, pos, t):
    if ac_id in id_dict.keys():
        track[ac_id].append((pos, t))
        if len(track[ac_id]) > args.vel_samples:
            track[ac_id].popleft()

# compute velocity from track
# returns zero if not enough samples
def compute_velocity(ac_id):
    vel = [ 0., 0., 0. ]
    if len(track[ac_id]) >= args.vel_samples:
        nb = -1
        for (p2, t2) in track[ac_id]:
            nb = nb + 1
            if nb == 0:
                p1 = p2
                t1 = t2
            else:
                dt = t2 - t1
                if dt < 1e-5:
                    continue
                vel[0] = (p2[0] - p1[0]) / dt
                vel[1] = (p2[1] - p1[1]) / dt
                vel[2] = (p2[2] - p1[2]) / dt
                p1 = p2
                t1 = t2
        if nb > 0:
            vel[0] / nb
            vel[1] / nb
            vel[2] / nb
    return vel


def receiveRigidBodyList( rigidBodyList, stamp ):
    for (ac_id, pos, quat) in rigidBodyList:
        i = str(ac_id)
        print("TEST")
        print(i)
        if i not in id_dict.keys():
            continue

        store_track(i, pos, stamp)
        if timestamp[i] is None or abs(stamp - timestamp[i]) < period:
            if timestamp[i] is None:
                timestamp[i] = stamp
            continue # too early for next message
        timestamp[i] = stamp

        msg = PprzMessage("datalink", "REMOTE_GPS_LOCAL")
        msg['ac_id'] = id_dict[i]
        msg['pad'] = 0
        msg['enu_x'] = pos[0]
        msg['enu_y'] = pos[1]
        msg['enu_z'] = pos[2]
        vel = compute_velocity(i)
        msg['enu_xd'] = vel[0]
        msg['enu_yd'] = vel[1]
        msg['enu_zd'] = vel[2]
        msg['tow'] = int(stamp) # TODO convert to GPS itow ?
        # convert quaternion to psi euler angle
        dcm_0_0 = 1.0 - 2.0 * (quat[1] * quat[1] + quat[2] * quat[2])
        dcm_1_0 = 2.0 * (quat[0] * quat[1] - quat[3] * quat[2])
        msg['course'] = 180. * np.arctan2(dcm_1_0, dcm_0_0) / 3.14
        ivy.send(msg)
        
# dictionary of ID associations
id_dict = dict({'ac_id':3,'rigid_id':3})

# initial time per AC
timestamp = dict([(ac_id, None) for ac_id in id_dict.keys()])
period = 1. / 100

# initial track per AC
track = dict([(ac_id, deque()) for ac_id in id_dict.keys()])

# start natnet interface
natnet = NatNetClient(
        server='127.0.0.1',
        rigidBodyListListener=receiveRigidBodyList,
        dataPort=1511,
        commandPort=1510,
        verbose=2)


try:
    # Start up the streaming client.
    # This will run perpetually, and operate on a separate thread.
    natnet.run()
    while True:
        sleep(1)
except (KeyboardInterrupt, SystemExit):
    print("Shutting down ivy and natnet interfaces...")
    natnet.stop()
    ivy.shutdown()
except OSError:
    print("Natnet connection error")
    natnet.stop()
    ivy.stop()
    exit(-1)

'''