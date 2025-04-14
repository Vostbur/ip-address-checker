import subprocess
import os
from tkinter import *
from tkinter import ttk, messagebox, filedialog, simpledialog


class IPCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Address Checker")
        self.root.geometry("600x400")

        self.ip_list = []
        self.current_file = None

        self.create_widgets()

    def create_widgets(self):
        # Frame for IP list and buttons
        list_frame = Frame(self.root)
        list_frame.pack(pady=10, padx=10, fill=BOTH, expand=True)

        # IP list with scrollbar
        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.ip_listbox = Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=SINGLE)
        self.ip_listbox.pack(fill=BOTH, expand=True)

        scrollbar.config(command=self.ip_listbox.yview)

        # Buttons frame
        button_frame = Frame(self.root)
        button_frame.pack(pady=5, fill=X)

        # Action buttons
        Button(button_frame, text="Add IP", command=self.add_ip).pack(side=LEFT, padx=5)
        Button(button_frame, text="Edit IP", command=self.edit_ip).pack(side=LEFT, padx=5)
        Button(button_frame, text="Delete IP", command=self.delete_ip).pack(side=LEFT, padx=5)
        Button(button_frame, text="Check All", command=self.check_all_ips).pack(side=LEFT, padx=5)

        # File operations frame
        file_frame = Frame(self.root)
        file_frame.pack(pady=5, fill=X)

        Button(file_frame, text="New File", command=self.new_file).pack(side=LEFT, padx=5)
        Button(file_frame, text="Open File", command=self.open_file).pack(side=LEFT, padx=5)
        Button(file_frame, text="Save", command=self.save_file).pack(side=LEFT, padx=5)
        Button(file_frame, text="Save As", command=self.save_file_as).pack(side=LEFT, padx=5)

        # Status bar
        self.status_var = StringVar()
        self.status_var.set("Ready")
        status_bar = Label(self.root, textvariable=self.status_var, bd=1, relief=SUNKEN, anchor=W)
        status_bar.pack(side=BOTTOM, fill=X)

    def add_ip(self):
        ip = simpledialog.askstring("Add IP", "Enter IP address:")
        if ip and ip.strip():
            self.ip_list.append(ip.strip())
            self.update_listbox()

    def edit_ip(self):
        selection = self.ip_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an IP to edit")
            return

        index = selection[0]
        old_ip = self.ip_list[index]
        new_ip = simpledialog.askstring("Edit IP", "Edit IP address:", initialvalue=old_ip)
        if new_ip and new_ip.strip():
            self.ip_list[index] = new_ip.strip()
            self.update_listbox()

    def delete_ip(self):
        selection = self.ip_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an IP to delete")
            return

        index = selection[0]
        self.ip_list.pop(index)
        self.update_listbox()

    def update_listbox(self):
        self.ip_listbox.delete(0, END)
        for ip in self.ip_list:
            self.ip_listbox.insert(END, ip)

    def check_all_ips(self):
        if not self.ip_list:
            messagebox.showwarning("Warning", "IP list is empty")
            return

        results = []
        for ip in self.ip_list:
            status = self.ping_ip(ip)
            results.append(f"{ip}: {'Available' if status else 'Unavailable'}")

        result_window = Toplevel(self.root)
        result_window.title("Ping Results")

        text = Text(result_window, wrap=WORD)
        text.pack(fill=BOTH, expand=True, padx=10, pady=10)

        for result in results:
            text.insert(END, result + "\n")

        Button(result_window, text="Close", command=result_window.destroy).pack(pady=5)

    def ping_ip(self, ip):
        try:
            # Параметры ping в зависимости от ОС
            param = '-n' if os.name.lower() == 'nt' else '-c'
            timeout = '-w' if os.name.lower() == 'nt' else '-W'

            # Формируем команду ping
            command = ['ping', param, '2', timeout, '1000', ip]

            # Выполняем команду
            output = subprocess.run(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True,
                                    timeout=5)

            # Анализируем результат
            if os.name.lower() == 'nt':  # Windows
                return "TTL=" in output.stdout or "Reply from" in output.stdout
            else:  # Linux/Mac
                return "1 received" in output.stdout or "64 bytes from" in output.stdout

        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    def new_file(self):
        self.ip_list = []
        self.current_file = None
        self.update_listbox()
        self.status_var.set("New file created")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                self.ip_list = [line.strip() for line in f.readlines() if line.strip()]
                self.current_file = file_path
                self.update_listbox()
                self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def save_file(self):
        if not self.current_file:
            self.save_file_as()
            return

        try:
            with open(self.current_file, "w") as f:
                for ip in self.ip_list:
                    f.write(ip + "\n")
            self.status_var.set(f"Saved: {os.path.basename(self.current_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return

        self.current_file = file_path
        self.save_file()


if __name__ == "__main__":
    root = Tk()
    app = IPCheckerApp(root)
    root.mainloop()