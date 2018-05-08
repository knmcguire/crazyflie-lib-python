#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import sys
import time
import math
import numpy


import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils.multi_ranger import MultiRanger

URI = 'radio://0/80/250K'

if len(sys.argv) > 1:
    URI = sys.argv[1]

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


def logicIsCloseTo(real_value = 0.0, checked_value =0.0, margin=0.05):
    
    if real_value> checked_value-margin and real_value< checked_value+margin:
        return True 
    else:
        return False

def is_close(range):
    MIN_DISTANCE = 0.2  # m

    if range is None:
        return False
    else:
        return range < MIN_DISTANCE
    
if __name__ == '__main__':
    
    distance_from_wall = 0.3
    state = "wall_following"
    print state
    beta = numpy.deg2rad(90)
    yaw_rate = 0.0
    speed = 0.05
    already_turned = False
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    cf = Crazyflie(rw_cache='./cache')
    with SyncCrazyflie(URI, cf=cf) as scf:
        with MotionCommander(scf) as motion_commander:
            with MultiRanger(scf) as multi_ranger:
                keep_flying = True
                
                
                while keep_flying:
                    
                    #motion_commander._set_vel_setpoint(0,0,0,5)

                    '''
                    if state == "wall_following":
                        if (multi_ranger.front>multi_ranger.right):
                            motion_commander._set_vel_setpoint(0,0,0,10)
                        else:
                            motion_commander._set_vel_setpoint(0,0,0,-10)
                    '''   
                            
                    #print('right', multi_ranger.right)
                    #print multi_ranger.front
                    #print beta
                    
                    #handle state transitions
                    
                    if state=='wall_following':
                        if multi_ranger.front > 1.0 or multi_ranger.front is None:
                            already_turned = False
                            state = 'rotate_around_corner'
                            print state
                    elif state == 'rotate_around_corner':
                        if multi_ranger.front < 0.7 and multi_ranger.front is not None:
                            state = 'rotate_to_align_wall'
                            print state

                    elif state=='rotate_to_align_wall': 
                        if multi_ranger.right is not None and multi_ranger.front is not None:
                            if logicIsCloseTo(multi_ranger.right,multi_ranger.front, 0.1):
                                state ='wall_following'
                                print state

                    
                        
                    
                    
                    if state == 'wall_following':
                        true_distance_from_wall = distance_from_wall
                        if multi_ranger.right is not None and multi_ranger.front is not None:
                            # Calculate real distance to wall
                            true_distance_from_wall=(multi_ranger.right*multi_ranger.front*math.sin(beta))/math.sqrt(math.pow(multi_ranger.right,2)+math.pow(multi_ranger.front,2)-2*multi_ranger.right*multi_ranger.front*math.cos(beta))
                        # If drone is at the right distance, only rotate yaw
                        if logicIsCloseTo(true_distance_from_wall,distance_from_wall,0.1):
                            if multi_ranger.right is not None and multi_ranger.front is not None:
                                if logicIsCloseTo(multi_ranger.front,multi_ranger.right,0.05):
                                    motion_commander._set_vel_setpoint(speed,speed,0,0)                          
                                else:
                                    if (multi_ranger.front>multi_ranger.right):
                                        motion_commander._set_vel_setpoint(speed,speed,0,10)
                                    else:
                                        motion_commander._set_vel_setpoint(speed,speed,0,-10)
                            else:
                                motion_commander._set_vel_setpoint(0,0,0,0)
                        # if drone is away from distance, move            
                        else:
                            if true_distance_from_wall > distance_from_wall :
                                motion_commander._set_vel_setpoint(0.1,0,0,0)
                            else:
                                motion_commander._set_vel_setpoint(0,0.1,0,0)
                    if state == 'rotate_around_corner':
                        if already_turned == False:
                            motion_commander.move_distance(0.18,0.18,0,0.05)
                            already_turned = True
                        #motion_commander.turn_right(90,20)
                        #motion_commander.move_distance(0.18,0.18,0,0.05)
                        print 'check'

                        #motion_commander.goforward(speed,speed,0,0)
                        #time.sleep(2)
                        yaw_rate = numpy.rad2deg(0.02/distance_from_wall+0.1);
                        motion_commander._set_vel_setpoint(speed,speed,0,15)
                        #motion_commander._set_vel_setpoint(0,0,0,0)

                    if state == 'rotate_to_align_wall':
                        if multi_ranger.right is not None and multi_ranger.front is not None:
                            if (multi_ranger.front>multi_ranger.right):
                                motion_commander._set_vel_setpoint(0.00,0.00,0,10)
                            else:
                                motion_commander._set_vel_setpoint(0.00,0.00,0,-10)
                        else:
                            motion_commander._set_vel_setpoint(0,0,0,0)
                                   
                            
                    time.sleep(0.1)

                 
                    
                    if is_close(multi_ranger.up):
                        keep_flying = False
    

    
    
                motion_commander.stop()

    
                print('Demo terminated!')
