ShereCar RC Car Controller
====================

Control a RC car over the internet via node.js using socket.io and johnny-five.

Hardware Requirements
----------------------
* Raspberry Pi
* Arduino UNO
* USB connection from RPi to Arduino UNO
* Wires for power and ground
* Wires from Aruidno Pin 10/9 to proper servo connection

Libraries Requirements
---------------------
* Socket.io
* Expressjs
* Johnny-five
* OpenCV
* RaspiCam

Getting the Raspberry Pi Ready
------------------------------
* Update/upgrade OS
 * sudo apt-get update
 * sudo apt-get upgrade
* Install node modules
 * npm install socket.io express johnny-five opencv raspicam

To run opencv.py
* Install python libraries
 * sudo apt-get install libopencv-dev python-opencv
 * sudo pip install socketIO-client

Using the Controller
-------------------
* Start up the nodejs server
 * sudo node server.js
* Open a web browser to the Raspberry Pi's internet location
* Enter the Raspberry Pi's address into the field and click the connect button
* Control the RC Car

Alternate options to run
* Run the node server when there's no Arduino attached
 * sudo node server.js noArduino
 
File Layout
-----------
* server.js - socketio server, forwards information between opencv.py and webpage. Commands Arduino via johnny-five
* index.html - webpage served by node server
 * manual control socketio emits
 * robot status from socketio
 * retrieves static elements from public folder
* opencv.py - raspberry pi camera and opencv processing
 * only has face detection for now
 * updates opencv image in public folder
* lbpcascade_frontalface.xml - currently used cascade file

Possible Future Enhancements
----------------------------
* Nodejs version for opencv and raspi camera
* Proper 3d printed mounts for RC car components
* Easier way to configure RC car for use at new locations
* Stream OpenCV video to the internet
