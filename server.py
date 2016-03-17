# TCP Chat Server
__author__ = "Sam Scott"
__email__ = "samueltscott@gmail.com"
# Created on 16-03-2016

import socket, threading, time, datetime

def listen(s):
    print("Listening for connections to", server, "on port", str(port) + "...")
    s.listen(1)
    c, addr = s.accept()
    connections.append(c)
    if len(connections) == 1:
        admin = [c, addr]
    addresses[c] = addr
    print("Connection established with", str(addr))
    tc = threading.Thread(target = threaded_client, args = (c, addr))
    tc.start()

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
                prev_nick = ""
            nicks[addr] = nick
            if prev_nick:
                response = "{} changed nickname to {}".format(prev_nick, nick)
                print("{} changed nickname to {}".format(prev_nick, nick))
            else:
                response = "{} joined the server.".format(nick)
                print("{} joined the server.".format(nick))
        else:
            print(c, "nick change blocked. (Value: \"{}\")".format(nick))
            priv_response = "Nickname change denied."
    if command == "kick":
        if admin == [c, addr]:
            target = params[0]
            for connection in connections:
                a = addresses[connection]
                if nicks[a].lower() == target.lower():
                    connection.close()
                    response = "{} has disconnected.".format(nicks[a])
                    print("{} \"{}\" has disconnected.".format(a, nicks[a]))
                    connections.remove(connection)
                    break
        else:
            priv_response = "Access denied."
    if response:
        broadcast(response, sender=c, server = True)
    if priv_response:
        broadcast(priv_response, targets = [c])

def threaded_client(c, addr):
    while True:
        try:
            data = c.recv(data_buff)
        except socket.error as e:
            break
        if not data:
            break
        message = data.decode("utf-8")
        if message[0] == "/":
            try:
                print("\"{}\" from {}".format(message, addr), "\"{}\"".format(nicks[addr]))
            except:
                print("\"{}\" from {}".format(message, addr))
            process_command(message, c, addr)
        else:
            print("\"{}\"".format(message), "from", str(addr), "\"{}\"".format(nicks[addr]))
            broadcast(message, sender=c)
    print("{} \"{}\" disconnected.".format(addresses[c], nicks[addr]))
    c.close()
    connections.remove(c)

def broadcast(message, sender = None, targets = [], server=False):
    for connection in connections:
        time = datetime.datetime.now().strftime('%H:%M:%S')
        if targets:
            if connection in targets:
                try:
                    connection.send(message.encode())
                except socket.error as e:
                    print("{} \"{}\" disconnected.".format(addresses[c], nicks[addresses[c]]))
                    connection.close()
                    connections.remove(connection)
        else:
            if not server:
                message = "[" + time + "] " + nicks[addresses[sender]] + ": " + message
            else:
                message = "[" + time + "] " + message
            try:
                connection.send(message.encode())
            except socket.error as e:
                print("{} \"{}\" disconnected.".format(addresses[c], nicks[addresses[c]]))
                connection.close()
                connections.remove(connection)
            

connections = []
addresses = {}
nicks = {}
illegal_nicks = ["", " ", "<", ">"]
admin = []
if __name__ == "__main__":
    server = socket.gethostbyname(socket.gethostname())#"10.13.9.89" # MCS IP Address
    print("IP Address:", server)
    port = 45009
    data_buff = 4096
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((server, port))
    
    num_conn = 100
    for x in range(num_conn):
        listen(s)
