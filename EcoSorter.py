import tkinter as tk
from tkinter import messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TrashSortingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("EcoSorter")
        self.master.geometry("800x600")
        self.master.configure(bg="white")

        self.create_database()
        self.create_gui()

    def create_database(self):
        self.conn = sqlite3.connect("trash_sorting_app.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                ecocoins INTEGER DEFAULT 0,
                trash_collected INTEGER DEFAULT 0,
                trash INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def create_gui(self):
        self.label = tk.Label(self.master, text="Регистрация", font=("Helvetica", 20), bg="white")
        self.label.pack(pady=20)

        self.username_label = tk.Label(self.master, text="Логин:", bg="white")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack()

        self.password_label = tk.Label(self.master, text="Пароль:", bg="white")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self.master, text="Войти", command=self.login, bg="green", fg="white",
                                      relief=tk.GROOVE)
        self.login_button.pack(pady=10)

        self.register_button = tk.Button(self.master, text="Зарегистрироваться", command=self.register, bg="black", fg="white",
                                         relief=tk.GROOVE)
        self.register_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = self.cursor.fetchone()

        if user:
            messagebox.showinfo("Успешно", f"Добро пожаловать, {username}!")
            self.show_dashboard(username)
        else:
            messagebox.showerror("Ошибка", "Неправильное имя пользователя или пароль")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Пожалуйста, введите имя пользователя и пароль")
            return

        self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()

        messagebox.showinfo("Успешно", "Регистрация прошла успешно! Теперь вы можете войти.")

    def show_dashboard(self, username):
        dashboard = tk.Toplevel(self.master)
        dashboard.title("Карта сортировки мусора")
        dashboard.geometry("800x600")
        dashboard.configure(bg="white")

        self.plot_map(dashboard)

        collect_button = tk.Button(dashboard, text="Взять мусор", command=self.collect_trash,
                                   bg="green",
                                   fg="white",
                                   relief=tk.GROOVE)
        collect_button.pack(pady=10)

        dispose_button = tk.Button(dashboard, text="Утилизировать мусор", command=self.dispose_trash, bg="red",
                                   fg="white",
                                   relief=tk.GROOVE)
        dispose_button.pack(pady=10)

        profile_button = tk.Button(dashboard, text="Профиль", command=lambda: self.show_profile(username), bg="black",
                                   fg="white", relief=tk.GROOVE)
        profile_button.place(x=700, y=10)

    def plot_map(self, dashboard):
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.scatter([1.50, 2.75, 1.25], [4.50, 5, 5.75], color='blue')
        ax.set_title("Пункты сбора мусора")
        canvas = FigureCanvasTkAgg(fig, master=dashboard)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()

    def collect_trash(self):
        username = self.username_entry.get()
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()
        if user and len(user) >= 6:
            new_trash_collected = user[4] + 1
            new_trash = user[5] + 1
            self.cursor.execute("UPDATE users SET trash_collected = ?, trash = ? WHERE username = ?",
                                (new_trash_collected, new_trash, username))
            self.conn.commit()

            messagebox.showinfo("Успешно", "Мусор собран!Отнесите мусор.")
        else:
            messagebox.showerror("Ошибка", "Пользователь не найден или информация о пользователе неполная.")

    def dispose_trash(self):
        username = self.username_entry.get()
        self.cursor.execute("SELECT * FROM users WHERE username = ?",
                            (username,))
        user = self.cursor.fetchone()
        if user and len(user) >= 6 and user[5] > 0:
            new_ecocoins = user[3] + user[5]
            self.cursor.execute("UPDATE users SET ecocoins = ?, trash = 0 WHERE username = ?",
                                (new_ecocoins, username))
            self.conn.commit()

            messagebox.showinfo("Успешно", f"{user[5]} мусора вывезены! Добавлены экокоины.")
            self.show_profile(username)
        elif user and len(user) >= 6 and user[5] == 0:
            messagebox.showinfo("Информация", "Нет мусора, который нужно выбрасывать.")
        else:
            messagebox.showerror("Ошибка", "Пользователь не найден или информация о пользователе неполная.")

    def show_profile(self, username):
        profile_window = tk.Toplevel()
        profile_window.title("Профиль")
        profile_window.geometry("300x200")
        profile_window.configure(bg="white")

        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()

        if user:
            label_username = tk.Label(profile_window, text=f"Логин: {user[1]}", bg="white")
            label_username.pack(pady=10)
            label_ecocoins = tk.Label(profile_window, text=f"Экокоины: {user[3]}", bg="white")
            label_ecocoins.pack(pady=10)
        else:
            messagebox.showerror("Ошибка", "Пользователь не найден.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TrashSortingApp(root)
    root.mainloop()
