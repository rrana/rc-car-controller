var zerorpc = require("zerorpc");

var server = new zerorpc.Server({
    hello: function(name, reply) {
        console.log(name);
        reply("Hello, " + name);
    },
    hi: function(name, reply) {
        console.log(name);
    }
});

server.bind("tcp://0.0.0.0:4242");