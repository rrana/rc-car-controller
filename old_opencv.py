"""
TEMPORARY placeholder for camera opencv python script
to be deleted once opencv.py is confirmed to work
--
Robot OpenCV and Controller Script

Retrieve camera information from stream
Communicates through sockets with a websocket server
Applies OpenCV algorithms through video stills
OpenCV results through the socket
Receives robot commands from socket

"""

import os
import json
import io
import datetime
import time
import picamera
import cv2
import numpy as np
import serial
import glob
from socketIO_client import SocketIO

#constants: read from JSON file in the future
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

#ai
#manual control is now directly handled by the node.js server
ai_mode = '';
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier('cascade_files/lbpcascade_frontalface.xml')

#general
run_loop = True
stream = io.BytesIO()
robot_status = {}
user_commands = []
after_image = '';

def log(text):
    print text

def ai_step(raw_image):
    #Generate desired heading and direction given a robot mode
    if ai_mode == 'red':
        robot_status = detect_red(raw_image)
    elif ai_mode == 'face':
        robot_status = detect_face(raw_image)
    
    if robot_status:
        pass

def detect_red(raw_image):
    #convert to HSV
    hsv = cv2.cvtColor(raw_image, cv2.COLOR_BGR2HSV)
    
    #http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html
    lower_red = np.array([60,50,50])
    upper_red = np.array([60,255,255])
    
    mask = cv2.inRange(hsv, lower_red, upper_red)

def detect_face(raw_image):
    robot_status ['General'] = 'No face found'
    after_image = raw_image
    gray = cv2.cvtColor(raw_image,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        after_image = cv2.rectangle(after_image,(x,y),(x+w,y+h),(255,0,0),2)
        
        offCenter = x + w/2 - CAMERA_WIDTH/2
        log("({0}, {1}) {2}x{3}".format(x,y,w,h))
        log('Off Center: ' + str(offCenter))
        robot_status ['General'] = 'Face found'
        robot_status ['Face Center X'] = 'X: ' + str(x + w/2)
        robot_status ['Face Center Y'] = 'Y: ' + str(y + h/2)
        robot_status ['Face Off Center'] = str(offCenter)
        
        if offCenter < -40:
            user_commands.append('manual-turn-left')
            robot_status ['Direction'] = 'Left'
        elif offCenter > 40:
            user_commands.append('manual-turn-right')
            robot_status ['Direction'] = 'Right'
        else:
            user_commands.append('manual-turn-neutral')
            robot_status ['Direction'] = 'Neutral'
        
        #Adjust acceleration based on face box width
        if w < 90:
            user_commands.append('manual-throttle-forward')
            robot_status ['Movement'] = 'Forward'
        elif w > 100:
            user_commands.append('manual-throttle-reverse')
            robot_status ['Movement'] = 'Reverse'
        else:
            user_commands.append('manual-throttle-stop')
            robot_status ['Movement'] = 'None'

def update_ai(data):
    log('--- Implementing ---')
    log(data['command'])
    if data['command'] == 'face-start':
        ai_mode = 'face'
    elif data['command'] == 'red-start':
        ai_mode = 'red'
    #ai-stop
    else:
        ai_mode = ''
#Communicate through socket.io
with SocketIO('http://localhost', 80) as socketIO:
    #socketIO.on('robot ai', update_ai)
    ai_mode='face'
    #Streaming through picamera, so initialize outside loop
    with picamera.PiCamera() as camera:
        camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
        camera.start_recording(stream, format='h264')
        camera.start_preview()
        try:
            while run_loop:
                user_commands = []
                robot_status = {'Timestamp': str(datetime.datetime.now())}
                robot_status ['Has Camera'] = True

                camera.capture('public/camera_shot.jpg', format='jpeg', use_video_port=True)
                # Construct a numpy array from the stream
                #data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                #raw_image = cv2.imdecode(data, 1)
                raw_image = cv2.imread('public/camera_shot.jpg')
                after_image = raw_image
                if ai_mode:
                    ai_step (raw_image)
                    cv2.imwrite("public/car_cam_post.jpeg", after_image)
                    
                    socketIO.emit('robot update', {'data': robot_status})
                    for command in user_commands:
                        socketIO.emit('robot command', {'data': command})
                        log('Command: ' + str(command))
        finally:
            camera.stop_recording()
