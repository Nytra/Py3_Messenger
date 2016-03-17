# TCP Chat Client
__author__ = "Sam Scott"
__email__ = "samueltscott@gmail.com"
# Created on 16-03-2016
import socket, threading, random
from tkinter import *

# this program uses a graphical user interface

class App(Frame):
    version = 0.1
    server = input("Enter an IP address: ").strip()
    name = input("Enter your username: ").strip()
    if not name:
        name = "Anonymous" + str(random.randrange(1, 10000))
    port = 45009
    
    def __init__(self, master):
        super(App, self).__init__(master)
        
        self.grid()
        self.data_buff = 4096
        if not self.connect():
            #print("Unable to connect to", App.server, "on port", str(App.port), "\nClosing program...")
            quit()
        self.create_widgets()

        t1 = threading.Thread(target = self.get_messages)
        t1.start()

    def __str__(self):
        rep = "Chat Instance\nServer: " + App.server \
              + "\nPort: " + str(App.port) + "\nVersion: " \
              + str(App.version)
        return rep

    def create_widgets(self):
        self.message_lbl = Label(self, text = "Message: ")
        self.message_lbl.grid(row = 0, column = 0, sticky = W)
        self.message_output = Text(self, width = 40, height = 80, wrap = WORD)
        self.message_output.grid(row = 1, column = 0, sticky = W)
        self.message_input = Entry(self)
        self.message_input.grid(row = 0, column = 1, sticky = W)
        self.submit_bttn = Button(self, text = "Send", command = self.submit_message)
        self.submit_bttn.grid(row = 0, column = 2, sticky = W)

    def submit_message(self):
        message = self.message_input.get().strip()
        if not message:
            self.message_input.delete(0, END)
            return
        message = App.name + "> " + message
        data = message.encode()
        s.send(data)
        self.message_input.delete(0, END)

    def insert_message(self, message):
        log = self.message_output.get("1.0", END)
        log = log + message
        self.message_output.delete("1.0", END)
        self.message_output.insert("1.0", log)
        
    def get_messages(self):
        while True:
            data = s.recv(self.data_buff)
            if not data:
                break
            decoded = data.decode("utf-8")
            self.insert_message(decoded)
        s.close()
        self.insert_message("Connection Lost.")

    def connect(self):
        print("Attempting to connect to", App.server, "on port", App.port)
        try:
            s.connect((App.server, App.port))
            print("Connection established.")
            return True
        except Exception as e:
            print(e)
            input("\nPress enter to continue . . .")
            return False

        
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
root = Tk()
app = App(root)
root.title("Messenger V{}".format(str(App.version)))
root.geometry("512x720")
root.mainloop()

