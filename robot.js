/*** Robot Controller Script
 * complete nodejs application for controlling the RC car
 * parts:
 * * express.js - serves webpage for direct robot management
 * * socket.io - streams information
 * * johnny-five - interacts with the Arduino, and the RC car by extension
 * * raspicam - takes pictures via raspberry pi cammera
 * * opencv - applies vision algorithms to recorded image
*/

var express = require('express')
var app = express()
  , server = require('http').createServer(app)
  , io = require('socket.io').listen(server);

var raspiCam = require("raspicam");

var five = require("johnny-five"),
  board, servo;

var servos = {};

stringValues = {
  //throttle
  'forward': 35,
  'reverse': 125,
  'stop': 90,
  //steering
  'left': 40,
  'right': 100,
  'neutral': 75,
}

robotStatus = {
  hasArduino: false,
  hasCamera: false,
}

cameraOptions = {
  
}

// ----- socket.io -----
server.listen(80);

app.use(express.static(__dirname + '/public'));

app.get('/', function (req, res) {
  res.sendfile(__dirname + '/index.html');
});

io.sockets.on('connection', function (socket) {
  socket.emit('robot status', { data: 'server connected' });
  socket.on('robot command', function (data) {
    var parsedCommand = data.data.split("-");
    console.log('----- Command: -----');
    console.log(parsedCommand);
    
    if (robotStatus.hasArduino) {
      // Manual commands
      if (parsedCommand[0] == 'manual') {
        if (parsedCommand[1] == 'throttle') {
          if (parsedCommand[2] in stringValues) {
            accelChange(stringValues[parsedCommand[2]]);
          }
          else {
            accelChange(parseInt(parsedCommand[2]));
          }
        }
        else if (parsedCommand[1] == 'turn') {
          if (parsedCommand[2] in stringValues) {
            steerChange(stringValues[parsedCommand[2]]);
          }
          else {
            steerChange(parseInt(parsedCommand[2]));
          }
        }
      }
      else {    // parsedCommand[0] = 'stop'
        steerChange(stringValues['neutral']);
        accelChange(stringValues['stop']);
      }
    }
    socket.emit('robot command', { data: 'data' });
  });
});

// ----- RaspiCam + OpenCV -----
var camera = new RaspiCam(cameraOptions);
camera.start();

//listen for the "read" event triggered when each new photo/video is saved
camera.on("read", function(err, filename){ 
  cv.readImage("./camera_shot.jpg", function(err, im){
    im.detectObject(cv.FACE_CASCADE, {}, function(err, faces){
      for (var i=0;i<faces.length; i++){
        var x = faces[i]
        im.ellipse(x.x + x.width/2, x.y + x.height/2, x.width/2, x.height/2);
      }
      im.save('./process_shot.jpg');
    });
  })
});

// ----- Johnny Five -----

function steerChange (value) {
  servos.steering.move(value);
  
  board.repl.inject({
    s: servos
  });
}

function accelChange (value) {
  servos.acceleration.move(value);
  
  board.repl.inject({
    s: servos
  });
}

board = new five.Board();

board.on("ready", function() {
  servos = {
    acceleration: new five.Servo({
      pin: 9,
      range: [0, 180], // Default: 0-180
      type: "standard", // Default: "standard". Use "continuous" for continuous rotation servos
      startAt: 90, // if you would like the servo to immediately move to a degree
      center: false // overrides startAt if true and moves the servo to the center of the range
    }),
    steering: new five.Servo({
      pin: 10, 
      range: [40, 100], 
      type: "standard", 
      startAt: 75, 
      center: true, 
    })
  };
  acceleration = servos.acceleration;
  steering = servos.steering;
 
  // Inject the `servo` hardware into
  // the Repl instance's context;
  // allows direct command line access
  board.repl.inject({
    s: servos
  });
  
  robotStatus.hasArduino = true;
});
