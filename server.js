var express = require('express')
var app = express()
  , server = require('http').createServer(app)
  , io = require('socket.io').listen(server);

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
  });
  socket.on('robot update', function (data) {
    socket.emit('robot status', { 'data': data });
    socket.emit('robot camera', {'data': 'check'});
  });
  
  setInterval(function(){socket.emit('robot camera', {'data': 'check'});},1000);
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
      pin: 8, 
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