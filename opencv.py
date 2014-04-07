"""Robot OpenCV and Controller Script

Retrieve camera information from stream
Communicates through sockets with a websocket server
Applies OpenCV algorithms through video stills
OpenCV results through the socket
Receives robot commands from socket

"""

import io
import socket
import struct
import datetime
import time
import sys, getopt
import numpy as np
import cv2
import urllib2

CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
face_cascade = cv2.CascadeClassifier('cascade_files/lbpcascade_frontalface.xml')
body_cascade = cv2.CascadeClassifier('cascade_files/haarcascade_fullbody.xml')
upper_cascade = cv2.CascadeClassifier('cascade_files/haarcascade_upperbody.xml')
upper2_cascade = cv2.CascadeClassifier('cascade_files/haarcascade_mcs_upperbody.xml')

#general
run_loop = True
server_address = 'http://127.0.0.1'
server_port = 8000
stream = io.BytesIO()
robot_status = {}
user_commands = []
after_image = '';

#command line arguments
try:
    opts, args = getopt.getopt(sys.argv,"hs:p:",["server=","port="])
except getopt.GetoptError:
    print 'improper use of arguments'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print 'opencv.py: -p for port'
        sys.exit()
    #port to listen to address
    elif opt in ("-s", "--server"):
        server_address = arg
    elif opt in ("-p", "--port"):
        server_port = int(arg)

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')

def detect_face(raw_image):
    notFound = True
    robot_status ['General'] = 'No face found'
    after_image = raw_image
    gray = cv2.cvtColor(raw_image,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        if (notFound):
            cv2.rectangle(after_image,(x,y),(x+w,y+h),(255,255,0),2)
            move_command(x, y, w, h)
            notFound = False
        else:
            cv2.rectangle(after_image,(x,y),(x+w,y+h),(255,0,0),2)
    
    bodies = body_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in bodies:
        if (notFound):
            cv2.rectangle(after_image,(x,y),(x+w,y+h),(255,255,0),2)
            move_command(x, y, w, h)
            notFound = False
        else:
            cv2.rectangle(after_image,(x,y),(x+w,y+h),(0,255,0),2)
    
    uppers = upper_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in uppers:
        if (notFound):
            cv2.rectangle(after_image,(x,y),(x+w,y+h),(255,255,0),2)
            move_command(x, y, w, h)
            notFound = False
        else:
            cv2.rectangle(after_image,(x,y),(x+w,y+h),(0,0,255),2)
    
    uppers2 = upper2_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in uppers2:
        if (notFound):
            cv2.rectangle(after_image,(x,y),(x+w,y+h),(255,255,0),2)
            move_command(x, y, w, h)
            notFound = False
        else:
            cv2.rectangle(after_image,(x,y),(x+w,y+h),(0,255,255),2)
    
    return after_image

#generate movement command based on cascade detection box properties
def move_command(x, y, w, h):
    offCenter = x + w/2 - CAMERA_WIDTH/2
    print "({0}, {1}) {2}x{3}".format(x,y,w,h)
    print 'Off Center: ' + str(offCenter)
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
    if w < 150:
        user_commands.append('manual-throttle-forward')
        robot_status ['Movement'] = 'Forward'
    elif w > 200:
        user_commands.append('manual-throttle-reverse')
        robot_status ['Movement'] = 'Reverse'
    else:
        user_commands.append('manual-throttle-stop')
        robot_status ['Movement'] = 'None'

# ----- Main Operation -----
try:
    while run_loop:
        user_commands = []
        robot_status = {'Timestamp': str(datetime.datetime.now())}
        robot_status ['Has Camera'] = True
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(4))[0]
        if not image_len:
            print 'not image_len'
            continue
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        data = np.fromstring(image_stream.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, 1)
        
        new_image = detect_face(image)
        
        # Display the resulting frame
        cv2.imshow('camera',new_image)
        print('Image is processed')
        for command in user_commands:
            response = urllib2.urlopen(server_address+'/command/?command='+command).read()
            print response
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    connection.close()
    server_socket.close()
    cv2.destroyAllWindows()