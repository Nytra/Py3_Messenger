# TCP Chat Server
__author__ = "Sam Scott"
__email__ = "samueltscott@gmail.com"
repo = "https://github.com/Nytra/messenger"
# Created on 16-03-2016

import socket, threading, time, datetime, string

def listen(s):
    global admins, num_conn, nc_const, total_connections
    server_log("[" + time(full=True) + "] " + "listening for connections to " + server + ":" + str(port) + " . . .")
    s.listen(1)
    c, addr = s.accept()
    connections.append(c)
    addresses[c] = addr
    num_conn += 1
    total_connections += 1
    server_log("[" + time(full=True) + "] " + "connection established with " + str(addr) + " [{}/{}]".format(num_conn, nc_const))
    tc = threading.Thread(target = threaded_client, args = (c, addr))
    tc.start()
    server_log("[" + time(full=True) + "] " + "{} thread started successfully.".format(addresses[c]))

def process_command(message, c, addr):
    global admins, num_conn, nc_const, parties, total_connections, show_encrypted
    message = message[1:]
    params = message.split(" ")
    command = params[0]
    params = params[1:]
    server_response = ""
    response = ""
    if command == "nick":
        if params:
            nick = " ".join(x for x in params).strip()
            good = True
            for x in ["[ADMIN]", "[SERVER]"]:
                if x.lower() in nick.lower():
                    good = False
            if good:
                if nick not in illegal_nicks:
                    try:
                        prev_nick = nicks[addr]
                    except:
                        prev_nick = ""
                    if " " not in nick:
                        nicks[addr] = nick
                        server_command(c, "$%server%^mod%^widget%^nick%^label%^text%^{}".format(nick))
                        if prev_nick:
                            response = "{} changed nickname to {}".format(prev_nick, nick)
                            server_log("[" + time(full=True) + "] " + "{} changed nickname to {}".format(prev_nick, nick))
                        else:
                            response = "{} joined the server.".format(nick)
                            server_log("[" + time(full=True) + "] " + "{} joined the server.".format(nick))
                    else:
                        server_response = "Names cannot contain spaces."
                else:
                    server_log("[" + time(full=True) + "] " + str(addr) + " nick change blocked. (Value: \"{}\")".format(nick))
                    server_response = "Nickname change denied."
            else:
                server_log("[" + time(full=True) + "] " + str(addr) + " nick change blocked. (Value: \"{}\")".format(nick))
                server_response = "Nickname change denied."
        else:
            server_response = "Invalid parameters. /nick (name)"
    elif command == "kick":
        if [c, addr] in admins:
            if params:
                target = params[0]
                for connection in connections:
                    a = addresses[connection]
                    if nicks[a].lower() == target.lower():
                        server_log("[" + time(full=True) + "] " + "{} \"{}\" kick command invoked. removing {} \"{}\" from server.".format(addresses[c], nicks[addresses[c]], a, nicks[a]))
                        kick(connection)
                        break
            else:
                server_response = "Invalid parameters. /kick {name}"
        else:
            server_response = "Access denied."
    elif command == "kickall":
        if [c, addr] in admins:
            for connection in connections:
                if [connection, addresses[c]] not in admins:
                    kick(connection)
            server_response = "All clients have been removed from the session."
        else:
            server_response = "Access denied."
    elif command == "$dev_admin":
        if params:
            if params[0] == "1":
                if [c, addr] not in admins:
                    admins.append([c, addr])
                    server_response = "You are now an administrator."
                else:
                    server_response = "You are already an administrator."
            elif params[0] == "0":
                if [c, addr] in admins:
                    admins.remove([c, addr])
                    server_response = "You are no longer an administrator."
                else:
                    server_response = "You are not an administrator."
    elif command == "list":
        for index, nick in enumerate(list(nicks.values())):
            num = index+1
            if num < len(list(nicks.values())):
                server_response += nick + ", "
            else:
                server_response += nick
    elif command == "msg":
        if params:
            message = "[PRIVATE] {}: ".format(nicks[addr]) + " ".join(x for x in params[1:])
            recipient = params[0]
            server_response = "Message failed to send. {} could not be found.".format(recipient)
            for conn in connections:
                if nicks[addresses[conn]] == recipient:
                    recipient = conn
                    direct_msg(message, recipient)
                    server_response = "Message sent."
        else:
            server_response = "You must specify a recipient and a message in the format /msg {recipient} {msg}"
    elif command == "stat":
        server_response = "Connected clients: [{}/{}] - Server running since: [{}] - Number of epileptic seizures: {} - Total number of connections: {}".format(num_conn, nc_const, start_time_full, parties, total_connections)
    elif command == "party":
        server_command(c, "$%server%^do%^party")
        parties += 1
    elif command == "clear":
        server_command(c, "$%server%^do%^clear")
    elif command == "disconnect":
        server_command(c, "$%server%^do%^disconnect")
    elif command == "show_encrypted":
        if [c, addr] in admins:
            if params:
                if params[0] == "1":
                    show_encrypted = True
                    server_response = "Encrypted messages are now shown."
                elif params[0] == "0":
                    show_encrypted = False
                    server_response = "Encrypted messages are now hidden."
                else:
                    server_response = "On: 1, Off: 0"
            else:
                server_response = "/show_encrypted {1, 0}"
        else:
            server_response = "Access denied."
    elif command == "admin":
        found = False
        if [c, addr] in admins:
            if params:
                nick = params[0]
                for conn in connections:
                    if nicks[addresses[conn]] == nick:
                        found = True
                        if [conn, addresses[conn]] not in admins:
                            admins.append([conn, addresses[conn]])
                            message = "You are now an administrator."
                            direct_msg(message, conn)
                        else:
                            server_response = "This person is already an administrator."
                if not found:
                    server_response = "\"{}\" could not be found".format(nick)
        else:
            server_response = "Access denied."
    elif command == "show_admins":
        for index, admin in enumerate(admins):
            num = index+1
            nick = nicks[admin[1]]
            if num < len(admins):
                server_response += nick + ", "
            else:
                server_response += nick
    else:
        server_response = "\"/{}\" is not a valid command.".format(command)
        
    if response:
        broadcast(response, sender=c, server_msg = True)
    if server_response:
        direct_msg(server_response, c)

def direct_msg(message, target):
    try:
        server_log("[{}] {} \"{}\" server direct message: ".format(time(full=True), addresses[target], nicks[addresses[target]]) + message)
    except:
        server_log("[{}] {} server direct message: ".format(time(full=True), addresses[target]) + message)
    message = "[{}] ".format(time()) + message
    message = encrypt(message, 7)
    try:
        target.send(message.encode())
    except socket.error:
        try:
            server_log("[" + time(full=True) + "] " + "{} \"{}\" server direct message failed to send. removing client from server.".format(addresses[c], nicks[addresses[c]]))
        except KeyError:
            server_log("[" + time(full=True) + "] " + "{} server direct message failed to send. removing client from server.".format(addresses[c]))
        kick(target)

def server_command(c, message):
    try:
        try:
            server_log("[" + time(full=True) + "] " + "{} \"{}\" sending server command: {}".format(addresses[c], nicks[addresses[c]], message))
        except KeyError:
            server_log("[" + time(full=True) + "] " + "{} sending server command: {}".format(addresses[c], message))
        message = encrypt(message, 7)
        c.send(message.encode())
    except socket.error as e:
        try:
            server_log("[" + time(full=True) + "] " + "{} \"{}\" server command failed to execute. removing client from server.".format(addresses[c], nicks[addresses[c]]))
        except KeyError:
            server_log("[" + time(full=True) + "] " + "{} server command failed to execute. removing client from server.".format(addresses[c]))
        kick(c)

def kick(c):
    global num_conn, nc_const, admins
    if [c, addresses[c]] in admins:
        admins.remove([c, addresses[c]])
        try:
            server_log("[" + time(full=True) + "] " + "{} \"{}\" removed from admins array.".format(addresses[c], nicks[addresses[c]]))
        except KeyError:
            server_log("[" + time(full=True) + "] " + "{} removed from admins array.".format(addresses[c]))
    try:
        c.close()
        connections.remove(c)
        try:
            server_log("[" + time(full=True) + "] " + "{} \"{}\" removed from connections array.".format(addresses[c], nicks[addresses[c]]))
        except KeyError:
            server_log("[" + time(full=True) + "] " + "{} client removed from connections array.".format(addresses[c]))
    except:
        try:
            server_log("[" + time(full=True) + "] " + "{} \"{}\" attempt to remove client failed. already disconnected?".format(addresses[c], nicks[addresses[c]]))
        except KeyError:
            server_log("[" + time(full=True) + "] " + "{} attempt to remove client failed. already disconnected?".format(addresses[c]))
        return
    num_conn -= 1
    try:
        server_log("[" + time(full=True) + "] " + "{} \"{}\" disconnected.".format(addresses[c], nicks[addresses[c]]) + " [{}/{}]".format(num_conn, nc_const))
        broadcast("{} disconnected.".format(nicks[addresses[c]]), server_msg = True)
    except KeyError:
        server_log("[" + time(full=True) + "] " + "{} disconnected.".format(addresses[c]) + " [{}/{}]".format(num_conn, nc_const))
        #broadcast("{} disconnected.".format(addresses[c]), server_msg = True)
    try:
        del(nicks[addresses[c]])
    except KeyError:
        server_log("[" + time(full=True) + "] " + "{} has no nickname.".format(addresses[c]))

def server_log(message):
    print(str(message))
    with open("serverlog.txt", "a") as f:
        f.write(str(message) + "\n")

def threaded_client(c, addr):
    global show_encrypted
    while True:
        try:
            data = c.recv(data_buff)
        except socket.error as e:
            break
        if not data:
            break
        message = data.decode("utf-8")
        if show_encrypted == True:
            try:
                server_log("[" + time(full=True) + "] " + "{} \"{}\" received encrypted message: \"{}\"".format(addr, nicks[addresses[c]], message))
            except KeyError:
                server_log("[" + time(full=True) + "] " + "{} received encrypted message: \"{}\"".format(addr, message))
        message = decrypt(message, 7)
        if message[0] == "/":
            try:
                server_log("[" + time(full=True) + "] " + "{} \"{}\": \"{}\"".format(addr, nicks[addr], message))
            except:
                server_log("[" + time(full=True) + "] " + "{}: \"{}\"".format(addr, message))
            process_command(message, c, addr)
        else:
            try:
                server_log("[" + time(full=True) + "] " + str(addr) + " \"{}\":".format(nicks[addr]) + " \"{}\"".format(message))
            except KeyError:
                server_log("[" + time(full=True) + "] " + str(addr) + ": \"{}\"".format(message))
            broadcast(message, sender=c)
    try:
        server_log("[" + time(full=True) + "] " + "{} \"{}\" socket error and or null data. removing client from server.".format(addresses[c], nicks[addresses[c]]))
    except KeyError:
        server_log("[" + time(full=True) + "] " + "{} socket error and or null data. removing client from server.".format(addresses[c]))
    kick(c)

def broadcast(message, sender = None, server_msg=False):
    original = message
    if [sender, addresses[sender]] in admins:
        nick = "[ADMIN] " + nicks[addresses[sender]]
    else:
        nick = nicks[addresses[sender]]
    with open("chatlog.txt", "a") as f:
        if not server_msg:
            message = "[" + time(full=True) + "] " + nick + ": " + original
        else:
            message = "[" + time(full=True) + "] " + original
        f.write(message + "\n")
    for connection in connections:
        if not server_msg and sender != None:
            message = "[" + time() + "] " + nick + ": " + original
        else:
            message = "[" + time() + "] " + original
        message = encrypt(message, 7)
        if connection != sender:
            server_command(connection, "$%server%^do%^beep")
        try:
            connection.send(message.encode())
        except socket.error as e:
            try:
                server_log("[" + time(full=True) + "] " + "{} \"{}\" broadcast failed. removing client from server.".format(addresses[c], nicks[addresses[sender]]))
            except KeyError:
                server_log("[" + time(full=True) + "] " + "{} broadcast failed. removing client from server.".format(addresses[c]))
            kick(connection)

def time(full = False, date_only = False):
    if not full and not date_only:
        time = datetime.datetime.now().strftime('%H:%M:%S')
    elif not date_only and full == True:
        time = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    elif not full and date_only == True:
        time = datetime.datetime.now().strftime('%d-%m-%Y')
    return time

def encrypt(message, key):
    alphabet = ['x', '$', 'W', 't', 'D', '|', 'd', " ", 'E', 'N', '`', 'n', 'X', 'h', 'V', 'A',\
         'Y', '5', 'a', '¦', '2', 'J', 'C', 'b', 'k', 'H', 'I', 'c', 'f', 'K', '1', '9', 'u', ':', '3',\
          '#', '%', 'P', 'i', '^', '4', 'O', '(', '[', 'R', '+', 'T', 'o', '@', '&', 'l', 'M', '>', '8',\
           '"', 'Q', '<', '=', '*', '7', 'z', 'v', 'p', 's', 'B', '}', 'G', 'y', ')', '?', '0', '~', '/',\
            "'", 'j', '6', '-', '_', '¬', '£', ',', 'U', 'F', 'Z', 'S', 'g', 'w', 'L', 'e', 'r', 'q', ';',\
             '.', '\\', '!', 'm', ']', '{']
    encrypted = ""
    for char in message:
        index = alphabet.index(char)
        for i in range(key):
            index += 1
            if index > len(alphabet) - 1:
                index = 0
        encrypted += alphabet[index]
    return encrypted

def decrypt(message, key):
    alphabet = ['x', '$', 'W', 't', 'D', '|', 'd', " ", 'E', 'N', '`', 'n', 'X', 'h', 'V', 'A',\
         'Y', '5', 'a', '¦', '2', 'J', 'C', 'b', 'k', 'H', 'I', 'c', 'f', 'K', '1', '9', 'u', ':', '3',\
          '#', '%', 'P', 'i', '^', '4', 'O', '(', '[', 'R', '+', 'T', 'o', '@', '&', 'l', 'M', '>', '8',\
           '"', 'Q', '<', '=', '*', '7', 'z', 'v', 'p', 's', 'B', '}', 'G', 'y', ')', '?', '0', '~', '/',\
            "'", 'j', '6', '-', '_', '¬', '£', ',', 'U', 'F', 'Z', 'S', 'g', 'w', 'L', 'e', 'r', 'q', ';',\
             '.', '\\', '!', 'm', ']', '{']
    encrypted = ""
    for char in message:
        index = alphabet.index(char) - key
        encrypted += alphabet[index]
    return encrypted

connections = []
addresses = {}
nicks = {}
illegal_nicks = ["", " ", ":"]
admins = []
if __name__ == "__main__":
    server = socket.gethostbyname(socket.gethostname()) # "10.13.9.89" # MCS IP Address
    port = 45011
    parties = 0
    total_connections = 0
    show_encrypted = False
    data_buff = 4096 # data buffer
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((server, port))
    except socket.error: # if port 45011 is not available
        s.bind((server, 0)) # chooses a random available port
        port = s.getsockname()[1]
    start_time_date = time(date_only = True)
    start_time_time = time()
    start_time_full = time(full=True)
    server_log("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n[{}] starting server . . .".format(time(full=True)))
    server_log("[{}] IP address: ".format(time(full=True)) + server)
    server_log("[{}] port: ".format(time(full=True)) + str(port))
    
    num_conn = 0
    nc_const = 256 # maximum number of connected users
    printed = False
    server_log("[" + time(full=True) + "] " + "maximum number of simultaneous connections: {}".format(nc_const))
    while True:
        if num_conn >= nc_const:
            if not printed:
                server_log("[" + time(full=True) + "] " + "the server has stopped accepting connections. [{}/{}]".format(num_conn, nc_const))
                printed = True
        else:
            if printed:
                server_log("[" + time(full=True) + "] " + "the server is now accepting connections. [{}/{}]".format(num_conn, nc_const))
            printed = False
            listen(s)
