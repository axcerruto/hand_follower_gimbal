#!/usr/bin/env python3
# Created by Antonio X Cerruto 24 Feb 2022
import cv2
from sight import Sight
from gimbal import Gimbal
import serialport
from time import sleep
import numpy as np
import multiprocessing
import subprocess
import threading
import sys
import pickle
import os
from os.path import exists

def update_arr(arr, newval):
    newarr = arr.copy()
    newarr.insert(0,newval)
    del newarr[-1]
    return newarr

def bound_angle(x):
  if(x >= 180): return 180
  elif(x <= 0): return 0
  else: return x

def kill_sight():
  subprocess.run("kill $(ps -ax | grep sight.py | awk '{print $1}' | sed \$d)", shell=True) # kill previously spawned processes

def start_sight():
  filename_sight = 'sight.log'
  if(exists(filename_sight)): os.remove(filename_sight)

  kill_sight()
  result = subprocess.Popen(['python3', 'sight.py']) # this one doesn't block
  while(not exists(filename_sight)):
    pass
  return open(filename_sight,'r')


def main():
  ser = serialport.port_setup()
  gimbal = Gimbal()
  t_write = gimbal._timestamp_()
  t_read = gimbal._timestamp_()
  s_read = gimbal._timestamp_()
  t_start = gimbal._timestamp_()
  t_led_status = gimbal._timestamp_()
  target_y_arr = [90]*3
  target_y = int(np.mean(target_y_arr))
  target_p_arr = [90]*3
  target_p = int(np.mean(target_p_arr))
  led_status = 0
  new_target_y = 90
  new_target_p = 90
  write_y = 90
  write_p = 90
  center_theta_yaw = 90
  center_theta_pitch = 90
  last_line = ''

  # multiprocessing (option 1)
  # multiprocessing.set_start_method('spawn')
  # d = multiprocessing.Process(target=s.run_continuously(), daemon=False).start() # this blocks

  # threading (option 2)
  # result = threading.Thread(target=s.run_continuously()).start().join(timeout=0) # this blocks

  # subprocess (option 3)
  # result = subprocess.run(['python3', 'sight.py']) # this blocks
  # result = subprocess.Popen(['python3', sys.argv[0], s.run_continuously()]) # this one blocks
  # result = subprocess.Popen(['python3', 'sight.py'], stdout=subprocess.PIPE) # this one doesn't block
  file_sight = start_sight()

  while True:
    # update center angle from background process 'sight.py'
    if(gimbal._timestamp_()-s_read > 30):
      line = file_sight.readline()
      if(line != ''):
        line = line.split(',')
        led_status = int(line[0])
        center_theta_yaw = int(line[1])
        center_theta_pitch = int(line[2])
        x = int(line[3])
        y = int(line[4])
        z = int(line[5])
        gimbal.update_coordinates(x, y, z)
        new_target_y = (center_theta_yaw-90)+gimbal.curr_yaw
        new_target_y = bound_angle(new_target_y)
        new_target_p = (center_theta_pitch-90)+gimbal.curr_pitch
        new_target_p = bound_angle(new_target_p)
        last_line = line

        # start timer if no hands found
        if(led_status == 1):
          t_led_status = gimbal._timestamp_()

        # update yaw target angle
        target_y_arr = update_arr(target_y_arr, new_target_y)
        target_y = int(np.mean(target_y_arr))
        if(abs(target_y - gimbal.curr_yaw) >= 5):
          write_y = target_y

        # update pitch target angle
        target_p_arr = update_arr(target_p_arr, new_target_p)
        target_p = int(np.mean(target_p_arr))
        if(abs(target_p - gimbal.curr_pitch) >= 5):
          write_p = target_p
      s_read=gimbal._timestamp_()

    # read gimbal position
    if(gimbal._timestamp_()-t_read > 2):
      gimbal.read_gimbal(ser)
      # print(f'time: {gimbal._timestamp_()-t_start}, target: {target_y}, wrote: {write_y}, current: {gimbal.curr_yaw}, center: {center_theta}')
      t_read=gimbal._timestamp_()

    # send updated target angle to motor
    if(gimbal._timestamp_()-t_write > 35):
      gimbal.update_led_status(ser, led_status)
      gimbal.update_angles(target_p, write_y)
      gimbal.move_gimbal(ser)
      t_write=gimbal._timestamp_()

    # reset motors if no hand has been found for a long time
    # if(gimbal._timestamp_()-t_led_status > 10000):
    #   kill_sight()
    #   for x in target_y_arr:
    #     target_y_arr = update_arr(target_y_arr, 90)
    #   target_y = int(np.mean(target_y_arr))
    #   write_y = target_y
    #   file_sight = start_sight()
    #   t_led_status = gimbal._timestamp_()



if __name__ == "__main__":
  # execute only if run as a script
  main()
    
