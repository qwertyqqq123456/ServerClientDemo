import socket

def client(ip, port, message):
    'This function is for executing client logic'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print"Received: {}".format(response)
    finally:
        sock.close()
        
        
if __name__ == "__main__":
    
    ip, port = "127.0.0.1", 53758
    
    for i in range(1, 31):
        client(ip, port, "Client Request# " + str(i))
