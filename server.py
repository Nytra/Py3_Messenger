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
        addresses[c] = addr
        print("Connection established with", str(addr))
        tc = threading.Thread(target = threaded_client, args = (c, addr))
        tc.start()
    except Exception as e:
        print(e)
        input("Press enter to continue . . .")
        c.close()
        s.close()
        quit()

def process_command(message, c):
    message = message[1:]
    params = message.split(" ")
    command = params[0]
    if command == "nick":
        nick = " ".join(x for x in params).strip()
        if nick not in illegal_nicks:
            nicks[c] = nick
        else:
            print(c, "nick change blocked. (Value: \"{}\")".format(nick))
        

def threaded_client(c, addr):
    try:
        while True:
            data = c.recv(data_buff)
            if not data:
                break
            message = data.decode("utf-8")
            if message[0] == "/":
                process_command(message, c)
            print("\"{}\"".format(message), "from", str(addr))
            broadcast(message, c)
        c.close()
        connections.remove(c)
    except Exception as e:
        print(e)
        input("Press enter to continue . . .")
        c.close()
        s.close()
        quit()

def broadcast(message, c):
    for connection in connections:
        # if connection not in exceptions:
        try:
            message = nicks[c] + "> " + message
            connection.send(message.encode())
        except Exception as e:
            print(e)
            

connections = []
addresses = {}
nicks = {}
illegal_nicks = ["", " ", "<", ">"]
if __name__ == "__main__":
    server = socket.gethostbyname(socket.gethostname())#"10.13.9.89" # MCS IP Address
    print("IP Address:", server)
    port = 45009
    data_buff = 4096
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((server, port))
    
    num_conn = 30
    for x in range(num_conn):
        listen(s)
