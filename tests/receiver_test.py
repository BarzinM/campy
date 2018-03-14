from stream import Stream
from time import sleep
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('localhost', 8089))
s.listen(1)
connection, address = s.accept()

# socket.connect((server_ip, 8089))
print("connected")

cam = Stream()
cam.receive(connection)
cam.display()
