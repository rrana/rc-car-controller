"""Robot Controller Script

Retrieve camera information from attached sensors
Communicates through sockets with a websocket server
Applies OpenCV algorithms through video stills
Streams video and OpenCV results through the socket
Receives robot commands from socket

"""

import os
import json
import io
import time
import picamera
import cv2
import numpy as np
import serial
import glob

#constants: read from JSON file in the future
C = {
    'camera_width': 320,
    'camera_height': 240,
}

#sockets
client_socket = socket.socket()
#client_socket.connect(('my_server', 8000))

#ai
#manual control is now directly handled by the node.js server
ai_mode = '';
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#general
run_loop = True
robot_status = {}
user_commands = ''

def process_user_command():
    if user_commands:
        pass

def ai_step(im):
    #Generate desired heading and direction given a robot mode
    if robot_mode == 'lines':
        robot_status = detect_line(im)
    elif robot_mode == 'face':
        robot_status = detect_face(im)
    
    if robot_status:
        pass

def detect_line(im):
    gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,150,200,apertureSize = 3)
    
    #adjust HoughLine properties
    lines = cv2.HoughLinesP(edges,1,np.pi/100,50)
    if lines != None:
        for line in lines[0]:
            #print rho
            #print theta
            print line
            pt1 = (line[0],line[1])
            pt2 = (line[2],line[3])
            cv2.line(im, pt1, pt2, (0,0,255), 3)
    print '-----'

def detect_face(im):
    robot_status ['General'] = 'No face found'
    gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        cv2.rectangle(im,(x,y),(x+w,y+h),(255,0,0),2)
        print "({0}, {1}) {2}x{3}".format(x,y,w,h)
        robot_status ['General'] = 'Face found'
        robot_status ['Face Center X'] = 'X: ' + str(x + w/2)
        robot_status ['Face Center Y'] = 'Y: ' + str(y + h/2)
        robot_status ['Face Off Center'] = str(x + w/2 - 400/2)
        
        if robot_status ['Face Off Center'] < -5:
            ser.write('R')  # Right
            robot_status ['Direction'] = 'Right'
        elif robot_status ['Face Off Center'] > 5:
            ser.write('L')  # Left
            robot_status ['Direction'] = 'Left'
    print '-----'

#Streaming through picamera, so initialize outside loop
with picamera.PiCamera() as camera:
    camera.resolution = (C['camera_width'], C['camera_height'])
    stream = picamera.PiCameraCircularIO(camera, seconds=10)
    camera.start_recording(stream, format='h264')
    #camera.start_preview()
    try:
        while run_loop:
            robot_status = {}
            if ai_mode:
                camera.capture(stream, format='jpeg', use_video_port=True)
                # Construct a numpy array from the stream
                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                im = cv2.imdecode(data, 1)
                
                ai_step (im)
        
