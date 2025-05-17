import tkinter as tk
from tkinter import filedialog, messagebox, font
from tkinter import ttk


class FileViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Просмотр файла с отметками")

        self.file_path = None
        self.lines = []
        self.marked_lines = set()
        self.current_line = 0

        self.create_widgets()

    def create_widgets(self):
        # Кнопка загрузки файла
        self.load_button = tk.Button(self.root, text="Загрузить файл", command=self.load_file)
        self.load_button.pack(pady=5)

        # Область отображения текущей строки
        self.line_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.line_frame.pack(pady=5, padx=10, fill=tk.X)

        self.line_label = tk.Label(self.line_frame, text="Файл не загружен", justify=tk.LEFT, anchor='w')
        self.line_label.pack(pady=5, padx=5, fill=tk.X)

        # Кнопки навигации
        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack(pady=5)

        self.prev_button = tk.Button(self.nav_frame, text="Предыдущая", command=self.prev_line)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.mark_button = tk.Button(self.nav_frame, text="Отметить", command=self.mark_line)
        self.mark_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(self.nav_frame, text="Следующая", command=self.next_line)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Кнопка создания таблицы
        self.table_button = tk.Button(self.root, text="Создать таблицу", command=self.create_table)
        self.table_button.pack(pady=5)

        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Файл не загружен")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5, pady=5)

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if not self.file_path:
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.lines = [line.strip().split(';') for line in file.readlines() if line.strip()]

            if not self.lines:
                messagebox.showwarning("Предупреждение", "Файл пуст")
                return

            self.current_line = 0
            self.marked_lines = set()
            self.update_display()
            self.status_var.set(f"Загружен файл: {self.file_path}. Строк: {len(self.lines)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def update_display(self):
        if not self.lines:
            self.line_label.config(text="Файл не загружен")
            return

        line_data = self.lines[self.current_line]
        marked = "✓" if self.current_line in self.marked_lines else "✗"
        display_text = f"{marked} Строка {self.current_line + 1}/{len(self.lines)}: {' | '.join(line_data)}"
        self.line_label.config(text=display_text)

    def prev_line(self):
        if not self.lines:
            return

        self.current_line = max(0, self.current_line - 1)
        self.update_display()

    def next_line(self):
        if not self.lines:
            return

        self.current_line = min(len(self.lines) - 1, self.current_line + 1)
        self.update_display()

    def mark_line(self):
        if not self.lines:
            return

        if self.current_line in self.marked_lines:
            self.marked_lines.remove(self.current_line)
        else:
            self.marked_lines.add(self.current_line)

        self.update_display()

    def create_table(self):
        if not self.marked_lines:
            messagebox.showwarning("Предупреждение", "Нет отмеченных строк")
            return

        # Создаем новое окно для таблицы
        table_window = tk.Toplevel(self.root)
        table_window.title("Таблица из отмеченных строк")

        # Создаем Treeview для отображения таблицы
        columns = [f"Поле {i + 1}" for i in range(len(self.lines[0]))]
        tree = ttk.Treeview(table_window, columns=columns, show="headings")

        # Настраиваем заголовки
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.W)  # По умолчанию выравниваем влево

        # Добавляем отмеченные строки
        for line_idx in sorted(self.marked_lines):
            line_data = self.lines[line_idx]
            tree.insert("", tk.END, values=line_data)

        # Получаем шрифт по умолчанию для расчета ширины
        default_font = font.nametofont("TkDefaultFont")

        # Автоматически подбираем ширину столбцов
        for col in columns:
            # Ширина по заголовку
            header_width = default_font.measure(col) + 20
            # Ширина по данным
            col_index = int(col.split()[-1]) - 1  # Получаем индекс столбца (0-based)
            data_width = max(default_font.measure(str(self.lines[i][col_index]))
                             for i in self.marked_lines) + 20
            tree.column(col, width=max(header_width, data_width, 100))

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(table_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(expand=True, fill=tk.BOTH)

        # Кнопка сохранения таблицы
        save_button = tk.Button(
            table_window,
            text="Сохранить таблицу",
            command=lambda: self.save_table_data(tree, columns)
        )
        save_button.pack(pady=10)

    def save_table_data(self, tree, columns):
        # Запрашиваем путь для сохранения
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("CSV файлы", "*.csv"),
                ("Все файлы", "*.*")
            ],
            title="Сохранить таблицу как"
        )

        if not file_path:
            return  # Пользователь отменил сохранение

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                # # Записываем заголовки
                # headers = [tree.heading(col)['text'] for col in columns]
                # file.write("\t".join(headers) + "\n")

                # Записываем данные
                for item in tree.get_children():
                    values = tree.item(item)['values']
                    file.write("\t".join(str(v) for v in values) + "\n")

            messagebox.showinfo("Успех", f"Таблица успешно сохранена в файл:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileViewerApp(root)
    root.mainloop()