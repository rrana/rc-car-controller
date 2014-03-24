/*** Robot Controller Script
 * application for controlling the RC car through a web browser
 * parts:
 * * express.js - serves webpage for direct robot management
 * * socket.io - streams information
 * * johnny-five - interacts with the Arduino, and the RC car by extension
 * run in conjunction with python opencv.py for AI commands
 *
 * Command line options:
 * * noArduino - skip all johnny-five content
*/

var args = process.argv.slice(2);

// Consider adding option to automatically start python script:
//http://shapeshed.com/command-line-utilities-with-nodejs/

var express = require('express')
var app = express()
  , server = require('http').createServer(app)
  , io = require('socket.io').listen(server);

if (args.indexOf("noArduino") == -1) {
  var five = require("johnny-five")
    , board, servo;
  
  var arduinoServos = {};
  var accelerationServo = {
    pin: 9,
    range: [0, 180],    // Default: 0-180
    type: "standard",   // Default: "standard". Use "continuous" for continuous rotation servos
    startAt: 90,          // if you would like the servo to immediately move to a degree
    center: false         // overrides startAt if true and moves the servo to the center of the range
  }
  var steeringServo = {
    pin: 8, 
    range: [40, 100], 
    type: "standard", 
    startAt: 75, 
    center: true, 
  }
}

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

serverStatus = {
    hasArduino: false,
    hasCamera: false,
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
    
    if (serverStatus.hasArduino) {
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
      // AI commands
      if (parsedCommand[0] == 'face') {
        if (parsedCommand[1] == 'begin') {
          socket.broadcast.emit('robot ai', { 'command': 'face-start' });
        }
        else {
          socket.broadcast.emit('robot ai', { 'command': 'ai-stop' });
        }
      }
      if (parsedCommand[0] == 'red') {
        if (parsedCommand[1] == 'begin') {
          socket.broadcast.emit('robot ai', { 'command': 'red-start' });
        }
        else {
          socket.broadcast.emit('robot ai', { 'command': 'ai-stop' });
        }
      }
    }
  });
  socket.on('robot update', function (data) {
    socket.broadcast.emit('robot status', { 'data': data });
    socket.broadcast.emit('robot camera', {'data': 'check'});
  });
  
  setInterval(function(){socket.emit('robot camera', {'data': 'check'});},1000);
});

// ----- Johnny Five -----
// These should only be called or accessed if "noArduino" is not an option

function steerChange (value) {
  arduinoServos.steering.move(value);
  
  board.repl.inject({
    s: arduinoServos
    });
}

function accelChange (value) {
  arduinoServos.acceleration.move(value);
  
  board.repl.inject({
    s: arduinoServos
  });
}

if (args.indexOf("noArduino") == -1) {
  board = new five.Board();

  board.on("ready", function() {
    arduinoServos = {
      acceleration: new five.Servo(accelerationServo),
      steering: new five.Servo(steeringServo)
    };
    acceleration = arduinoServos.acceleration;
    steering = arduinoServos.steering;
   
    // Inject the `servo` hardware into
    // the Repl instance's context;
    // allows direct command line access
    board.repl.inject({
      s: arduinoServos
    });
    
    serverStatus.hasArduino = true;
  });
}