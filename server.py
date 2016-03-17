# TCP Chat Server
__author__ = "Sam Scott"
__email__ = "samueltscott@gmail.com"
# Created on 16-03-2016

import socket, threading

def listen(s):
    try:
        print("Listening for connections to", server, "on port", str(port) + "...")
        s.listen(1)
        c, addr = s.accept()
        connections.append(c)
        print("Connection established with", str(addr), "on port", port)
        tc = threading.Thread(target = threaded_client, args = (c, addr))
        tc.start()
    except:
        c.close()
        s.close()
        quit()

def threaded_client(c, addr):
    try:
        while True:
            data = c.recv(data_buff)
            if not data:
                break
            message = data.decode("utf-8")
            print("\"{}\"".format(message), "from", str(addr))
            broadcast(message, [c])
        c.close()
        connections.remove(c)
    except Exception as e:
        print(e)
        
        c.close()
        s.close()
        quit()

def broadcast(message, exceptions = []):
    for connection in connections:
        # if connection not in exceptions:
        try:
            connection.send(message.encode())
        except Exception as e:
            print(e)

connections = []
if __name__ == "__main__":
    server = socket.gethostbyname(socket.gethostname())#"10.13.9.89" # MCS IP Address
    print("This server's IP address is", server)
    print("Clients must connect to this address in order to use the chat.")
    input("\nPress enter to continue . . .")
    port = 45009
    data_buff = 4096
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((server, port))
    
    num_conn = 30
    for x in range(num_conn):
        listen(s)
