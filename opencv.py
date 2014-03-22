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
from socketIO_client import SocketIO

#constants: read from JSON file in the future
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

#ai
#manual control is now directly handled by the node.js server
ai_mode = '';
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier('lbpcascade_frontalface.xml')

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
    if ai_mode == 'lines':
        robot_status = detect_line(raw_image)
    elif ai_mode == 'face':
        robot_status = detect_face(raw_image)
    
    if robot_status:
        pass

def detect_line(raw_image):
    gray = cv2.cvtColor(raw_image,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,150,200,apertureSize = 3)
    
    #adjust HoughLine properties
    lines = cv2.HoughLinesP(edges,1,np.pi/100,50)
    if lines != None:
        for line in lines[0]:
            #print rho
            #print theta
            log(line)
            pt1 = (line[0],line[1])
            pt2 = (line[2],line[3])
            cv2.line(raw_image, pt1, pt2, (0,0,255), 3)
    log('-----')

def detect_face(raw_image):
    robot_status ['General'] = 'No face found'
    after_image = raw_image
    gray = cv2.cvtColor(raw_image,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        after_image = cv2.rectangle(after_image,(x,y),(x+w,y+h),(255,0,0),2)
        
        offCenter = x + w/2 - 400/2
        log("({0}, {1}) {2}x{3}".format(x,y,w,h))
        robot_status ['General'] = 'Face found'
        robot_status ['Face Center X'] = 'X: ' + str(x + w/2)
        robot_status ['Face Center Y'] = 'Y: ' + str(y + h/2)
        robot_status ['Face Off Center'] = str(offCenter)
        
        if offCenter < -5:
            user_commands.append('manual-turn-left')
            robot_status ['Direction'] = 'Left'
        elif offCenter > 5:
            user_commands.append('manual-turn-right')
            robot_status ['Direction'] = 'Right'
        else:
            user_commands.append('manual-turn-neutral')
            robot_status ['Direction'] = 'Neutral'
        
        #Adjust acceleration based on face box width
        if w > 5:
            pass
    log('-----')

#Communicate through socket.io
with SocketIO('http://localhost', 80) as socketIO:
    #Streaming through picamera, so initialize outside loop
    with picamera.PiCamera() as camera:
        camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
        camera.start_recording(stream, format='h264')
        camera.start_preview()
        ai_mode = 'face'
        try:
            while run_loop:
                user_commands = []
                robot_status = {}
                
                camera.capture('camera_shot.jpg', format='jpeg', use_video_port=True)
                # Construct a numpy array from the stream
                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                #raw_image = cv2.imdecode(data, 1)
                raw_image = cv2.imread('camera_shot.jpg')
                after_image = raw_image
                if ai_mode:
                    ai_step (raw_image)
                    cv2.imwrite("public/car_cam_post.jpeg", after_image)
                    
                    socketIO.emit('robot update', {'data': robot_status})
                    test = 0
                    for command in user_commands:
                        socketIO.emit('robot command', {'data': command})
                        log('Command: ' + str(command))
                        test += 1
        finally:
            camera.stop_recording()