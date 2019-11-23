import socket
import threading
import sys
import msgpack
import queue
import time
import signal

PORT = 42069
running = True
connected = False

server = None

inQueue = queue.Queue()
outQueue = queue.Queue()


# def signal_handler(sig, frame):
# 	global running, connected
# 	running = False
# 	if connected:
# 		connected = False
# 		server.close()
# 	print('Exiting...')
# 	time.sleep(5)
# 	sys.exit()
# signal.signal(signal.SIGINT, signal_handler)

class distanceTester(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cnt = 0

    def run(self):
        while running:
            if inQueue.empty():
                outQueue.put([69, self.cnt, ["testing", 3.14159]])
            else:
                outQueue.put(inQueue.get())
            time.sleep(5)
        print('TestInserter thread dying!')


class TestInserter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cnt = 0

    def run(self):
        while running:
            outQueue.put([69, self.cnt, ["testing", 3.14159]])
            time.sleep(5)
        print('TestInserter thread dying!')


class QueueReader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while running:
            if not inQueue.empty():
                print(inQueue.get())
        print('QueueReader thread dying!')


class LaunchConnectionReader(threading.Thread):
    def __init__(self, sock, address):
        threading.Thread.__init__(self)
        self.address = address
        self.sock = client

    def run(self):
        global connected
        unpacker = msgpack.Unpacker(raw=False, max_buffer_size=1024 * 1024)

        while connected:
            buf = self.sock.recv(1024)
            if not buf:
                connected = False
                break

            unpacker.feed(buf)
            for o in unpacker:
                inQueue.put(o)
        print('LaunchConnectionReader thread dying!')


class LaunchConnectionWriter(threading.Thread):
    def __init__(self, sock, address):
        threading.Thread.__init__(self)
        self.address = address
        self.sock = client

    def run(self):
        while connected:
            while not outQueue.empty():
                self.sock.send(msgpack.packb(outQueue.get()))
        print('LaunchConnectionWriter thread dying!')


if __name__ == "__main__":
    print('Setting up socket on port {}...'.format(PORT))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', PORT))
    server.listen(1)
    print('Ground Controller initialized!')

    tester = TestInserter()
    tester.start()

    #dT = distanceTester()
    #dT.start()

    qrt = QueueReader()
    qrt.start()

    while running:
        print('Listening on port {}...'.format(PORT))
        (client, address) = server.accept()
        print('Accepted connection from {}:{}!'.format(address[0], address[1]))
        connected = True

        lcr = LaunchConnectionReader(client, address)
        lcw = LaunchConnectionWriter(client, address)

        lcr.start()
        lcw.start()

        lcr.join()
        lcw.join()

        print('Connection closed!')

    qrt.join()
