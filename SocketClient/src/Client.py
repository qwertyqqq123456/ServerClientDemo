import socket
from random import randrange
import time

class Client:
    'This function is for executing client logic'

    def __init__(self, ip, port):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setblocking(1)
        self.__sock.connect((ip, port)) 
        
    def sendrecv(self, message):
        self.__sock.sendall(message)
        response = self.__sock.recv(1024)
        print "Client received:", response
    
    def close(self):
        self.__sock.close()
        
        
if __name__ == "__main__":
    
    ip, port = "54.214.131.101", 36666
    # ip, port = "localhost", 36666
    
    totalnumber = 5000
    times = 5000
    c_dict = {}
    for i in range(1, (totalnumber / 2) + 1):
        # reg_message = "R#Client{0}#Client{1}".format(i, (i + totalnumber / 2))
        c_dict[i] = Client(ip, port)
        # c_dict[i].sendrecv(reg_message)
    for i in range((totalnumber / 2) + 1, totalnumber + 1):
        # reg_message = "R#Client{0}#Client{1}".format(i, (i - totalnumber / 2))
        c_dict[i] = Client(ip, port)
        # c_dict[i].sendrecv(reg_message)

    # print "Waiting for registration to be completed...\n"
    # time.sleep(1)
    # print "Now it's time to send data..." 
    
    for j in range(times):
        randnumber_1 = randrange(1, totalnumber + 101)
        randnumber_2 = randrange(1, totalnumber)
        if randnumber_1 % 2 == 0:
            msg = "D#{0}#Send#Red#20".format(randnumber_2) 
        else:
            msg = "D#{0}#Reply##".format(randnumber_2)
        c_dict[randnumber_2].sendrecv(msg)
        
    """for j in range(1, totalnumber + 1):
        c_dict[j].close()
    print "Over" """
    

