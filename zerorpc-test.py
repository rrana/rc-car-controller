import zerorpc

c = zerorpc.Client()
c.connect("tcp://127.0.0.1:4242")
c.hello("RPC2")
#c.hi('hi')