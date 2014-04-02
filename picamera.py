"""Raspberry Pi Camera Script

Uses picamera library to take pictures from the Raspberry Pi Camera
Outputs results to a stream

"""

import json
import os
import picamera
import socket
import time
import sys, getopt

#constants
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

#general
server_address = '127.0.0.1'
server_port = 8000
continue_recording = True

#command line arguments
try:
    opts, args = getopt.getopt(argv,"hs:x:y:",["server=","width=","height="])
except getopt.GetoptError:
    print 'improper use of arguments'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print 'picamera.py: -x/--width for CAMERA_EIDTH, -x/--height for CAMERA_HEIGHT'
        sys.exit()
    #server address
    elif opt in ("-s", "--server"):
        server_address = arg
    elif opt in ("-p", "--port"):
        server_port = int(arg)
    #adjust camera resolution
    elif opt in ("-x", "--width"):
        CAMERA_WIDTH = int(arg)
    elif opt in ("-y", "--height"):
        CAMERA_HEIGHT = int(arg)

#connect a client socket to server
client_socket = socket.socket()
client_socket.connect((server_address, server_port))

#file object to be sent over connection
connection = client_socket.makefile('wb')
try:
    with picamera.PiCamera() as camera:
        camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
        #start preview and warm up camera for a second
        camera.start_preview()
        time.sleep(1)
        #start recording and end on user input to stop
        camera.start_recording(connection, format='h264')
        raw_input('Press Enter to Stop')
        camera.stop_recording()
finally:
    #close socket connections
    connection.close()
    client_socket.close()