import socket
import threading
import time
import tkinter
from tkinter import simpledialog
from tkinter import scrolledtext
import clientFile

HOST = '127.0.0.1'  # local host
PORT = 50000


def bind_theSocket(self):
    for port in range(55000, 55016):
        try:
            self.sock.bind(('', port))
            print(f'The client connected with port {port}')
            return port
        except:
            continue
    print("We're sorry but there is no available port to connected, please try2 later!.\n")


class Client:
    def __init__(self, nickname=None, flag=True):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = bind_theSocket(self)
        self.sock.connect((HOST, PORT))  # connect to the server
        self.flag = flag
        self.udp_C_socket = None
        msg = tkinter.Tk()  # tkinter frame
        msg.withdraw()  # hides the window
        self.gui_done = False
        self.running = True
        self.nickname = nickname
        self.last_message = ""
        if self.flag:
            self.nickname = simpledialog.askstring("Login", "Insert your name", parent=msg)
        self.last_message2 = ""
        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    """"
   Basic chat construction, including a typing window, 
   a chat view and a send button that activates the "sendMessage" function
   and sends the message to all relevant users (ie all those whose checkbox is checked)
    """""

    def gui_loop(self):
        self.COLOR = '#6b88fe'  # ["#" + ''.join([random.choice('ABCDEF0123456789') for i in range(6)])]
        self.win = tkinter.Tk()
        self.win.configure(bg=self.COLOR)

        self.name = tkinter.Label(self.win, text=f"Nickname: {self.nickname}", fg='white', bg=self.COLOR)
        self.name.config(font=("Flux Regular", 18, "bold"))
        self.name.grid(row=0, column=4, columnspan=5, pady=10)

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg=self.COLOR)
        self.chat_label.config(font=("Arial", 14))
        self.chat_label.grid(row=1, column=0, columnspan=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, height=10, width=50)
        self.text_area.config(state='disable')
        self.text_area.grid(row=2, column=0, rowspan=3, columnspan=5, padx=20)

        self.msg_label = tkinter.Label(self.win, text="Your message:", bg=self.COLOR)
        self.msg_label.config(font=("Arial", 14))
        self.msg_label.grid(row=5, column=0, columnspan=5)

        self.input_area = tkinter.Text(self.win, height=6, width=46)
        self.input_area.config(font=("Arial", 12))
        self.input_area.grid(row=6, column=0, rowspan=3, columnspan=5, padx=20)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.grid(row=7, column=6)

        self.send_toUser_button = tkinter.Button(self.win, text="Send to", command=self.write_toUser)
        self.send_toUser_button.config(font=("Arial", 12))
        self.send_toUser_button.grid(row=8, column=6)

        self.nick_input = tkinter.Text(self.win, width=8, height=1.4)
        self.nick_input.grid(row=8, column=7)

        self.onlineUsers_button = tkinter.Button(self.win, text="Online users", command=self.get_onlineUsers)
        self.onlineUsers_button.config(font=("Arial", 12))
        self.onlineUsers_button.grid(row=2, column=6)

        self.files_button = tkinter.Button(self.win, text="Files", command=self.files)
        self.files_button.config(font=("Arial", 12))
        self.files_button.grid(row=3, column=6)

        self.download = tkinter.Button(self.win, text="Download a file", command=self.threadDownload)
        self.download.config(font=("Arial", 11))
        self.download.grid(row=4, column=6)

        self.input_file = tkinter.Text(self.win, width=8, height=1.4)
        self.input_file.grid(row=4, column=7, padx=20)

        tkinter.Label(self.win, text="       ", bg=self.COLOR).grid(row=10, column=0, columnspan=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode())
        self.input_area.delete('1.0', 'end')

    def write_toUser(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(("SENDTOUSER-->" + self.nick_input.get('1.0', 'end') + '|' + message).encode())
        self.input_area.delete('1.0', 'end')

        self.text_area.config(state='normal', font=("Arial", 12))  # the text area is changeable
        self.text_area.insert('end', message)  # to append the message at the end
        self.text_area.yview('end')  # scroll down to the end with the messages
        self.text_area.config(state='disable', font=("Arial", 12))

    def threadDownload(self):
        threading.Thread(target=self.specific_file,).start()

    def specific_file(self):
            file_name = f"{self.input_file.get('1.0', 'end')}"
            file_name = file_name.replace('\n', "")
            self.sock.send(f'FILETODOWNLOAD-->{file_name}'.encode())
            time.sleep(8)
            msg = self.last_message
            if msg == "** File not found **\n":
               return
            else:
                print("found\n")
                msg = (msg.removeprefix("File size = ")).removesuffix("\nDownloading...\n")
                threading.Thread(target=clientFile.udp_file_transfer,
                                 args=(self, file_name, int(msg))).start()  # msg = file size

    def files(self):
        message = f"FILES-->{self.nickname}"
        self.sock.send(message.encode())

    def get_onlineUsers(self):
        message = f"ONLINEUSERS-->{self.nickname}"
        self.sock.send(message.encode())

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    """""
     Receive a message from the server.
     Check whether it is a:
     - Request for a nickname
     - Update on a user's login/exit
     - Normal chat message
     Perform actions according to the classification of the message.
     """""

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode()
                if message.startswith("File size ="):
                    self.last_message = message
                else :
                    self.last_message2 = message
                if message == 'NICK' and self.nickname is not None:
                    self.sock.send(self.nickname.encode())
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal', font=("Arial", 12))  # the text area is changeable
                        self.text_area.insert('end', message)  # to append the message at the end
                        self.text_area.yview('end')  # scroll down to the end with the messages
                        self.text_area.config(state='disable', font=("Arial", 12))
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break
