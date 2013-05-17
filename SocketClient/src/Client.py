import socket
import threading
from random import randrange
import time

def client(ip, port, message):
    'This function is for executing client logic'
    randtime = randrange(0, 10)
    time.sleep(randtime)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print"Received: {}".format(response)
    finally:
        sock.close()
        
        
if __name__ == "__main__":
    
    ip, port = "54.214.53.142", 36666
    # ip, port = "localhost", 36666
    
    totalnumber = 5000
    times = 4000
    
    for i in range(1, (totalnumber / 2) + 1):
        reg_message = "R#Client{0}#Client{1}".format(i, (i + totalnumber / 2))
        (threading.Thread(target=client, args=(ip, port, reg_message))).start()
    for i in range((totalnumber / 2) + 1, totalnumber + 1):
        reg_message = "R#Client{0}#Client{1}".format(i, (i - totalnumber / 2))
        (threading.Thread(target=client, args=(ip, port, reg_message))).start()

    print "Waiting for registration to be completed...\n"
    time.sleep(40)
    
    for j in range(times):
        randnumber_1 = randrange(1, totalnumber + 101)
        randnumber_2 = randrange(1, totalnumber)
        if randnumber_1 % 2 == 0:
            msg = "D#{0}#Send#Red#20".format(randnumber_2) 
        else:
            msg = "D#{0}#Reply##".format(randnumber_2)
        
        (threading.Thread(target=client, args=(ip, port, msg))).start()
    

