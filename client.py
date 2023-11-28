import socket
import threading
import random
import tkinter as tk

class Client():
    def __init__(self, host, port, color,gui):
        self.host = host
        self.port = port
        self.color = color
        self.gui = gui
        self.nickname = None
        self.chat_window = None
        self.nickname_list = []
        
        # set up socket
    def start_client(self, nickname):
        try:
            self.nickname = nickname
            print(self.nickname)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"[*] connected to {self.host} : {self.port}")
            self.running = True

            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()

            self.chat_window = self.gui.chat_window
            self.chat_window.root.mainloop()
        except Exception as e:
            print(f"[!] error start client: {e}")
            self.running = False  
        

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                print(message)
                message = message.split(';')
                if message[0] == 'login':
                    #self.sock.send(self.nickname.encode('utf-8'))
                    for name in message[1:]:
                        if self.nickname == name:
                            self.nickname = self.nickname + '%'
                        self.nickname_list.append(name)
                    self.nickname_list.append(self.nickname)
                    self.sock.send(self.nickname.encode('utf-8'))
                    print("mengirim nickname")   
                    #print(self.nickname)
                #     print(self.nickname_list)                
                elif message[0] == 'list':
                    #print(message)
                    self.nickname_list = []
                    for name in message[1:]:
                        self.append_nickname_list(name)
                    #print(self.nickname_list)
                    self.update_client_list()
                elif message[0] == 'client':
                    #print(message)
                    self.gui.chat_window.broadcast_new_client(message)
                elif message[0] == 'kirim':
                    print(message)
                    cek = self.nickname_list.index(self.nickname)
                    print(message[3])
                    if message[3] == str(cek): #private message
                        self.gui.chat_window.insert_private_message(message)
                    elif message[1] == self.nickname:
                        self.gui.chat_window.insert_message(message)
                    elif message[3] == "0":
                        self.gui.chat_window.insert_message(message)
                    else:
                        pass # target message is not private/all
                elif message[0] == 'img':
                    print(message)
                    cek = self.nickname_list.index(self.nickname)
                    if message[3] == "0": # ALL
                        self.gui.chat_window.insert_image(message)
                    elif message[3] == str(cek): # private
                        print(f"{self.nickname} mendapatkan private")
                        self.gui.chat_window.insert_private_image(message)
                    elif message[1] == self.nickname: # receive private
                        self.gui.chat_window.insert_image(message)
                    else:
                        pass
            except Exception as e:
                print(f"Error receive message: {e}")
                self.sock.close()
                break

    def send_message(self, message):
        message = f"kirim;{self.nickname};{message};{self.color}" #kirim;nickname;msg;target;color
        print(message)
        self.sock.send(message.encode('utf-8'))

    def send_img(self, img_path):
        message = f"img;{self.nickname};{img_path};{self.color}" #img;nickname;img_path;target;color
        self.sock.send(message.encode('utf-8'))

    def stop_client(self):
        self.running = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except Exception as e:
            print(f"Error stopping client: {e}")

    def append_nickname_list(self, name):
        if name not in self.nickname_list:
            self.nickname_list.append(name)

    def update_client_list(self):
        self.chat_window.listbox.delete(0, tk.END)
        for client in self.nickname_list:
            #print(client)
            name = client.replace('%','')
            self.gui.chat_window.listbox.insert(tk.END, name)

host = 'localhost'
port = 3000

