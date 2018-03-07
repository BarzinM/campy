import struct
import threading
import pickle
import socket
import errno
from time import sleep

import cv2
from camera import Camera


class Stream(Camera):

    def receive(self, connection):
        self.running = True
        thrd = threading.Thread(target=self._receive, args=(connection,))
        thrd.daemon = True
        thrd.start()
        while self.frame is None:
            sleep(.01)

    def send(self, connection):
        cap = self.setup()

        thrd = threading.Thread(target=self._send, args=(cap, connection))
        thrd.daemon = True

        self.running = True
        thrd.start()

    def _receive(self, connection):
        data_size = struct.calcsize(">L")
        offset = 2 + data_size  # 'sp' + data_size

        data = connection.recv(4096)

        while self.running:
            pointer = -1
            while len(data) < 4096:
                data += connection.recv(4096)

            for i in range(len(data) - offset):
                if data[i:i + 1] == b's' and data[i + 1:i + 2] == b'p':
                    pointer = i + 2
                    break
                else:
                    print("bad start", pointer)
                    print(data)
                    raise ValueError("Bad Start")

            if pointer < 0:
                data = data[-offset:] + connection.recv(4096)
                print('looking again', len(data))
                raise
                continue

            message_size = struct.unpack(
                ">L", data[pointer:pointer + data_size])[0]
            pointer += data_size

            while len(data) < message_size + pointer:
                data += connection.recv(4096)

            frame_data = data[pointer:pointer + message_size]
            pointer += message_size

            data = data[pointer:]

            frame = pickle.loads(frame_data)
            with self.frame_lock:
                self.frame = frame

    def _send(self, cap, connection):
        try:
            while self.running:
                ret, frame = cap.read()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                data = pickle.dumps(frame)
                data_length = struct.pack(">L", len(data))

                connection.sendall(b"sp" + data_length)
                for i in range(0, len(data), 4096):
                    connection.sendall(data[i:i + 4096])

        except socket.error as e:
            e = e[0]
            if e == errno.ECONNRESET:
                print("Camera debug: Connection reset by peer")
                # continue
            else:
                print("Some socket error!!!")
        finally:
            self.running = False
            cap.release()


class StreamUDP(Camera):

    def receive(self, ip='localhost', port=8089, backlog=1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((ip, port))
        # connection, address = sock.accept()
        connection = sock

        self.running = True
        thrd = threading.Thread(target=self._receive, args=(connection,))
        thrd.daemon = True
        thrd.start()
        while self.frame is None:
            sleep(.01)

    def send(self, ip='localhost', port=8089):
        cap = self.setup()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # sock.connect((ip, port))

        thrd = threading.Thread(
            target=self._send, args=(cap, sock, (ip, port)))
        thrd.daemon = True

        self.running = True
        thrd.start()

    def _receive(self, connection):
        data_size = struct.calcsize(">L")
        offset = 2 + 2 * data_size  # 'sp' + data_size

        data = connection.recvfrom(4096)[0]

        while self.running:
            pointer = -1
            while len(data) < 4096:
                data += connection.recvfrom(4096)[0]

            for i in range(len(data) - offset):
                if data[i:i + 2] == b'sp':
                    this = pointer
                    pointer = i + 2
                    break
                # else:
                #     print("bad start", pointer)
                #     print(data[0])
                #     raise ValueError("Bad Start")

            if pointer < 0:
                data = data[-offset:] + connection.recvfrom(4096)[0]
                # print('looking again', len(data), data)
                # raise ValueError("couldn't find start")
                continue

            print(data[pointer - 2:pointer + 20])
            message_size = struct.unpack(
                ">L", data[pointer:pointer + data_size])[0]
            pointer += data_size
            message_size_2 = struct.unpack(
                ">L", data[pointer:pointer + data_size])[0]
            pointer += data_size
            if message_size != message_size_2:
                print(data[this:this + 10])
                print('bad packet size info', message_size, message_size_2)
                continue

            while len(data) < message_size + pointer + 2:
                data += connection.recvfrom(4096)[0]

            frame_data = data[pointer:pointer + message_size]
            pointer += message_size

            if data[pointer:pointer + 2] != b"ep":
                print("bad end", data[pointer:pointer + 2])
                data = data[pointer:]
                continue

            data = data[pointer + 2:]

            frame = pickle.loads(frame_data)
            with self.frame_lock:
                self.frame = frame

    def _send(self, cap, connection, address):
        try:
            while self.running:
                ret, frame = cap.read()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                data = pickle.dumps(frame)
                data_length = struct.pack(">L", len(data))
                print(len(data), data_length)

                connection.sendto(b"sp" + data_length + data_length, address)
                # # connection.sendto(b"sp",address)
                # connection.sendto(, address)
                # connection.sendto(data_length, address)

                for i in range(0, len(data), 512):
                    connection.sendto(data[i:i + 512], address)
                connection.sendto(b"ep", address)

        except socket.error as e:
            e = e[0]
            if e == errno.ECONNRESET:
                print("Camera debug: Connection reset by peer")
                # continue
            else:
                print("Some socket error!!!")
        finally:
            self.running = False
            cap.release()
