ShereCar RC Car Controller
====================

Control a RC car over the internet via node.js using socket.io and johnny-five.

Hardware Requirements
----------------------
* Raspberry Pi
* Arduino UNO
* USB connection from RPi to Arduino UNO
* Wires for power and ground
* Wires from Aruidno Pin 8/9 to proper servo connection

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

To Do
-----
* Fix socket.io client failure in opencv.py
 * Likely reason: socket.io fires a heartbeat to clients, which times out on python script. This causes the connection to drop
* Have python socket client listen in on a separate thread to take commands from the webpage
 * Might fix previous issue
* Better range values for RC car servos
* Use something like "manual-turn-35" instead of "manual-turn-left" for better precision turning
* Reduce strain on ai commands from opencv.py/server.js to johnny-five, as commands are being dropped
* Convert camera feed from refreshed jpeg to video (VideoWriter)
* Integrate voltage regulator and run RPi off the battery

Want List
---------
* Nodejs version for opencv and raspi camera
* Proper 3d printed mounts for RC car components
* Easier way to configure RC car for use at new locations
* Stream OpenCV video to the internet