import tkinter.filedialog as filedialog
import customtkinter
import ncmdump
import os
import multiprocessing

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("Dark")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")

def load_path():
    directory = filedialog.askdirectory()
    return os.path.abspath(directory) if directory!="" else ''

def open_path(path):
    path = os.path.abspath(path.replace('\n', ''))
    os.startfile(path)

def convert(file: str):
    print("start converting" + file)
    ncmdump.dump(os.path.abspath(file))
    print("convert complete")


def update_path(field_path: customtkinter.CTkTextbox, field_ncm: customtkinter.CTkTextbox, field_mp3: customtkinter.CTkTextbox):
    path_text = load_path().replace('\n', '')
    if path_text!='':
        field_path.delete("0.0", customtkinter.END)
        field_mp3.delete("0.0", customtkinter.END)
        field_ncm.delete("0.0", customtkinter.END)
        field_path.insert('0.0', path_text)

        # list_mp3 = list(filter(lambda s: s.endswith('.mp3'), os.listdir(path_text)))
        list_ncm = list(
            filter(lambda s: s.endswith('.ncm'), os.listdir(path_text)))
        # print(list_mp3,list_ncm)
        # [field_mp3.insert(customtkinter.END,s+'\n') for s in list_mp3]
        [field_ncm.insert(customtkinter.END, s+'\n') for s in list_ncm]
    # print(list_mp3, list_ncm)


def transcode(path: str, root, btn):
    path = path.replace('\n', '')
    list_ncm = list(map(lambda s: os.path.join(path, s), filter(
        lambda s: s.endswith('.ncm'), os.listdir(path))))
    # [ncmdump.dump(os.path.abspath(file)) for file in list_ncm]
    btn.configure(state="disabled")
    btn.configure(text='正在转换')
    pool = multiprocessing.Pool(4).map_async(convert, list_ncm)
    schedule_check(pool, root, btn)

def schedule_check(pool, root, btn):
    """
    Schedule the execution of the `check_if_done()` function after
    one second.
    """
    root.after(1000, check_if_done, pool,root, btn)


def check_if_done(pool,root, btn):
    # If the thread has finished, re-enable the button and show a message.
    if pool.ready():
        print("done")
        btn.configure(state="normal")
        btn.configure(text="开始转换")
        return True
    else:
        # Otherwise check again after one second.
        schedule_check(pool, root, btn)

def setup():
    root = customtkinter.CTk()
    root.title("ncm to mp3")
    root.geometry("600x350")

    frame_main = customtkinter.CTkFrame(master=root)
    frame_main.pack(pady=20, padx=30, fill="both", expand=True)

    label = customtkinter.CTkLabel(master=frame_main, text="请选择目录：")
    label.pack(pady=12, padx=10)

    text_path = customtkinter.CTkTextbox(
        master=frame_main, height=14, width=500)
    # text_path.configure(height=14, width=100)
    frame_file = customtkinter.CTkFrame(master=root)
    field_ncm = customtkinter.CTkTextbox(master=frame_file, width=500)
    field_mp3 = customtkinter.CTkTextbox(master=frame_file, width=500)

    text_path.pack(padx=12, pady=10)

    btn_folder = customtkinter.CTkButton(
        master=frame_main, height=10, text="选择文件夹", command=lambda: update_path(text_path, field_ncm, field_mp3))
    btn_folder.pack(pady=12, padx=10)

    btn_trascode = customtkinter.CTkButton(
        master=frame_main, height=10, text="开始转换", )
    btn_trascode.configure(command=lambda: transcode(text_path.get("0.0", customtkinter.END),root=root,btn=btn_trascode))
    btn_trascode.pack(pady=12, padx=10)

    btn_open = customtkinter.CTkButton(
        master=frame_main, height=10, text="打开目录", command=lambda: open_path(text_path.get('0.0', customtkinter.END)))
    btn_open.pack(pady=12, padx=10)
    
    # frame_file.pack(pady=20, padx=60, fill="both", expand=True)
    # field_ncm.pack(padx=12, pady=10)
    # field_mp3.pack(padx=12, pady=10)

    return root


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = setup()
    app.mainloop()
