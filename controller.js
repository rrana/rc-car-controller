var app = require('express')()
  , server = require('http').createServer(app)
  , io = require('socket.io').listen(server);

server.listen(80);

app.use(require('express').static(__dirname + '/public'));

app.get('/', function (req, res) {
  res.sendfile(__dirname + '/index.html');
});

io.sockets.on('connection', function (socket) {
  socket.emit('robot status', { data: 'server connected' });
  socket.on('robot command', function (data) {
    console.log(data);
    socket.emit('robot command', { data: 'data' });
  });
  
  socket.on('robot status', function (data) {
    console.log('--- Received data ---');
    console.log(data);
    socket.emit('status update', { data: data });
  });
});