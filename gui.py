import tkinter as tk
from tkinter import scrolledtext, filedialog, PhotoImage
from client import Client, host, port
import random

color_list = ['#ff2400','yellow','#32cd32','#00bfff', 'cornflowerblue', 'cyan3', '#bca7e8', '#ee5921', '#efe0cd', '#f78fa7']

class GUI:
    def __init__(self,host,port,color):
        self.client = Client(host,port,color,self)
        self.login_window = None
        self.chat_window = None
        self.run()

    def show_login_window(self):
        self.login_window = LoginWindow(self)
        return self.login_window.nickname

    def get_chat_window(self, nickname, client):
        self.chat_window = ChatWindow(self, nickname, client)
        return self.chat_window

    def run(self):
        nickname = self.show_login_window()
        self.chat_window = ChatWindow(self, nickname, self.client)
        self.client.start_client(nickname)

class Window:
    def __init__(self, title):
        self.root = tk.Tk()
        self.root.config(bg="#282b30")
        self.root.resizable(height=False, width=False)
        self.root.title(title)

class ChatWindow(Window):
    def __init__(self,gui, nickname, client):
        super().__init__("GigglyTalk")
        self.client = client
        self.nickname = nickname
        self.judul = None
        self.label_nama = None
        self.button = None
        self.text_area = None
        self.input_area = None
        self.target = None
        self.image_paths = []

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        self.build_window()

    def build_window(self):
        self.judul = tk.Label(self.root, text='GigglyTalk', font=('Georgia',20,'bold'), bg="#282b30", fg="#0d6efd")
        self.judul.pack(anchor='nw', padx=20)

        self.label_nama = tk.Label(self.root, text=f"Selamat Datang {self.nickname}", font=('Arial',10,'bold'), bg="#282b30", fg="#FFF")
        self.label_nama.pack(anchor='nw', padx=20)

        self.frame = tk.Frame(self.root, bg="#282b30")
        self.frame.pack(anchor='nw', padx=15, pady=1)

        self.text_area = scrolledtext.ScrolledText(self.frame, width=70, height=20, state='disabled', bg="#424549", fg="#FFF")
        self.text_area.grid(row=0, column=0, padx=10)

        self.frame2 = tk.Frame(self.frame, bg="#282b30")
        self.frame2.grid(row=0, column=1)

        self.active_users = tk.Label(self.frame2, text="Active Users", font=("Georgia", 10, 'bold'), bg="#282b30", fg="#FFF")
        self.active_users.grid(row=0, column=0)
        self.listbox = tk.Listbox(self.frame2, selectmode=tk.SINGLE, width=20, height=19, bg="#424549", fg="#FFF")
        self.listbox.grid(row=1, column=0, padx=10)

        self.img_button = tk.Button(self.root, width=3, text="image", bg="#0d6efd", fg="#FFF", command=self.send_img)
        self.img_button.pack(side=tk.LEFT, anchor=tk.NE ,padx=1, pady=15)


        self.input_area = tk.Entry(self.root, width=79)
        self.input_area.focus_set()
        self.input_area.pack(side=tk.LEFT, anchor=tk.NE ,padx=25, pady=15)
        self.input_area.bind('<Return>', self.send_message)

        self.button = tk.Button(self.root, text='Send', width=8, bg="#0d6efd", fg="#FFF")
        self.button.pack(side=tk.LEFT, anchor=tk.NE, pady=12)
        self.button.bind('<Button-1>', self.send_message)

    def send_img(self):
        index_target = self.listbox.curselection()
        if index_target:
            self.target = index_target[0]
        else:
            self.target = 0
        img_path = str(filedialog.askopenfilename(title="SELECT IMAGE")) +";"+ str(self.target)
        self.client.send_img(img_path)

    def insert_private_image(self, message):
        image_path = message[2]
        if image_path not in self.image_paths:
            self.image_paths.append(image_path)
            index = self.image_paths.index(image_path)
        else:
            index = self.image_paths.index(image_path)
        print(f"test {index}")
        index = int(index)
        print(f'{index}')

        self.image_paths[index] = PhotoImage(file=image_path)
        self.image_paths[index] = self.image_paths[index].subsample(3,3)
        name = message[1].replace('%','')

        self.text_area.config(state='normal')
        self.text_area.tag_config(f'{message[1]}:{message[4]}', foreground=f'{message[4]}')
        self.text_area.insert('end',f"="*70)
        self.text_area.tag_config('center',justify='center')
        self.text_area.insert('end',f"\n{name} MENGIRIM ANDA PESAN PRIBADI\n",'center')
        self.text_area.insert('end',f'  {name}\n\n',f'{message[1]}:{message[4]}')
        self.text_area.image_create('end',image=self.image_paths[index])
        self.text_area.insert('end','\n')
        self.text_area.config(state='disabled')

    def insert_image(self, message):
        image_path = message[2]

        if image_path not in self.image_paths:
            self.image_paths.append(image_path)
            index = self.image_paths.index(image_path) # ambil index terakhir
        else:
            index = self.image_paths.index(image_path) # ambil index yang sesuai dengan path image
        index = int(index)

        self.image_paths[index] = PhotoImage(file=image_path)
        self.image_paths[index] = self.image_paths[index].subsample(5,5)

        self.text_area.config(state='normal')

        if message[1] == self.client.nickname:
            self.text_area.tag_config(f'{message[1]}:{message[4]}', foreground=f'{message[4]}', justify='right')
            self.text_area.tag_configure('right', justify='right')
            self.text_area.insert('end',f"<<  \n\n",f'{message[1]}:{message[4]}')
            self.text_area.insert('end'," ",'right')
            self.text_area.image_create(tk.END, image=self.image_paths[index])
            self.text_area.insert('end',"\n")
        else:
            name = message[1].replace('%', '')
            self.text_area.tag_config(f'{message[1]}:{message[4]}', foreground=f'{message[4]}', justify='left')
            self.text_area.insert('end', f' {name}\n\n', f'{message[1]}:{message[4]}')
            self.text_area.image_create('end', image=self.image_paths[index])
            self.text_area.insert('end',"\n")

        self.text_area.yview(tk.END)
        self.text_area.config(state='disabled', font=("Helvetica", 10, 'bold'))
        print("Insert successful")

    def insert_private_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.tag_config(f'{message[1]}:{message[4]}',foreground=f'{message[4]}')
        self.text_area.insert('end',f"="*70)
        self.text_area.tag_configure('center',justify='center')
        self.text_area.insert('end',f"\n{message[1]} MENGIRIM ANDA PESAN PRIBADI!\n",'center')
        self.text_area.insert('end',f"  {message[1]}\n",f'{message[1]}:{message[4]}')
        self.text_area.insert('end',f"  >> {message[2]}\n")
        self.text_area.config(state='disabled')


    def show_login_window(self):
        login_window = LoginWindow(self)
        return login_window.nickname

    def send_message(self, event):
        message = self.input_area.get()
        index_target = self.listbox.curselection()
        print(index_target)
        if index_target:
            self.target = index_target[0]
        else:
            self.target = 0
        if message != '' and self.client.nickname != self.client.nickname_list[self.target]:
            message = message +';'+ str(self.target)
            self.client.send_message(message)
            self.input_area.delete(0, 'end')
        else:
            self.input_area.delete(0,'end')
            print("tidak bisa mengirim pesan ke diri sendiri")


    def run(self):
        self.root.mainloop()
        self.root.destroy()

    def close_app(self):
        self.client.stop_client()
        self.root.destroy()

    def broadcast_new_client(self,message):
        self.text_area.config(state='normal')
        msg = message[1].replace('%','')
        self.text_area.tag_configure('tengah',justify="center")
        self.text_area.insert('end',msg+'\n','tengah')
        self.text_area.yview(tk.END)
        self.text_area.config(state='disabled')

    def insert_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.tag_config(f'{message[1]}:{message[4]}',foreground=f'{message[4]}')
        if message[1] == self.client.nickname:
            self.text_area.tag_configure('right',justify='right')
            self.text_area.insert('end',f"\n{message[2]} << \n\n",'right')
        else:
            name = message[1].replace('%','')
            self.text_area.insert('end','  '+name,f'{message[1]}:{message[4]}')
            self.text_area.insert('end',f"\n  >> {message[2]}\n\n")
        self.text_area.yview(tk.END)
        self.text_area.config(state='disabled', font=("Halvetica",10,'bold'))

class LoginWindow(Window):
    def __init__(self, gui):
        super().__init__("Login")
        self.gui = gui
        self.label = None
        self.entry = None
        self.button = None
        self.nickname = None

        self.build_window()
        self.run()

    def build_window(self):
        self.root.geometry("300x100")

        self.label1 = tk.Label(self.root, text="Welcome to GigglyTalk", font=("Georgia", 15, "bold"), bg="#282b30", fg="#FFF")
        self.label2 = tk.Label(self.root, text="Silakan masukkan nama anda!", bg="#282b30", fg="#FFF")
        self.label1.pack(expand=tk.YES)
        self.label2.pack(expand=tk.YES)

        self.frame = tk.Frame(self.root, bg="#282b30")
        self.frame.pack()

        self.entry = tk.Entry(self.frame, width=20)
        self.entry.focus_set()
        self.entry.grid(row=0, column=0, sticky=(tk.N + tk.E), padx=10, pady=5)

        self.button = tk.Button(self.frame, text="Login", command=self.get_login_event, bg="#0d6efd", fg="#FFF")
        self.button.grid(row=0, column=1, sticky=(tk.N + tk.E), padx=2, pady=5)
      
    def get_login_event(self, event=None):
        self.nickname = self.entry.get()
        self.root.quit()

    def run(self):
        self.root.mainloop()
        self.root.destroy()

host = 'localhost'
port = 3000
color = random.choice(color_list)

app = GUI(host,port,color)
