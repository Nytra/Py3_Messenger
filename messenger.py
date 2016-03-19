# TCP Chat Client__author__ = "Sam Scott"__email__ = "samueltscott@gmail.com"# Created on 16-03-2016import socket, threading, random, winsoundfrom tkinter import *class App(Frame):    version = 0.65    def __init__(self, master):        super(App, self).__init__(master)        with open("servers.txt", "r") as f:            servers = f.readlines()        if len(servers) >= 1:            print("Servers you have connected to")            printed_ip = []            for ip in servers:                if ip not in printed_ip:                    print(ip)                    printed_ip.append(ip)        self.server = input("\nEnter an IP address: ").strip()        self.port = ""        print("Enter a port number: ", end = "")        while not self.port:            try:                self.port = int(input())            except ValueError:                print("Enter integers only: ", end = "")                pass        self.name = ""        print("Enter your name: ", end = "")        while not self.name:            self.name = input().strip()            if " " in self.name:                print("Your name cannot contain spaces: ", end = "")                self.name = ""                continue        if not self.name:            self.name = "Anonymous" + str(random.randrange(1, 10000))        self.grid()        self.sound = True        self.data_buff = 4096        if not self.connect():            #print("Unable to connect to", self.server, "on port", str(self.port), "\nClosing program...")            quit()        with open("servers.txt", "a") as f:            f.write(self.server + ":" + str(self.port) + "\n")        s.send("/nick {}".format(self.name).encode())        self.create_widgets()        t1 = threading.Thread(target = self.get_messages)        t1.start()    def __str__(self):        rep = "Chat Instance\nServer: " + self.server + "\nPort: " + str(self.port) + "\nVersion: " + str(self.version)        return rep    def create_widgets(self):        self.nick_lbl = Label(self, text = "Nickname: " + self.name, bg = "black", fg = "white")        self.nick_lbl.grid(row = 0, column = 1, sticky = N)        #self.message_lbl = Label(self, text = "Message: ", bg = "black", fg = "white")        #self.message_lbl.grid(row = 1, column = 0, sticky = W)        self.message_output = Text(self, width = 100, height = 40, wrap = WORD)        self.message_output.grid(row = 0, column = 0, sticky = W)        self.message_input = Entry(self, width = 130)        self.message_input.grid(row = 1, column = 0, sticky = W)        self.submit_bttn = Button(self, text = "Send", command = self.submit_message, bg = "white", fg = "black")        self.submit_bttn.grid(row = 1, column = 0, sticky = E)        self.message_output.config(state=DISABLED)        root.bind('<Return>', self.enter)        self.mute_button = Button(self, text = "Notifications: Enabled", command = self.toggle_sound, bg = "darkgreen", fg = "white")        self.mute_button.grid(row = 0, column = 2, sticky = "N")    def enter(self, event):        self.submit_message()    def toggle_sound(self):        if self.sound == True:            self.mute_button["text"] = "Notifications: Disabled"            self.sound = False        else:            self.mute_button["text"] = "Notifications: Enabled"            self.sound = True    def submit_message(self):        message = self.message_input.get().strip()        if not message:            self.message_input.delete(0, END)            return        #message = self.name + "> " + message        data = message.encode()        s.send(data)        self.message_input.delete(0, END)    def insert_message(self, message):        log = self.message_output.get("1.0", END)        log = log + message        if self.sound:            tbeep = threading.Thread(target = winsound.Beep, args = (600, 100))            tbeep.start()        self.message_output.config(state=NORMAL)        self.message_output.delete("1.0", END)        self.message_output.insert("1.0", log)        self.message_output.config(state=DISABLED)        self.message_output.yview("moveto", 1)    def server_command(self, message):        parts = message.split("%^")        if parts[0] == "$%server":            if parts[1] == "mod":                if parts[2] == "widget":                    if parts[3] == "nick":                        if parts[4] == "label":                            if parts[5] == "text":                                try:                                    temp = self.nick_lbl["text"]                                    self.nick_lbl["text"] = "Nickname: " + " ".join(x for x in parts[6:])                                except:                                    self.nick_lbl["text"] = temp    def get_messages(self):        while True:            data = s.recv(self.data_buff)            if not data:                break            decoded = data.decode("utf-8")            try:                if decoded[:8] != "$%server":                    self.insert_message(decoded)                else:                    self.server_command(decoded)            except IndexError:                self.insert_message(decoded)        s.close()        self.insert_message("Connection Lost.")    def connect(self):        print("Attempting to connect to", self.server, "on port", self.port)        try:            s.connect((self.server, self.port))            print("Connection established.")            return True        except Exception as e:            print(e)            return False                try:    with open("servers.txt", "r") as r:        r.read()except IOError:    with open("servers.txt", "w") as f:        passs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)root = Tk()app = App(root)app.configure(background = "black")root.configure(background = "black")root.title("Messenger V{}".format(str(App.version)))#root.geometry("1280x720")root.mainloop()