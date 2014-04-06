"""Raspberry Pi Camera Script

Uses picamera library to take pictures from the Raspberry Pi Camera
Outputs results to a stream

"""

import json
import os
import picamera
import io
import socket
import struct
import time
import sys, getopt

#constants
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

#general
server_address = '127.0.0.1'
server_port = 8000

#command line arguments
try:
    opts, args = getopt.getopt(sys.argv,"hs:p:x:y:",["server=","port=","width=","height="])
except getopt.GetoptError:
    print 'improper use of arguments'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print 'picamera.py: -s/--server for server address, -p/--port for port,\n   -x/--width for CAMERA_EIDTH, -x/--height for CAMERA_HEIGHT'
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
while True:
    with picamera.PiCamera() as camera:
        camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
        #start preview and warm up camera for a second
        camera.start_preview()
        time.sleep(1)
        
        #start recording and end on user input to stop
        start = time.time()
        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream, 'jpeg'):
            # Write the length of the capture to the stream and flush to
            # ensure it actually gets sent
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            # Rewind the stream and send the image data over the wire
            stream.seek(0)
            connection.write(stream.read())
            # If we've been capturing for more than 30 seconds, quit
            if time.time() - start > 30:
                break
            # Reset the stream for the next capture
            stream.seek(0)
            stream.truncate()
    # Write a length of zero to the stream to signal we're done
    connection.write(struct.pack('<L', 0))
#finally:
    #close socket connections
connection.close()
client_socket.close()