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