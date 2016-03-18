# TCP Chat Server
__author__ = "Sam Scott"
__email__ = "samueltscott@gmail.com"
# Created on 16-03-2016

import socket, threading, time, datetime

def listen(s):
    global admin
    print("Listening for connections to", server, "on port", str(port) + "...")
    s.listen(1)
    c, addr = s.accept()
    connections.append(c)
    addresses[c] = addr
    print("Connection established with", addr)
    tc = threading.Thread(target = threaded_client, args = (c, addr))
    tc.start()

def process_command(message, c, addr):
    global admin
    message = message[1:]
    params = message.split(" ")
    command = params[0]
    params = params[1:]
    server_response = ""
    response = ""
    if command == "nick":
        if params:
            nick = " ".join(x for x in params).strip()
            if nick not in illegal_nicks:
                try:
                    prev_nick = nicks[addr]
                except:
                    prev_nick = ""
                if " " not in nick:
                    if admin == [c, addr]:
                        nicks[addr] = "[ADMIN] " + nick
                    else:
                        nicks[addr] = nick
                    server_command(c, "$%server%^mod%^widget%^nick%^label%^text%^{}".format(nick))
                    if prev_nick:
                        response = "{} changed nickname to {}".format(prev_nick, nick)
                        print("{} changed nickname to {}".format(prev_nick, nick))
                    else:
                        response = "{} joined the server.".format(nick)
                        print("{} joined the server.".format(nick))
                else:
                    server_response = "Names cannot contain spaces."
                    print("Warning issued to {}: \"Names cannot contain spaces.\"")
            else:
                print(c, "nick change blocked. (Value: \"{}\")".format(nick))
                server_response = "Nickname change denied."
        else:
            server_response = "Invalid parameters. /nick (name)"
    elif command == "kick":
        if params:
            if admin == [c, addr]:
                target = params[0]
                for connection in connections:
                    a = addresses[connection]
                    if nicks[a].lower() == target.lower():
                        kick(connection)
                        break
            else:
                server_response = "Access denied."
        else:
            server_response = "Invalid parameters. /kick (name)"
    elif command == "kickall" and admin == [c, addr]:
        for connection in connections:
            if connection not in admin:
                kick(connection)
        server_response = "All clients have been removed from the session."
    elif command == "$dev_admin on":
        admin = [c, addr]
        server_response = "You are now an administrator."
    elif command == "$dev_admin off":
        admin = []
        server_response = "You are no longer an administrator."
    elif command == "list":
        for index, nick in enumerate(list(nicks.values())):
            num = index+1
            server_response += nick + ", "
            if num % 3 == 0:
                server_response += "\n"
    elif command == "msg":
        message = " ".join(x for x in params[1:])
        recipient = params[0]
        server_response = "Message failed to send. {} could not be found.".format(recipient)
        for conn in connections:
            if nicks[addresses[conn]] == recipient:
                recipient = conn
                broadcast(message, sender = c, targets = [recipient], private = True)
                server_response = "Message sent."
        
    if response:
        broadcast(response, sender=c, server_msg = True)
    if server_response:
        direct_msg(server_response, c)

def direct_msg(message, target):
    try:
        target.send(message.encode())
    except socket.error:
        kick(target)

def server_command(c, message):
    try:
        c.send(message.encode())
    except socket.error as e:
        kick(c)

def kick(c):
    c.close()
    connections.remove(c)
    try:
        print("{} \"{}\" disconnected.".format(addresses[c], nicks[addresses[c]]))
        broadcast("{} \"{}\" disconnected.".format(addresses[c], nicks[addresses[c]]), server_msg = True)
    except KeyError:
        print("{} disconnected.".format(addresses[c]))
        broadcast("{} disconnected.".format(addresses[c]), server_msg = True)

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
                print("{} \"{}\": \"{}\"".format(addr, nicks[addr], message))
            except:
                print("{}: \"{}\"".format(addr, message))
            process_command(message, c, addr)
        else:
            print(str(addr), "\"{}\":".format(nicks[addr]), "\"{}\"".format(message))
            broadcast(message, sender=c)
    kick(c)

def broadcast(message, sender = None, server_msg=False):
    original = message
    time = datetime.datetime.now().strftime('%H:%M:%S')
    with open("chatlog.txt", "a") as f:
        if not server_msg:
            message = "[" + time + "] " + nicks[addresses[sender]] + ": " + original
        else:
            message = "[" + time + "] " + original
        f.write(message + "\n")
    for connection in connections:
        if not server_msg and sender != None:
            message = "[" + time + "] " + nicks[addresses[sender]] + ": " + original
        else:
            message = "[" + time + "] [SERVER]: " + original
        try:
            connection.send(message.encode())
        except socket.error as e:
            kick(connection)

connections = []
addresses = {}
nicks = {}
illegal_nicks = ["", " ", "<", ">"]
admin = []
if __name__ == "__main__":
    server = socket.gethostbyname(socket.gethostname())#"10.13.9.89" # MCS IP Address
    print("IP Address:", server)
    port = 45010
    data_buff = 4096
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((server, port))
    
    num_conn = 100
    for x in range(num_conn):
        listen(s)
    print("The server has stopped accepting connections.")
