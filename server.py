import socket
import threading
import time
import os
import tkinter as tk
import subprocess

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__(daemon=True, target=self.listen)
        self.host = host
        self.port = port
        self.client_list = ['null']
        self.nickname_list = ['ALL']
        #self.image_paths = []
        self.shutdown = False
        self.server = None

        # create socket / server
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(10)
            self.start()
            print('type "quit" to close the server!')
            print("=" * 35)
            print(f"[*] listening as {self.host} : {self.port}")
            print("[*] waiting for client to connect")
        except Exception as e:
            print(f"[!] Error create socket: {e}")

    # method for listening to clients
    def listen(self):
        while not self.shutdown:
            client, addr = self.server.accept()
            print(f"[+] {addr} is connected!")

            # if the client is not in client_list (new client)
            if client not in self.client_list:
                message = "login;" + ";".join(self.nickname_list)
                client.send(message.encode('utf-8'))  # send signal login to client
                print(message)
                print(f"mengirim sinyal login")
                nickname = client.recv(1024).decode('utf-8')
                print(f"test: {nickname}")
                self.nickname_list.append(nickname)
                print(f"[+] {nickname} has joined the server")
                # send nickname list to new client

                self.broadcast(f"client;{nickname} has joined the chat!".encode('utf-8'))
                self.client_list.append(client)
                client.send("client;Connected to the server coba deh!".encode('utf-8'))  # [['client],[]],

                self.send_nickname_list()

                threading.Thread(target=self.handle_client, args=(client,)).start() #thread for handle client

                threading.Thread(target=self.window) #thread window for server

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                print(message)
                if not message:
                    break

                message_parts = message.split(";")
                if message_parts[0] == "img":
                    message = self.process_image(message_parts)

                # client_name = self.nickname_list[self.client_list.index(client)]
                message = f"{message}"
                self.broadcast(message.encode('utf-8'))

            except ConnectionResetError:
                break
            except Exception as e:
                print(f"[!] Error handle client: {e}")
                break
        self.remove_client(client)

    def process_image(self, message):
        try:
            with Image.open(message[2]) as img:
                png_temp_path = os.path.join({path}/images",
                                             os.path.basename(message[2]).replace(os.path.splitext(message[2])[1],
                                                                                   '.png')).replace("\\", "/")
                message = f"{message[0]};{message[1]};{png_temp_path};{message[3]};{message[4]}"
                img.save(png_temp_path, format="PNG")
                return message
        except Exception as e:
            print(f"[!] Error process image: {e}")

    def remove_client(self, client):
        if client in self.client_list:
            index = self.client_list.index(client)
            nickname = self.nickname_list[index]
            self.client_list.remove(client)
            self.nickname_list.remove(nickname)
            self.send_nickname_list()
            print(f"[-] {nickname} disconnected from the server")
            self.broadcast(f"client;{nickname} has left the chat.\n".encode('utf-8'))
            client.close()

    def stop_server(self):
        self.shutdown = True
        print("[!] server disconnected!")
        self.server.close()

    def send_nickname_list(self):
        print("mengirim send signal list")
        nickname_list_message = 'list;' + ';'.join(self.nickname_list)  # list;reyhan;agus;dfsafs
        print(nickname_list_message)
        self.broadcast(nickname_list_message.encode('utf-8'))

    def broadcast(self, msg):
        for client in self.client_list:
            try:
                client.send(msg)
            except AttributeError as e:
                pass
            except Exception as e:
                print(f"[!] Error broadcast: {e}")

    def window(self):
        self.root = tk.Tk()
        self.root.config(bg="#282b30")
        self.root.geometry("300x100")
        self.root.resizable(height=False, width=False)
        self.root.title("Tambah User")
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.label1 = tk.Label(self.root, text="GigglyTalk", font=("Georgia", 15, "bold"), bg="#282b30", fg="#FFF")
        self.label2 = tk.Label(self.root, text="Silakan tambah user!", bg="#282b30", fg="#FFF")
        self.button = tk.Button(self.root, text="Add", command=self.add_new_client, bg="#0d6efd", fg="#FFF")
        self.label1.pack(anchor='center', ipady=5)
        self.label2.pack(anchor='center')
        self.button.pack(anchor='center')

        self.root.mainloop()

    def add_new_client(self):
        path = "gui.py"
        addNewClient = subprocess.Popen(["python",path])

    def on_window_close(self):
        self.stop_server()
        self.root.destroy()

host = 'localhost'
port = 3000

server = Server(host=host, port=port)

while True:
    server.window()
    msg = input()
    if msg == 'quit' or msg == 'QUIT' or msg == 'Quit':
        server.stop_server()
        break
