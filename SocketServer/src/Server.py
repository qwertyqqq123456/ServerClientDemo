import threading
import SocketServer

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    'This handler is for handling request on server'
    def handle(self):
        data = self.request.recv(1024)
        response = "{0} reply: \n{1}" .format(threading.current_thread().name, data)
        self.request.sendall(response)
        
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    'This is Threaded TCP Server'
    pass


if __name__ == "__main__":
    
    HOST, PORT = "localhost", 53758
    
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    print "ip,port= ", ip, port
    
    try:
        server.serve_forever()
    except KeyboardInterrupt as e:
        server.shutdown()
        print "Server shutdown."
    
    
