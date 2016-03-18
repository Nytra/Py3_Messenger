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
    print("Connection established with", str(addr))
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
                        response = "{} has disconnected.".format(nicks[a])
                        print("{} \"{}\" has disconnected.".format(a, nicks[a]))
                        break
            else:
                server_response = "Access denied."
        else:
            server_response = "Invalid parameters. /kick (name)"
    elif command == "kickall" and admin == [c, addr]:
        for connection in connections:
            if connection not in admin:
                kick(connection)
        response = "All clients have been removed from the session."
    elif command == "$dev_admin on":
        admin = [c, addr]
        priv_response = "You are now an administrator."
    elif command == "$dev_admin off":
        admin = []
        server_response = "You are no longer an administrator."
    elif command == "/list":
        for index, connection in enumerate(connections):
            num = index+1
            server_response += nicks[addresses[connection]] + ", "
            if num % 3 == 0:
                response += "\n"
    elif command == "/msg":
        message = " ".join(x for x in params[1:])
        recipient = params[0]
        broadcast(message, sender = c, targets = [recipient], private = True)
        
    if response:
        broadcast(response, sender=c, server = True)
    if server_response:
        broadcast(priv_response, targets = [c])

def server_command(c, message):
    try:
        c.send(message.encode())
    except socket.error as e:
        kick(c)

def kick(c):
    c.close()
    connections.remove(c)
    print("{} \"{}\" disconnected.".format(addresses[c], nicks[addresses[c]]))

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
    kick(c)

def broadcast(message, sender = None, targets = [], server=False, private=False):
    time = datetime.datetime.now().strftime('%H:%M:%S')
    with open("chatlog.txt", "a") as f:
        if targets:
            pass
        else:
            if not server:
                message = "[" + time + "] " + nicks[addresses[sender]] + ": " + message
            else:
                message = "[" + time + "] " + message
        f.write(message + "\n")
    for connection in connections:
        if targets:
            if connection in targets:
                try:
                    if private:
                        message = "[" + time + "] " + "[Private] " + nicks[addresses[sender]] + ": " + message
                    print(message)
                    connection.send(message.encode())
                except socket.error as e:
                    kick(connection)
        else:
            if not server:
                message = "[" + time + "] " + nicks[addresses[sender]] + ": " + message
            else:
                message = "[" + time + "] " + message
            print(message)
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
