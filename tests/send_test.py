from stream import Stream
from time import sleep
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# socket.bind(('192.168.9.11', 8089))
# socket.listen(1)
# connection, address = socket.accept()

s.connect(('localhost', 8089))


c = Stream()
c.send(s)
while True:
    sleep(1.)
