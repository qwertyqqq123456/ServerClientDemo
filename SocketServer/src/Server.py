import threading
import SocketServer
import Queue
import socket


devlist_pairinfo = 0
devlist_connected = 1
devlist_isalive = 2
devlist_lock = 3
devlist_queue = 4

devicelist = {}
devicenumber_index = {}
indexlock = threading.Lock()

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    'This handler is for handling request on server'
    def process(self, data):
        'This function handles the processing of the requests'
        
        paralist = data.split("#")
        
        if paralist[0] == "R":          
            device_name = paralist[1]
            pairing_info = paralist[2]
            connected = False
            isalive = True
            
            if device_name not in devicelist:
                devicelist[device_name] = [pairing_info, connected, isalive, threading.Lock()]
                
                indexlock.acquire()
                devicenumber = len(devicenumber_index) + 1
                devicenumber_index[devicenumber] = device_name
                indexlock.release()
                
                if pairing_info in devicelist:
                    if devicelist[pairing_info][devlist_pairinfo] == device_name:
                        
                        devicelist[pairing_info][devlist_lock].acquire()
                        devicelist[pairing_info][devlist_connected] = True
                        devicelist[pairing_info].append(Queue.Queue(5))
                        devicelist[pairing_info][devlist_lock].release()
                        
                        devicelist[device_name][devlist_lock].acquire()
                        devicelist[device_name][devlist_connected] = True
                        devicelist[device_name].append(Queue.Queue(5))
                        devicelist[device_name][devlist_lock].release()
                        
                    else:
                        print "Some error in devicelist: [name mismatching]"
                    
                response = "{0} registered as {1}" .format(device_name, devicenumber)
            else:
                response = "{0} has already been registered.".format(device_name)
        
            return (device_name, response)
        elif paralist[0] == "D":
            sender_number = int(paralist[1])
            code = paralist[2]             
            if code == "Send":
                color = paralist[3]
                brightness = paralist[4]
                         
            if sender_number in devicenumber_index:
                sender_name = devicenumber_index[sender_number]

                if sender_name in devicelist:

                    if devicelist[sender_name][devlist_pairinfo] in devicelist:
                    
                        if devicelist[sender_name][devlist_connected] == True \
                        and devicelist[devicelist[sender_name][devlist_pairinfo]][devlist_connected] == True:
                        
                            'Response'    
                            try:
                                response = devicelist[sender_name][devlist_queue].get(False)
                                devicelist[sender_name][devlist_queue].task_done()
                            except Queue.Empty:
                                response = "No message this time"
                                
                            response = sender_name + ": " + response
                        
                            'Send msg'
                            if code == "Send":
                                operation = "Send " + color + " " + brightness
                            elif code == "Reply":
                                operation = "Reply"
                            else:
                                print "error code"                                                          
                            # print"operation:", operation
                            
                            try:
                                devicelist[devicelist[sender_name][devlist_pairinfo]][devlist_queue].put(operation, False)
                            except Queue.Full:
                                print "The queue is full, try again later"
                                
                        else:
                            response = "Warning: This device is not connected."
                    else:
                        response = "Warning: The pair information is not recorded."
                else:
                    response = "Error: This email appears in index list but not the devicelist." 
                return (sender_name, response)              
            else:
                response = "Error: Didn't find this device number in system!"
                return ("default", response)
                
            return (sender_name, response)
        elif paralist[0] == "N":
            sender_number = int(paralist[1])
            if sender_number in devicenumber_index:
                sender_name = devicenumber_index[sender_number]

                if sender_name in devicelist:                  
                    'Response'    
                    try:
                        response = devicelist[sender_name][devlist_queue].get(False)
                        devicelist[sender_name][devlist_queue].task_done()
                    except Queue.Empty:
                        response = "No message this time"
                                
                    response = sender_name + ": " + response                   
                else:
                    response = "Error: This email appears in index list but not the devicelist."  
                return (sender_name, response)             
            else:
                response = "Error: Didn't find this device number in system!"
                return ("default", response)
            
        else:
            response = "Error Op Code." 
            pass         
    
    def handle(self):
        running = True      
        self.__devicename = ["default"]
        while(running):           
            try:
                self.request.settimeout(3600)
                data = self.request.recv(1024)
                if data == 0 or data == None or data == "":
                    if self.__devicename[0] is not "default":
                        client_die(self.__devicename[0])
                    running = False
                    self.request.close()
                    print "The client closed."
                elif data == -1:
                    continue
                    print "recv() error."
                else:
                    self.__devicename[0], response = self.process(data)
                    handle_alivesignal(self.__devicename[0])
                    print "request processed."
                    self.request.sendall(response)
            except socket.timeout as e:
                if self.__devicename[0] is not "default":
                    client_die(self.__devicename[0])
                running = False
                self.request.close()
                print "timeout error:", e.strerror
            
        
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    'This is Threaded TCP Server'
    pass

def handle_alivesignal(devicename):
    'This function handles the alive signal sent by clients.'
    devicelist[devicename][devlist_lock].acquire()
    if devicelist[devicename][devlist_isalive] == False:
        devicelist[devicename][devlist_isalive] = True
        if devicelist[devicename][devlist_pairinfo] in devicelist:
            if devicelist[devicelist[devicename][devlist_pairinfo]][devlist_isalive] == True:
                devicelist[devicename][devlist_connected] = True
                devicelist[devicelist[devicename][devlist_pairinfo]][devlist_connected] = True
            else:
                print "Cannot reconnect: the pair device is dead."
        else:
            print "Cannot reconnect: the pair info is not recorded."
    devicelist[devicename][devlist_lock].release()

def client_die(devicename):
    'Performing operations when the server thinks this device is dead'    
    devicelist[devicename][devlist_lock].acquire()   
    if devicelist[devicename][devlist_pairinfo] in devicelist:
        devicelist[devicename][devlist_connected] = False
        devicelist[devicelist[devicename][devlist_pairinfo]][devlist_connected] = False
        try:
            devicelist[devicename][devlist_queue].clear()
            devicelist[devicelist[devicename][devlist_pairinfo]][devlist_queue].clear()
        except Queue.Empty:
            print "This queue is already empty, no need to clear."
    else:
        print "Warning: missing the pair information, cannot make it disconnected, die alone"
    devicelist[devicename][devlist_isalive] = False
    devicelist[devicename][devlist_lock].release()
    # May include another timer to indicate when to clear the long-dead device record

if __name__ == "__main__":
    
    HOST, PORT = "10.253.11.33", 36666
    # HOST, PORT = "localhost", 36666
    
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    print "ip,port= ", ip, port
    
    try:
        print "Server is serving..."
        server.serve_forever()    
    except KeyboardInterrupt as e:
        server.shutdown()
        print "Server shutdown."  

"""import socket
import threading 
import time  

class Server:
    
    def __init__(self):    
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind(("localhost", 36668))
        self.__server.listen(5)
        
    def process(self):
        while(1):
            self.__c_sock.settimeout(5)
            try:
                print "before recv"
                data = self.__c_sock.recv(1024)
                print "after recv"
            except socket.timeout as e:
                print "timeout error:", e.strerror
            self.__c_sock.sendall(data)

    def serve(self):
        while(1):
            self.__c_sock, c_address = self.__server.accept()
            threading.Thread(target=self.process).start()

class Client:
    
    def __init__(self):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.connect(("localhost", 36668))
        
    def sendrecv(self, msg):
        self.__sock.sendall(msg)
        response = self.__sock.recv(1024)
        print "C Recv:", response

if __name__ == "__main__":
    mserver = Server()
    threading.Thread(target=mserver.serve).start()   
    mclient = Client()
    mclient.sendrecv("Sample msg")
    
    print "Over" """



    
