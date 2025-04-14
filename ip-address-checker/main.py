import subprocess
import os
from tkinter import *
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter.font import Font


class IPCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Address Checker")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        # Настройка стилей
        self.setup_styles()

        self.ip_list = []
        self.current_file = None

        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')  # Можно попробовать 'alt', 'default', 'vista'

        # Настройка цветов
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', font=('Segoe UI', 9), padding=6)
        style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 9))
        style.configure('Listbox', font=('Segoe UI', 10), background='white')

        # Стиль для кнопок действий
        style.map('Action.TButton',
                  foreground=[('active', 'white'), ('!active', 'white')],
                  background=[('active', '#45a049'), ('!active', '#4CAF50')])

        # Стиль для кнопок файлов
        style.map('File.TButton',
                  foreground=[('active', 'white'), ('!active', 'white')],
                  background=[('active', '#3a7ebf'), ('!active', '#4285F4')])

        # Стиль для статусбара
        style.configure('Status.TLabel', background='#e0e0e0', relief='sunken', padding=5)

    def create_widgets(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=BOTH, expand=True)

        # Панель инструментов
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=X, pady=(0, 10))

        # Кнопки файловых операций
        ttk.Button(toolbar, text="New File", command=self.new_file, style='File.TButton').pack(side=LEFT, padx=2)
        ttk.Button(toolbar, text="Open File", command=self.open_file, style='File.TButton').pack(side=LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_file, style='File.TButton').pack(side=LEFT, padx=2)
        ttk.Button(toolbar, text="Save As", command=self.save_file_as, style='File.TButton').pack(side=LEFT, padx=2)

        # Основная область
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=True)

        # Список IP с заголовком
        list_frame = ttk.LabelFrame(content_frame, text="IP Address List", padding=10)
        list_frame.pack(fill=BOTH, expand=True)

        # Список IP с прокруткой
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.ip_listbox = Listbox(list_frame,
                                  yscrollcommand=scrollbar.set,
                                  selectmode=SINGLE,
                                  font=('Segoe UI', 10),
                                  bg='white',
                                  relief='solid',
                                  borderwidth=1)
        self.ip_listbox.pack(fill=BOTH, expand=True)

        scrollbar.config(command=self.ip_listbox.yview)

        # Панель кнопок действий
        action_frame = ttk.Frame(content_frame, padding=(0, 10, 0, 0))
        action_frame.pack(fill=X)

        ttk.Button(action_frame, text="Add IP", command=self.add_ip, style='Action.TButton').pack(side=LEFT, padx=2)
        ttk.Button(action_frame, text="Edit IP", command=self.edit_ip, style='Action.TButton').pack(side=LEFT, padx=2)
        ttk.Button(action_frame, text="Delete IP", command=self.delete_ip, style='Action.TButton').pack(side=LEFT, padx=2)
        ttk.Button(action_frame, text="Check All", command=self.check_all_ips, style='Action.TButton').pack(side=LEFT, padx=2)

        # Статус бар
        self.status_var = StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root,
                               textvariable=self.status_var,
                               style='Status.TLabel',
                               anchor='center')
        status_bar.pack(side=BOTTOM, fill=X)

    def add_ip(self):
        ip = simpledialog.askstring("Add IP", "Enter IP address:")
        if ip and ip.strip():
            self.ip_list.append(ip.strip())
            self.update_listbox()
            self.status_var.set(f"Added IP: {ip.strip()}")

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
            self.status_var.set(f"Updated IP: {old_ip} → {new_ip.strip()}")

    def delete_ip(self):
        selection = self.ip_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an IP to delete")
            return

        index = selection[0]
        deleted_ip = self.ip_list.pop(index)
        self.update_listbox()
        self.status_var.set(f"Deleted IP: {deleted_ip}")

    def update_listbox(self):
        self.ip_listbox.delete(0, END)
        for ip in self.ip_list:
            self.ip_listbox.insert(END, ip)

    def check_all_ips(self):
        if not self.ip_list:
            messagebox.showwarning("Warning", "IP list is empty")
            return

        results = []
        total = len(self.ip_list)
        available = 0

        # Создаем окно прогресса
        progress_window = Toplevel(self.root)
        progress_window.title("Checking IPs...")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)

        Label(progress_window, text="Checking IP addresses...").pack(pady=5)
        progress_var = DoubleVar()
        progress = ttk.Progressbar(progress_window, variable=progress_var, maximum=total)
        progress.pack(fill=X, padx=10, pady=5)

        # Обновляем UI
        progress_window.update()

        for i, ip in enumerate(self.ip_list):
            status = self.ping_ip(ip)
            if status:
                available += 1
            results.append(f"{ip}: {'✓ Available' if status else '✗ Unavailable'}")
            progress_var.set(i+1)
            progress_window.update()

        progress_window.destroy()

        # Показываем результаты
        result_window = Toplevel(self.root)
        result_window.title(f"Ping Results ({available}/{total} available)")
        result_window.geometry("500x400")

        # Используем Treeview для красивого отображения
        tree = ttk.Treeview(result_window, columns=('status',), show='headings')
        tree.heading('#0', text='IP Address')
        tree.heading('status', text='Status')

        # Настраиваем цвета строк
        tree.tag_configure('available', background='#e8f5e9')
        tree.tag_configure('unavailable', background='#ffebee')

        for result in results:
            ip, status = result.split(': ')
            tag = 'available' if '✓' in status else 'unavailable'
            tree.insert('', 'end', text=ip, values=(status,), tags=(tag,))

        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Кнопка закрытия
        ttk.Button(result_window, text="Close", command=result_window.destroy, style='Action.TButton').pack(pady=5)

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
                                    timeout=5,
                                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

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
                self.status_var.set(f"Loaded: {os.path.basename(file_path)} ({len(self.ip_list)} IPs)")
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
            self.status_var.set(f"Saved: {os.path.basename(self.current_file)} ({len(self.ip_list)} IPs)")
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