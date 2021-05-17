import socket

class relay:

    def __init__(self, ip):
        self._ip = ip

    def on(self, relay_index):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self._ip, 80))
            s.sendall(("GET /state.xml?relay"+str(relay_index)+"State=1 HTTP/1.1\r\n\r\n").encode())
            s.close()
        except Exception as e:
            print(e)

    def off(self, relay_index):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self._ip, 80))
            s.sendall(("GET /state.xml?relay" + str(relay_index) + "State=0 HTTP/1.1\r\n\r\n").encode())
            s.close()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    relay = relay("192.168.0.6")
    relay.off(4)