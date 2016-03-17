# TCP Chat Server
__author__ = "Sam Scott"
__email__ = "samueltscott@gmail.com"
# Created on 16-03-2016

import socket, threading, time, datetime

def listen(s):
    #try:
    print("Listening for connections to", server, "on port", str(port) + "...")
    s.listen(1)
    c, addr = s.accept()
    connections.append(c)
    addresses[c] = addr
    print("Connection established with", str(addr))
    tc = threading.Thread(target = threaded_client, args = (c, addr))
    tc.start()
    #except Exception as e:
        #print(e)
        #c.close()
        #connections.remove(c)

def process_command(message, c, addr):
    message = message[1:]
    params = message.split(" ")
    command = params[0]
    params = params[1:]
    priv_response = ""
    response = ""
    if command == "nick":
        nick = " ".join(x for x in params).strip()
        if nick not in illegal_nicks:
            try:
                prev_nick = nicks[addr]
            except:
                prev_nick = addr
            nicks[addr] = nick
            response = "[SERVER] {} changed nickname to {}".format(prev_nick, nick)
        else:
            print(c, "nick change blocked. (Value: \"{}\")".format(nick))
            priv_response = "Nickname change denied."
    if response:
        broadcast(response, sender=c)
    if priv_response:
        broadcast(priv_response, targets = [c])
        

def threaded_client(c, addr):
    #try:
    while True:
        data = c.recv(data_buff)
        if not data:
            break
        message = data.decode("utf-8")
        if message[0] == "/":
            process_command(message, c, addr)
        else:
            print("\"{}\"".format(message), "from", str(addr))
            broadcast(message, sender=c)
    c.close()
    connections.remove(c)
    #except Exception as e:
        #print(e)
        #c.close()
        #connections.remove(c)

def broadcast(message, sender = None, targets = []):
    for connection in connections:
        time = datetime.datetime.now().strftime('%H:%M:%S')
        if targets:
            if connection in targets:
                #try:
                connection.send(message.encode())
                #except Exception as e:
                    #print(e)
                    #connection.close()
                    #connections.remove(connection)
        else:
            #try:
            message = "[" + time + "] " + nicks[addresses[sender]] + ": " + message
            connection.send(message.encode())
            #except Exception as e:
                #print(e)
                #connection.close()
                #connections.remove(connection)
            

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
